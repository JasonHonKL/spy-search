def retrieve_user(client, user_id):
    """Retrieve a user by ID."""
    try:
        response = client.users.retrieve(user_id=user_id)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)} 