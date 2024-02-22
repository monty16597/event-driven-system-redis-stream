def placed_order(message_data):
    print(f"Order placed - Order ID: {message_data['data']['order_id']}, Product: {message_data['data']['product']}")