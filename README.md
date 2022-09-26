# TriOptima  Project
`pip3 install -r requirements.txt` - to install all the requirements\
`pytest tests/` - to run the tests\
`python3 main.py` - to run the server locally

Requests:

1. Create user:
        
        curl --location --request POST 'http://127.0.0.1:5000/user' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "user_name": "Sheldon Cooper",
            "phone_number": "+46123456789",
            "email": "sheldon@cooper.com"
        }'
        
1. Send a message:
        
        curl --location --request POST 'http://127.0.0.1:5000/message' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "body": "Bazinga!",
            "author_id": 1,
            "recipient_id": 2
        }'

1. Get all the new messages that a specific user received:

        curl --location --request GET 'http://127.0.0.1:5000/new_messages?user_id=2'
        
1. Delete a message:

        curl --location --request DELETE 'http://127.0.0.1:5000/message/1'
        
1. Delete multiple messages:

        curl --location --request POST 'http://127.0.0.1:5000/delete_messages' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "message_ids": [
                2,
                3
            ]
        }'
                
1. Fetch sorted messages:

        curl --location --request GET 'http://127.0.0.1:5000/sorted_messages?start_index=2021-09-25%2018:00:51.514215&stop_index=2023-09-25%2018:00:51.514219&user_id=2'
                
