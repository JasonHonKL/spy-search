def append_block_children(client, block_id, children):
    """Append children to a block."""
    try:
        response = client.blocks.children.append(block_id=block_id, children=children)
        return {"status": "success", "data": response["results"]}
    except Exception as e:
        return {"status": "error", "message": str(e)} 