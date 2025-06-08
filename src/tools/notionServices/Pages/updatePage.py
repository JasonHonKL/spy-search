def update_page_properties(client, page_id, properties):
    """Update page properties."""
    try:
        response = client.pages.update(page_id=page_id, properties=properties)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)} 