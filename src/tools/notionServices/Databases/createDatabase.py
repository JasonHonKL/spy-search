def create_database(client, parent_page_id, title, properties):
    """Create a database in Notion."""
    try:
        response = client.databases.create(
            parent={"page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": title}}],
            properties=properties
        )
        return {"status": "success", "database_id": response["id"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}