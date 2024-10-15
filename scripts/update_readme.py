import requests
import re
import json

def get_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    return response.json()

def update_readme(repos):
    with open('README.md', 'r') as file:
        content = file.read()

    repo_data = json.dumps(repos)
    
    new_content = re.sub(
        r'(<!-- REPO_DATA_START -->).*?(<!-- REPO_DATA_END -->)',
        f'\\1\n{repo_data}\n\\2',
        content,
        flags=re.DOTALL
    )

    with open('README.md', 'w') as file:
        file.write(new_content)

if __name__ == "__main__":
    repos = get_repos("Thavanish")
    update_readme(repos)
