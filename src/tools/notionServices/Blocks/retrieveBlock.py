def retrieve_block(client, block_id):
    """Retrieve a block by ID."""
    try:
        response = client.blocks.retrieve(block_id=block_id)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def retrieve_block_children(client, block_id):
    """Retrieve children of a block."""
    try:
        response = client.blocks.children.list(block_id=block_id)
        return {"status": "success", "data": response["results"]}
    except Exception as e:
        return {"status": "error", "message": str(e)} 