from github import Github
import os
# Personal Access Token from GitHub
ACCESS_TOKEN = os.environ['GIT']

# Repository details
REPO_NAME = "Armx-123/yt-meme"  # Format: username/repo
FILE_PATH = "file.txt"  # Path in the repo
LOCAL_FILE = "file.txt"  # Local file to upload
COMMIT_MESSAGE = "Add a new text file"

# Authenticate to GitHub
g = Github(ACCESS_TOKEN)
repo = g.get_repo(REPO_NAME)

# Read the content of the local file
with open(LOCAL_FILE, "r") as file:
    content = file.read()

try:
    # Check if the file already exists in the repository
    contents = repo.get_contents(FILE_PATH)
    # Update the file if it exists
    repo.update_file(
        contents.path, COMMIT_MESSAGE, content, contents.sha
    )
    print(f"Updated {FILE_PATH} in the repository.")
except Exception as e:
    # If the file doesn't exist, create a new one
    repo.create_file(FILE_PATH, COMMIT_MESSAGE, content)
    print(f"Created {FILE_PATH} in the repository.")
