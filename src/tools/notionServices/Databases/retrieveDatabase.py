def retrieve_database(client, database_id):
    """Retrieve a database by ID."""
    try:
        response = client.databases.retrieve(database_id=database_id)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)} 