import os


def create_env_file(filepath, content):
    """Creates a .env file with the given content."""
    with open(filepath, "w") as f:
        f.write(content)


if __name__ == "__main__":
    file_path = ".env"
    env_content = """
    DEEPSEEK_API=<YOUR-DEEPSEEK-API>
    GEMINI_API=<YOU-GEMINI-API>
    XAI_API_KEY=<XAI API KEY>
    OPENAI_API_KEY=<YOUR OPENAI API KEY>
    """
    create_env_file(file_path, env_content)
    print(f".env file created at {os.path.abspath(file_path)}")
    os.mkdir("./tmp")
    os.mkdir("./tmp/screenshot")
    os.mkdir("./local_files")
