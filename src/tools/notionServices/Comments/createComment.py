def create_comment(client, parent_id, rich_text, parent_type="page_id"):
    """Create a comment on a page or discussion."""
    try:
        parent = {parent_type: parent_id}
        response = client.comments.create(parent=parent, rich_text=rich_text)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)} 