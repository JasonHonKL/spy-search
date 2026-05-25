def update_block(client, block_id, block_data):
    """Update a block's content."""
    try:
        response = client.blocks.update(block_id=block_id, **block_data)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)} 