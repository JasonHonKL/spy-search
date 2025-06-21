from .notionServices.Auth.auth import NotionAuth
from .notionServices.Auth.token_storage import TokenStorage
from .notionServices.Pages.createPage import create_page
from .notionServices.Pages.retrievePage import retrieve_page
from .notionServices.Pages.updatePage import update_page_properties
from .notionServices.Pages.archivePage import archive_page
from .notionServices.Databases.createDatabase import create_database
from .notionServices.Databases.retrieveDatabase import retrieve_database
from .notionServices.Databases.queryDatabase import query_database
from .notionServices.Databases.updateDatabase import update_database_properties
from .notionServices.Blocks.retrieveBlock import retrieve_block, retrieve_block_children
from .notionServices.Blocks.appendBlock import append_block_children
from .notionServices.Blocks.updateBlock import update_block
from .notionServices.Blocks.deleteBlock import delete_block
from .notionServices.Blocks.uploadFile import upload_file_to_block
from .notionServices.Users.listUsers import list_users
from .notionServices.Users.retrieveUser import retrieve_user
from .notionServices.Search.search import search_notion
from .notionServices.Comments.createComment import create_comment
from .notionServices.Comments.retrieveComments import retrieve_comments

class NotionController:
    def __init__(self):
        """Initialize controller without credentials."""
        self.token_storage = TokenStorage()
        self.auth = NotionAuth(self.token_storage)
        self.client = None  # Set after authentication

    def authenticate(self, user_id, auth_mode="oauth"):
        """Authenticate user with OAuth or integration token and initialize Notion client.
        
        Args:
            user_id (str): Unique identifier for the user (e.g., email).
            auth_mode (str): Authentication mode ('oauth' or 'token', default 'oauth').
        
        Returns:
            str: Access token (OAuth) or integration token (token mode).
        """
        token = self.auth.authenticate(user_id, auth_mode)
        self.client = self.auth.get_notion_client(token)
        return token

    # Page Operations
    def create_page(self, parent_id, title, content=None, parent_type="page_id"):
        """Create a new page in Notion under a specified parent.
        
        Args:
            parent_id (str): ID of the parent page or database.
            title (str): Title of the new page.
            content (list, optional): List of block objects for page content.
            parent_type (str): Type of parent ('page_id' or 'database_id', default 'page_id').
        
        Returns:
            dict: API response with the created page's details.
        """
        return create_page(self.client, parent_id, title, content, parent_type)

    def retrieve_page(self, page_id):
        """Retrieve details of a specific Notion page.
        
        Args:
            page_id (str): ID of the page to retrieve.
        
        Returns:
            dict: API response with the page's details.
        """
        return retrieve_page(self.client, page_id)

    def update_page_properties(self, page_id, properties):
        """Update properties of an existing Notion page.
        
        Args:
            page_id (str): ID of the page to update.
            properties (dict): Dictionary of properties to update (e.g., title).
        
        Returns:
            dict: API response with the updated page's details.
        """
        return update_page_properties(self.client, page_id, properties)

    def archive_page(self, page_id):
        """Archive (soft delete) a Notion page.
        
        Args:
            page_id (str): ID of the page to archive.
        
        Returns:
            dict: API response confirming the archival.
        """
        return archive_page(self.client, page_id)

    # Database Operations
    def create_database(self, parent_page_id, title, properties):
        """Create a new Notion database under a parent page.
        
        Args:
            parent_page_id (str): ID of the parent page.
            title (str): Title of the new database.
            properties (dict): Dictionary defining database properties (e.g., columns).
        
        Returns:
            dict: API response with the created database's details.
        """
        return create_database(self.client, parent_page_id, title, properties)

    def retrieve_database(self, database_id):
        """Retrieve details of a specific Notion database.
        
        Args:
            database_id (str): ID of the database to retrieve.
        
        Returns:
            dict: API response with the database's details.
        """
        return retrieve_database(self.client, database_id)

    def query_database(self, database_id, filter=None, sorts=None):
        """Query a Notion database with optional filters and sorts.
        
        Args:
            database_id (str): ID of the database to query.
            filter (dict, optional): Filter conditions for the query.
            sorts (list, optional): Sort criteria for the query results.
        
        Returns:
            dict: API response with the query results.
        """
        return query_database(self.client, database_id, filter, sorts)

    def update_database_properties(self, database_id, properties):
        """Update properties of an existing Notion database.
        
        Args:
            database_id (str): ID of the database to update.
            properties (dict): Dictionary of properties to update (e.g., title).
        
        Returns:
            dict: API response with the updated database's details.
        """
        return update_database_properties(self.client, database_id, properties)

    # Block Operations
    def retrieve_block(self, block_id):
        """Retrieve details of a specific Notion block.
        
        Args:
            block_id (str): ID of the block to retrieve.
        
        Returns:
            dict: API response with the block's details.
        """
        return retrieve_block(self.client, block_id)

    def retrieve_block_children(self, block_id):
        """Retrieve child blocks of a specific Notion block.
        
        Args:
            block_id (str): ID of the parent block.
        
        Returns:
            dict: API response with the child blocks' details.
        """
        return retrieve_block_children(self.client, block_id)

    def append_child_blocks(self, block_id, children):
        """Append child blocks to a Notion block.
        
        Args:
            block_id (str): ID of the parent block.
            children (list): List of block objects to append.
        
        Returns:
            dict: API response with the appended blocks' details.
        """
        return append_block_children(self.client, block_id, children)

    def update_block(self, block_id, block_data):
        """Update content of a specific Notion block.
        
        Args:
            block_id (str): ID of the block to update.
            block_data (dict): Updated block content (e.g., text).
        
        Returns:
            dict: API response with the updated block's details.
        """
        return update_block(self.client, block_id, block_data)

    def delete_block(self, block_id):
        """Delete a specific Notion block.
        
        Args:
            block_id (str): ID of the block to delete.
        
        Returns:
            dict: API response confirming the deletion.
        """
        return delete_block(self.client, block_id)

    def upload_file_to_block(self, block_id, file_url, file_type="file"):
        """Upload a file to a Notion block.
        
        Args:
            block_id (str): ID of the parent block.
            file_url (str): URL of the file to upload.
            file_type (str): Type of file ('file' or 'image', default 'file').
        
        Returns:
            dict: API response with the uploaded file's details.
        """
        return upload_file_to_block(self.client, block_id, file_url, file_type)

    # User Operations
    def list_users(self):
        """List all users in the Notion workspace.
        
        Returns:
            dict: API response with the list of users.
        """
        return list_users(self.client)

    def retrieve_user(self, user_id):
        """Retrieve details of a specific Notion user.
        
        Args:
            user_id (str): ID of the user to retrieve.
        
        Returns:
            dict: API response with the user's details.
        """
        return retrieve_user(self.client, user_id)

    # Search Operations
    def search(self, query, filter=None):
        """Search Notion workspace for pages or databases.
        
        Args:
            query (str): Search query string.
            filter (dict, optional): Filter for search results (e.g., object type).
        
        Returns:
            dict: API response with the search results.
        """
        return search_notion(self.client, query, filter)

    # Comment Operations
    def create_comment(self, parent_id, rich_text, parent_type="page_id"):
        """Create a comment on a Notion page or block.
        
        Args:
            parent_id (str): ID of the page or block to comment on.
            rich_text (list): List of rich text objects for the comment.
            parent_type (str): Type of parent ('page_id' or 'block_id', default 'page_id').
        
        Returns:
            dict: API response with the created comment's details.
        """
        return create_comment(self.client, parent_id, rich_text, parent_type)

    def retrieve_comments(self, page_id):
        """Retrieve comments on a specific Notion page.
        
        Args:
            page_id (str): ID of the page to retrieve comments for.
        
        Returns:
            dict: API response with the list of comments.
        """
        return retrieve_comments(self.client, page_id)