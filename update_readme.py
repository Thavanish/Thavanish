import requests
import json

def fetch_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repositories: {response.status_code}")
        return []

def generate_repo_menu(repos):
    menu_items = []
    for repo in repos:
        menu_items.append(f'<li><a href="{repo["html_url"]}">{repo["name"]}</a></li>')
    return "\n".join(menu_items)

def update_readme(username):
    repos = fetch_repos(username)
    repo_menu = generate_repo_menu(repos)
    
    with open('README.md', 'r') as file:
        content = file.read()
    
    start_marker = "<!-- REPO_MENU_START -->"
    end_marker = "<!-- REPO_MENU_END -->"
    
    start_index = content.find(start_marker)
    end_index = content.find(end_marker)
    
    if start_index != -1 and end_index != -1:
        new_content = (
            content[:start_index + len(start_marker)] +
            "\n" + repo_menu + "\n" +
            content[end_index:]
        )
        
        with open('README.md', 'w') as file:
            file.write(new_content)
        print("README.md updated successfully!")
    else:
        print("Markers not found in README.md. Please add the markers.")

if __name__ == "__main__":
    username = "Thavanish"
    update_readme(username)
