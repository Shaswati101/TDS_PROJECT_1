import os
from github import Github, Auth, GithubException
from github.Repository import Repository
import requests
from github import InputGitTreeElement
import base64

def commit_multiple_files(repo, files: dict, commit_message: str):
    try:
        main_ref = repo.get_git_ref("heads/main")
        latest_commit = repo.get_git_commit(main_ref.object.sha)
        base_tree = repo.get_git_tree(latest_commit.tree.sha)
        elements = []
        for path, content in files.items():
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            blob = repo.create_git_blob(encoded, "base64")
            element = InputGitTreeElement(
                path=path,
                mode="100644",
                type="blob",
                sha=blob.sha
            )
            elements.append(element)

        new_tree = repo.create_git_tree(elements, base_tree)
        new_commit = repo.create_git_commit(commit_message, new_tree, [latest_commit])
        main_ref.edit(new_commit.sha)

        print(f" Successfully committed {len(files)} files: {new_commit.sha}")
        return new_commit.sha

    except Exception as e:
        print(f" Error committing multiple files: {str(e)}")
        raise


def get_github_client() -> Github:
    github_pat = os.getenv("GITHUB_PAT")
    if not github_pat:
        raise ValueError("GITHUB_PAT environment variable not set.")
    auth = Auth.Token(github_pat)
    return Github(auth=auth)


def create_student_repo(g: Github, repo_name: str) -> Repository:
    try:
        user = g.get_user()
        repo = user.create_repo(
            name=repo_name,
            private=False,
            auto_init=True,
            description="AI-generated project.",
            license_template="mit"
        )
        print(f"Successfully created repository: {repo.full_name}")
        return repo
    except GithubException as e:
        print(f"Error creating repository: {e}")
        if e.status == 422:
            raise ValueError(f"Repository '{repo_name}' likely already exists.")
        raise


def add_file_to_repo(repo: Repository, file_path: str, file_content: str, commit_message: str):
    try:
        repo.create_file(
            path=file_path,
            message=commit_message,
            content=file_content
        )
        print(f"Successfully committed '{file_path}' to {repo.full_name}")
    except GithubException as e:
        print(f"Error committing file: {e}")
        raise

def update_file_to_repo(repo: Repository, file_path: str, file_content: str, commit_message: str):
    try:
        file = repo.get_contents(file_path, ref="main")
        print(file.sha)
        repo.update_file(
            path=file_path,
            message=commit_message,
            content=file_content,
            sha=file.sha
        )
        print(f"Successfully committed '{file_path}' to {repo.full_name}")
    except GithubException as e:
        print(f"Error committing file: {e}")
        raise


def get_existing_repo(g, repo_name: str):
    return g.get_user().get_repo(repo_name)


def enable_github_pages(repo):
    try:
        api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/pages"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {os.getenv("GITHUB_PAT")}"
        }
        payload = {
            "source": {
                "branch": "main",
                "path": "/"
            }
        }
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code not in (201, 204):
            raise Exception(f"GitHub Pages enable failed: {response.text}")
        print(f"GitHub Pages enabled for {repo.full_name}")
    except Exception as e:
        raise Exception(f"Failed to enable GitHub Pages: {str(e)}")


def get_file_content(repo, path: str) -> str:
    try:
        contents = repo.get_contents(path)
        return contents.decoded_content.decode("utf-8")
    except Exception as e:
        raise Exception(f"Failed to fetch content for '{path}': {str(e)}")
