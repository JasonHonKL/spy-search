def upload_file_to_block(client, block_id, file_url, file_type="file"):
    """Upload a file to a block."""
    try:
        response = client.blocks.children.append(
            block_id=block_id,
            children=[{"type": file_type, file_type: {"external": {"url": file_url}}}]
        )
        return {"status": "success", "data": response["results"]}
    except Exception as e:
        return {"status": "error", "message": str(e)} 