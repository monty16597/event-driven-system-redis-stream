from flask import Flask, request, jsonify
import redis
import json
import os

app = Flask(__name__)

STREAM_NAME = os.environ.get('REDIS_STREAM_NAME', 'my_stream')
GROUP_NAME = os.environ.get('REDIS_CONSUMER_GROUP_NAME', 'my_group')
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)

# Check if the stream exists using XINFO command
try:
    stream_info = redis_client.execute_command('XINFO', 'STREAM', STREAM_NAME)
except redis.exceptions.RedisError as e:
    print(f"Stream not found: {e}")
    # If the stream doesn't exist, create it with an initial message
    initial_message = event = {"event_type": "stream_init","data": json.dumps({})}
    redis_client.xadd(STREAM_NAME, initial_message)

# Create a consumer group for the stream
# This is typically done once per consumer group
# Use the XINFO GROUPS command to get information about consumer groups for the specified stream
try:
    # Manually send the XINFO GROUPS command
    response = redis_client.execute_command('XINFO', 'GROUPS', STREAM_NAME)

    try:
        if not response:
            raise Exception("Stream has not been intialised yet")
        # Parse the response to check if the consumer group exists
        info = dict(zip(response[0][::2], response[0][1::2]))
        if info[b'name'].decode() != GROUP_NAME:
            print(f"The consumer group {GROUP_NAME} does not exist for the stream {STREAM_NAME}")
            raise Exception("Consumer group has not been found")
    except Exception as e:
        print(f'{e}. Creating group...')
        redis_client.xgroup_create(STREAM_NAME, GROUP_NAME, id='0', mkstream=True)
except redis.exceptions.RedisError as e:
    print(f"Redis Error: {e}")


# Route to receive POST requests and create events
@app.route('/create-event', methods=['POST'])
def create_event():
    try:
        # Get data from the POST request
        event_type = dict(request.get_json())['event_type']
        data = dict(request.get_json())['data']
        # Create the event object
        event = {
            "event_type": event_type,
            "data": json.dumps(data)
        }

        # Publish the event to a Redis Stream named 'events_stream'
        redis_client.xadd(STREAM_NAME, event)

        message = None
        if event_type == 'order_placed':
            message = f"Order placed - Order ID: {data['order_id']}, Product: {data['product']}"

        elif event_type == 'user_registered':
            message = f"User registered - User ID: {data['user_id']}, Name: {data['name']}"
        else:
            message = "Unknown event type"

        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
