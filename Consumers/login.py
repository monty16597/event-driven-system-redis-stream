def user_registered(message_data):
    print(f"User registered - User ID: {message_data['data']['user_id']}, Name: {message_data['data']['name']}")
