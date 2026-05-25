def retrieve_comments(client, page_id):
    """Retrieve comments for a page."""
    try:
        response = client.comments.list(page_id=page_id)
        return {"status": "success", "data": response["results"]}
    except Exception as e:
        return {"status": "error", "message": str(e)} 