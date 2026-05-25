def create_page(client, parent_id, title, content=None, parent_type="page_id"):
    """Create a page in Notion."""
    try:
        parent = {parent_type: parent_id}
        properties = {"title": {"title": [{"type": "text", "text": {"content": title}}]}}
        payload = {"parent": parent, "properties": properties}
        if content:
            payload["children"] = content
        response = client.pages.create(**payload)
        return {"status": "success", "page_id": response["id"]}
    except Exception as e:
        return {"status": "error", "message": str(e)} 