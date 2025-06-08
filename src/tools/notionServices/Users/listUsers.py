def list_users(client):
    """List all users in the workspace."""
    try:
        response = client.users.list()
        return {"status": "success", "data": response["results"]}
    except Exception as e:
        return {"status": "error", "message": str(e)} 