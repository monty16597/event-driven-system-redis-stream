import redis
import json
import os
from order import  placed_order
from login import  user_registered


# Consumer group name and consumer name
STREAM_NAME = os.environ.get('REDIS_STREAM_NAME', 'events_stream')
GROUP_NAME = os.environ.get('REDIS_CONSUMER_GROUP_NAME', 'my_group')
CONSUMER_NAME = os.environ.get('REDIS_CONSUMER_NAME', 'consumer1')  # Change this for each consumer
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)


# Function to process messages
def process_messages():
    print(f"================= CONSUMER {CONSUMER_NAME} STARTED =================")
    while True:
        try:
            # Read messages from the stream using XREADGROUP
            messages = redis_client.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_NAME: '>'}, block=0)
            # Process the messages
            for stream, message_list in messages:
                for message in message_list:
                    print(f"========== Processing message in {CONSUMER_NAME} consumer ==========")
                    message_id = message[0]
                    message_data = message[1]

                    # Convert bytes to str for the data dictionary
                    message_data = {key.decode('utf-8'): value.decode('utf-8') if isinstance(value, bytes) else value
                                    for key, value in message_data.items()}

                    print(f"Received message with ID: {message_id}, Data: {message_data}", type(message_data))

                    # Add your message processing logic here
                    # Process the event based on its type
                    message_data['data'] = json.loads(message_data['data'])
                    if message_data['event_type'] == 'order_placed':
                        placed_order(message_data)
                    elif message_data['event_type'] == 'user_registered':
                        user_registered(message_data)
                    elif message_data['event_type'] == 'stream_init':
                        print('Stream Initialized!!')
                    else:
                        print("Unknown event type")
                    # Acknowledge the message to mark it as processed
                    redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)
                    print(f"========== Processed message successfully ==========")

        except Exception as e:
            print(f"Error: {e}")
            print(f"========== Couldn't process message ==========")


if __name__ == '__main__':
    process_messages()
