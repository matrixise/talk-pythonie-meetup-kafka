from common.records import MessageRecord
from faust_consumer import app

message_topic = app.topic("messages", value_type=MessageRecord)
email_topic = app.topic("emails", value_type=MessageRecord)
