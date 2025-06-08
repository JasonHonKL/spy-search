def retrieve_page(client, page_id):
    """Retrieve a page by ID."""
    try:
        response = client.pages.retrieve(page_id=page_id)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)} 