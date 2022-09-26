from datetime import datetime

import sqlalchemy
from flask import Flask, make_response
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy

from validators import message_parser, new_message_parser, delete_messages_parser, fetch_sorted_message_parser, \
    user_parser

app = Flask(__name__)

if __name__ == "__main__":
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/trioptima.db"

api = Api(app)
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    phone_number = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(80), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column(db.DateTime(), default=lambda: datetime.utcnow())
    is_fetched = db.Column(db.Boolean(), default=False)


@app.post('/message')
def send_message():
    # Submit a message to a defined recipient, identified with some identifier,
    # e.g. email-address, phone-number, user name or similar.
    args = message_parser.parse_args()

    try:
        author = db.session.query(User).filter(
            User.id == args["author_id"]
        ).one()
    except sqlalchemy.exc.NoResultFound:
        abort(make_response({"description": "The user doesn't exist"}, 400))

    try:
        recipient = db.session.query(User).filter(
            User.id == args["recipient_id"]
        ).one()
    except sqlalchemy.exc.NoResultFound:
        abort(make_response({"description": "The recipient doesn't exist"}, 400))

    new_message = Message(
        body=args["body"],
        author_id=author.id,
        recipient_id=recipient.id,
    )
    db.session.add(new_message)
    db.session.commit()
    return {"message_id": new_message.id}


@app.get('/new_messages')
def fetch_new_messages():
    # Fetch new messages (meaning the service must know what has already been fetched).

    args = new_message_parser.parse_args()
    try:
        user = db.session.query(User).filter(
            User.id == args["user_id"]
        ).one()
    except sqlalchemy.exc.NoResultFound:
        abort(make_response({"description": "The user doesn't exist"}, 400))

    messages = db.session.query(Message).filter(
        Message.recipient_id == user.id,
        Message.is_fetched == False
    ).all()
    for message in messages:
        message.is_fetched = True
    db.session.commit()

    return [
        {"author_id": message.author_id, "body": message.body} for message in messages
    ]


@app.delete('/message/<int:message_id>')
def delete_message(message_id):
    # Delete a single message.

    try:
        message = db.session.query(Message).filter(
            Message.id == message_id
        ).one()
    except sqlalchemy.exc.NoResultFound:
        abort(make_response({"description": "The message does not exist"}, 400))

    db.session.delete(message)
    db.session.commit()

    return {"status": "OK"}


@app.post('/delete_messages')
def delete_messages():
    # Delete multiple messages.
    args = delete_messages_parser.parse_args()
    messages = db.session.query(Message).filter(
        Message.id.in_(args["message_ids"])
    ).all()
    if not messages:
        abort(make_response({"description": "None of the messages exist"}, 400))

    for message in messages:
        db.session.delete(message)
    db.session.commit()

    return {"status": "OK"}


@app.get('/sorted_messages')
def fetch_sorted_messages():
    # Fetch messages (including previously fetched) ordered by time, according
    # to start and stop index.
    args = fetch_sorted_message_parser.parse_args()
    messages = db.session.query(Message).filter(
        Message.recipient_id == args["user_id"],
        args["start_index"] <= Message.created_on,
        Message.created_on <= args["stop_index"]
    ).order_by(Message.created_on).all()
    db.session.commit()

    return [
        {"author_id": message.author_id, "body": message.body, "created_on": message.created_on} for message in messages
    ]


class UserResourse(Resource):

    def post(self):
        args = user_parser.parse_args()
        new_user = User(
            user_name=args["user_name"],
            phone_number=args["phone_number"],
            email=args["email"],
        )
        db.session.add(new_user)
        db.session.commit()
        return {"id": new_user.id}


api.add_resource(UserResourse, '/user')

if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
