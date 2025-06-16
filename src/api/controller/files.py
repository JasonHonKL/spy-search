from ...utils import read_config, write_config
from fastapi import UploadFile

"""
    This files should handle 
"""


def select_folder_handler(folder_name: str):
    folder_path = f"./local_files/{folder_name}"

    config = read_config()
    config["db"] = folder_path

    write_config(config)
    return folder_path


def delete_folder_handler():
    pass


def get_folder_handler():
    pass


def upload_file_handler():
    pass


def delete_file_handler():
    pass


def download_file_handler():
    pass


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    pass
