from tools.notion_controller import NotionController

def main():
    # Get user inputs
    user_id = input("Enter your user ID (e.g., email or username): ").strip()
    print("Choose authentication mode: 'token' (single workspace, no browser login) or 'oauth' (personal workspace)")
    auth_mode = input("Enter mode (token/oauth, default: token): ").strip().lower() or "token"
    if auth_mode not in ["token", "oauth"]:
        print("Invalid auth mode. Use 'token' or 'oauth'.")
        return

    # Initialize controller
    controller = NotionController()

    # Authenticate
    try:
        token = controller.authenticate(user_id, auth_mode)
        print(f"Authenticated successfully with {'access token' if auth_mode == 'oauth' else 'integration token'}: {token[:10]}...")
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        return

    # Get IDs for testing
    database_id = input("Enter your Notion database ID for tasks: ").strip()
    parent_page_id = input("Enter your parent page ID for tests: ").strip()
    page_id = input("Enter a page ID for tests: ").strip()
    block_id = input("Enter a block ID for tests: ").strip()
    user_id_notion = input("Enter a Notion user ID for tests: ").strip()

    # Test Page Operations
    print("\nTesting Page Operations:")
    try:
        print("Creating page...")
        print(controller.create_page(parent_page_id, "Test Page", content=[{"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Hello, Notion!"}}]}}], parent_type="page_id"))
        print("Retrieving page...")
        print(controller.retrieve_page(page_id))
        print("Updating page properties...")
        print(controller.update_page_properties(page_id, {"title": [{"type": "text", "text": {"content": "Updated Title"}}]}))
        print("Archiving page...")
        print(controller.archive_page(page_id))
    except Exception as e:
        print(f"Page operations failed: {str(e)}")

    # Test Database Operations
    print("\nTesting Database Operations:")
    try:
        db_properties = {
            "Name": {"title": {}},
            "Status": {"select": {"options": [{"name": "To Do"}, {"name": "Done"}]}}
        }
        print("Creating database...")
        print(controller.create_database(parent_page_id, "Test Database", db_properties))
        print("Retrieving database...")
        print(controller.retrieve_database(database_id))
        print("Querying database...")
        print(controller.query_database(database_id, filter={"property": "Status", "select": {"equals": "To Do"}}))
        print("Updating database properties...")
        print(controller.update_database_properties(database_id, {"title": [{"type": "text", "text": {"content": "Updated DB"}}]}))
    except Exception as e:
        print(f"Database operations failed: {str(e)}")

    # Test Block Operations
    print("\nTesting Block Operations:")
    try:
        print("Retrieving block...")
        print(controller.retrieve_block(block_id))
        print("Retrieving block children...")
        print(controller.retrieve_block_children(block_id))
        print("Appending block children...")
        print(controller.append_child_blocks(block_id, [{"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "New Block"}}]}}]))
        print("Updating block...")
        print(controller.update_block(block_id, {"paragraph": {"rich_text": [{"type": "text", "text": {"content": "Updated Block"}}]}}))
        print("Deleting block...")
        print(controller.delete_block(block_id))
        print("Uploading file to block...")
        print(controller.upload_file_to_block(block_id, "https://example.com/sample.pdf", "file"))
    except Exception as e:
        print(f"Block operations failed: {str(e)}")

    # Test User Operations
    print("\nTesting User Operations:")
    try:
        print("Listing users...")
        print(controller.list_users())
        print("Retrieving user...")
        print(controller.retrieve_user(user_id_notion))
    except Exception as e:
        print(f"User operations failed: {str(e)}")

    # Test Search
    print("\nTesting Search:")
    try:
        print("Searching for 'Test Page'...")
        print(controller.search("Test Page"))
    except Exception as e:
        print(f"Search operation failed: {str(e)}")

    # Test Comments
    print("\nTesting Comment Operations:")
    try:
        print("Creating comment...")
        print(controller.create_comment(page_id, [{"type": "text", "text": {"content": "Test comment"}}], parent_type="page_id"))
        print("Retrieving comments...")
        print(controller.retrieve_comments(page_id))
    except Exception as e:
        print(f"Comment operations failed: {str(e)}")

if __name__ == "__main__":
    main()