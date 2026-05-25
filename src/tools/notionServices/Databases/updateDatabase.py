def update_database_properties(client, database_id, properties):
    """Update database properties."""
    try:
        response = client.databases.update(database_id=database_id, properties=properties)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)} 