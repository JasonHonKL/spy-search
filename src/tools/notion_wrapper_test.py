import os
from .notion_controller import NotionController
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    client_id = os.getenv("NOTION_CLIENT_ID")
    client_secret = os.getenv("NOTION_CLIENT_SECRET")
    redirect_uri = os.getenv("NOTION_REDIRECT_URI")

    # Initialize controller
    controller = NotionController(client_id, client_secret, redirect_uri)

    # Simulate OAuth flow (in practice, get code from redirect)
    auth_url = controller.auth.get_auth_url()
    print(f"Please visit to authorize: {auth_url}")
    code = input("Enter the code from redirect: ")  # Manual input for testing
    access_token = controller.authenticate(code)

    # Test Page Operations
    parent_page_id = "your-parent-page-id"  # Replace with actual ID
    print(controller.create_page(parent_page_id, "Test Page", content=[{"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Hello, Notion!"}}]}}]))
    page_id = "your-page-id"  # Replace with actual ID
    print(controller.retrieve_page(page_id))
    print(controller.update_page_properties(page_id, {"title": [{"type": "text", "text": {"content": "Updated Title"}}]}))
    print(controller.archive_page(page_id))

    # Test Database Operations
    db_properties = {
        "Name": {"title": {}},
        "Status": {"select": {"options": [{"name": "To Do"}, {"name": "Done"}]}}
    }
    print(controller.create_database(parent_page_id, "Test Database", db_properties))
    database_id = "your-database-id"  # Replace with actual ID
    print(controller.retrieve_database(database_id))
    print(controller.query_database(database_id, filter={"property": "Status", "select": {"equals": "To Do"}}))
    print(controller.update_database_properties(database_id, {"title": [{"type": "text", "text": {"content": "Updated DB"}}]}))

    # Test Block Operations
    block_id = "your-block-id"  # Replace with actual ID
    print(controller.retrieve_block(block_id))
    print(controller.retrieve_block_children(block_id))
    print(controller.append_child_blocks(block_id, [{"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "New Block"}}]}}]))
    print(controller.update_block(block_id, {"paragraph": {"rich_text": [{"type": "text", "text": {"content": "Updated Block"}}]}}))
    print(controller.delete_block(block_id))
    print(controller.upload_file_to_block(block_id, "https://example.com/sample.pdf", "file"))

    # Test User Operations
    print(controller.list_users())
    user_id = "your-user-id"  # Replace with actual ID
    print(controller.retrieve_user(user_id))

    # Test Search
    print(controller.search("Test Page"))

    # Test Comments
    print(controller.create_comment(page_id, [{"type": "text", "text": {"content": "Test comment"}}]))
    print(controller.retrieve_comments(page_id))

if __name__ == "__main__":
    main() 