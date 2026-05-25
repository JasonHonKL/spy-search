def delete_block(client, block_id):
    """Delete a block."""
    try:
        response = client.blocks.delete(block_id=block_id)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)} 