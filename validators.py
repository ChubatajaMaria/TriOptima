from flask_restful import reqparse


message_parser = reqparse.RequestParser()
message_parser.add_argument("body", type=str, required=True)
message_parser.add_argument("author_id", type=int, required=True)
message_parser.add_argument("recipient_id", type=int, required=True)


new_message_parser = reqparse.RequestParser()
new_message_parser.add_argument("user_id", type=int, required=True, location="args")


delete_messages_parser = reqparse.RequestParser()
delete_messages_parser.add_argument("message_ids", type=list, required=True, location="json")


fetch_sorted_message_parser = reqparse.RequestParser()
fetch_sorted_message_parser.add_argument("start_index", type=str, required=True, location="args")
fetch_sorted_message_parser.add_argument("stop_index", type=str, required=True, location="args")
fetch_sorted_message_parser.add_argument("user_id", type=int, required=True, location="args")


user_parser = reqparse.RequestParser()
user_parser.add_argument("user_name", type=str, required=True)
user_parser.add_argument("phone_number", type=str, required=True)
user_parser.add_argument("email", type=str, required=True)
