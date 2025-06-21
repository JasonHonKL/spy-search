def archive_page(client, page_id):
    """Archive (soft delete) a page."""
    try:
        response = client.pages.update(page_id=page_id, archived=True)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)} 