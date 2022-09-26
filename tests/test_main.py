from freezegun import freeze_time

import main

from datetime import datetime


class TestClass:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        main.app.config['TESTING'] = True
        main.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test_trioptima.db"
        client = main.app.test_client()
        if not main.app.extensions.get('sqlalchemy'):
            main.db.init_app(main.app)
        with main.app.app_context():
            main.db.create_all()

            user_1 = main.User(
                user_name="Sheldon Cooper",
                phone_number="+46123456789",
                email="sheldon@cooper.org",
            )

            user_2 = main.User(
                user_name="Leonard Hofstadter",
                phone_number="+46123456780",
                email="leonard@hofstadter.org",
            )

            main.db.session.add(user_1)
            main.db.session.add(user_2)
            main.db.session.commit()
        self.db = main.db
        self.client = client

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        with main.app.app_context():
            self.db.drop_all()

    def test_send_message(self):
        """Testing message sending."""

        response = self.client.post('/message', json={
            "body": "Hello",
            "author_id": 1,
            "recipient_id": 2,
        })
        assert response.status_code == 200
        assert response.json["message_id"]

        # the message can't be send to non-existent user
        response = self.client.post('/message', json={
            "body": "Hello",
            "author_id": 1,
            "recipient_id": 1000,
        })
        assert response.status_code == 400
        assert response.json["description"] == "The recipient doesn't exist"

        # the message can't be send from non-existent user
        response = self.client.post('/message', json={
            "body": "Bye!",
            "author_id": 1000,
            "recipient_id": 2,
        })
        assert response.status_code == 400
        assert response.json["description"] == "The user doesn't exist"

    def test_fetch_new_messages(self):
        """Testing message fetching."""

        self.client.post('/message', json={
            "body": "Hello",
            "author_id": 2,
            "recipient_id": 1,
        })

        response = self.client.get('/new_messages', query_string={
            "user_id": 1,
        })
        assert response.status_code == 200
        assert len(response.json) == 1

        # the message has already been fetched
        response = self.client.get('/new_messages', query_string={
            "user_id": 1,
        })
        assert response.status_code == 200
        assert len(response.json) == 0

        response = self.client.get('/new_messages', query_string={
            "user_id": 1000,
        })
        assert response.status_code == 400
        assert response.json["description"] == "The user doesn't exist"

    def test_delete_message(self):
        """Testing single message deleting."""

        response = self.client.post('/message', json={
            "body": "Hello",
            "author_id": 1,
            "recipient_id": 2,
        })
        message_id = response.json["message_id"]

        response = self.client.delete('/message/{}'.format(message_id))
        assert response.status_code == 200

        response = self.client.delete('/message/{}'.format(message_id))
        assert response.status_code == 400
        assert response.json["description"] == "The message does not exist"

    def test_multiple_delete_messages(self):
        """Testing multiple message deleting."""

        message_ids = []

        response = self.client.post('/message', json={
            "body": "Knock-knock-knock!",
            "author_id": 1,
            "recipient_id": 2,
        })
        message_ids.append(response.json["message_id"])

        response = self.client.post('/message', json={
            "body": "Leonard!",
            "author_id": 1,
            "recipient_id": 2,
        })
        message_ids.append(response.json["message_id"])

        response = self.client.post('/delete_messages', json={
            "message_ids": message_ids,
        })
        assert response.status_code == 200

        response = self.client.post('/delete_messages', json={
            "message_ids": message_ids,
        })
        assert response.status_code == 400

    def test_fetch_sorted_messages(self):
        """Testing fetching sorted messages."""

        with freeze_time("2022-09-26 12:00:01"):
            self.client.post('/message', json={
                "body": "Knock-knock-knock!",
                "author_id": 1,
                "recipient_id": 2,
            })

        with freeze_time("2022-09-26 12:30:01"):
            self.client.post('/message', json={
                "body": "Leonard!",
                "author_id": 1,
                "recipient_id": 2,
            })

        response = self.client.get('/sorted_messages', query_string={
            "user_id": 2,
            "start_index": "2022-09-26 12:00:01",
            "stop_index": "2022-09-26 12:01:01",
        })
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["body"] == "Knock-knock-knock!"
