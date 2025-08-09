import os
from youtrack_lap import Connection

YOUTRACK_URL = "https://r3recube.myjetbrains.com/youtrack/"


def read_token_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Token file not found: {file_path}")
        exit(1)
        return None

# Initialize token and client
token_file = os.path.expanduser("secrets/yt_token.txt")
YOUTRACK_TOKEN = read_token_from_file(token_file)
yt_client = Connection(base_url=YOUTRACK_URL, token=YOUTRACK_TOKEN)
