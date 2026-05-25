def query_database(client, database_id, filter=None, sorts=None):
    """Query a database with optional filters and sorts."""
    try:
        response = client.databases.query(database_id=database_id, filter=filter, sorts=sorts)
        return {"status": "success", "data": response["results"]}
    except Exception as e:
        return {"status": "error", "message": str(e)} 