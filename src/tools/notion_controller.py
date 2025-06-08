from .notionServices.Auth.auth import NotionAuth
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
    def __init__(self, client_id, client_secret, redirect_uri):
        """Initialize controller with OAuth credentials."""
        self.auth = NotionAuth(client_id, client_secret, redirect_uri)
        self.client = None  # Set after authentication

    def authenticate(self, code=None):
        """Authenticate and set up Notion client."""
        access_token = self.auth.get_access_token(code)
        self.client = self.auth.get_notion_client(access_token)
        return access_token

    # Page Operations
    def create_page(self, parent_id, title, content=None, parent_type="page_id"):
        return create_page(self.client, parent_id, title, content, parent_type)

    def retrieve_page(self, page_id):
        return retrieve_page(self.client, page_id)

    def update_page_properties(self, page_id, properties):
        return update_page_properties(self.client, page_id, properties)

    def archive_page(self, page_id):
        return archive_page(self.client, page_id)

    # Database Operations
    def create_database(self, parent_page_id, title, properties):
        return create_database(self.client, parent_page_id, title, properties)

    def retrieve_database(self, database_id):
        return retrieve_database(self.client, database_id)

    def query_database(self, database_id, filter=None, sorts=None):
        return query_database(self.client, database_id, filter, sorts)

    def update_database_properties(self, database_id, properties):
        return update_database_properties(self.client, database_id, properties)

    # Block Operations
    def retrieve_block(self, block_id):
        return retrieve_block(self.client, block_id)

    def retrieve_block_children(self, block_id):
        return retrieve_block_children(self.client, block_id)

    def append_child_blocks(self, block_id, children):
        return append_block_children(self.client, block_id, children)

    def update_block(self, block_id, block_data):
        return update_block(self.client, block_id, block_data)

    def delete_block(self, block_id):
        return delete_block(self.client, block_id)

    def upload_file_to_block(self, block_id, file_url, file_type="file"):
        return upload_file_to_block(self.client, block_id, file_url, file_type)

    # User Operations
    def list_users(self):
        return list_users(self.client)

    def retrieve_user(self, user_id):
        return retrieve_user(self.client, user_id)

    # Search Operations
    def search(self, query, filter=None):
        return search_notion(self.client, query, filter)

    # Comment Operations
    def create_comment(self, parent_id, rich_text, parent_type="page_id"):
        return create_comment(self.client, parent_id, rich_text, parent_type)

    def retrieve_comments(self, page_id):
        return retrieve_comments(self.client, page_id) 