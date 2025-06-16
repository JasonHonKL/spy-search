import os
import json


def create_env_file(path, content):
    with open(path, "w") as f:
        f.write(content.strip() + "\n")


def create_json_file(path, content):
    with open(path, "w") as f:
        json.dump(content, f)


if __name__ == "__main__":
    file_path = ".env"
    env_content = """\
DEEPSEEK_API=<YOUR-DEEPSEEK-API>
GEMINI_API=<YOU-GEMINI-API>
XAI_API_KEY=<XAI API KEY>
OPENAI_API_KEY=<YOUR OPENAI API KEY>
"""
    create_env_file(file_path, env_content)
    print(f".env file created at {os.path.abspath(file_path)}")

    os.makedirs("./tmp/screenshot", exist_ok=True)
    os.makedirs("./local_files", exist_ok=True)

    messages_file = "messages.json"
    create_json_file(messages_file, [])
    print(f"{messages_file} created with empty list content")
