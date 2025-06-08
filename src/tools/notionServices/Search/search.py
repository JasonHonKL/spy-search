def search_notion(client, query, filter=None):
    """Search pages and databases."""
    try:
        response = client.search(query=query, filter=filter)
        return {"status": "success", "data": response["results"]}
    except Exception as e:
        return {"status": "error", "message": str(e)} 