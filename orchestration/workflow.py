from typing import Dict
from services import github_service, gemini_service
import time
import requests

def create_project_workflow(task_id: str, task_store: Dict, repo_name: str, code_prompt: str, attachments: list, checks: list, eval_url: str, eval_body:Dict):
    try:
        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Initializing services"}
        gemini_service.configure_gemini()
        g = github_service.get_github_client()
        task_store[task_id] = {"status": "IN_PROGRESS", "details": f"Creating repository '{repo_name}'"}
        repo = github_service.create_student_repo(g, repo_name)
        repo_url = repo.html_url
        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Generating code with AI"}
        generated_code = gemini_service.generate_html_code(code_prompt, attachments, checks)
        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Generating README.md with AI"}
        readme = gemini_service.generate_read_me(code_prompt, generated_code)
        if not generated_code:
            raise ValueError("AI model returned empty code")
        if not readme:
            raise ValueError("AI model returned empty readme")

        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Committing generated code..."}


        # github_service.add_file_to_repo(repo,"index.html", generated_code,"Initial commit of AI-generated code" )
        # github_service.update_file_to_repo(repo, "README.md", readme," Initial commit of AI-generated README.md")

        commit_sha = github_service.commit_multiple_files(
            repo,
            {
                "index.html": generated_code,
                "README.md": readme
            },
            "Initial commit of AI-generated code and README"
        )

        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Enabling GitHub Pages hosting"}
        github_service.enable_github_pages(repo)

        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Posting to evaluation url"}
        pages_url = f"https://{repo.owner.login}.github.io/{repo.name}/"
        eval_body["commit_sha"] = commit_sha
        eval_body["repo_url"] = repo_url
        eval_body["pages_url"] = pages_url
        response = submit_evaluation(eval_url, eval_body)
        print(f"Eval success: {response}")

        task_store[task_id] = {
            "status": "SUCCESS",
            "details": "Project created, hosted, and committed successfully.",
            "repo_url": repo_url,
            "pages_url": pages_url,
            "commit_sha": commit_sha,
        }
        print(f"Task {task_id} completed successfully. Hosted at: {pages_url}")

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        task_store[task_id] = {"status": "FAILED", "details": error_message}
        print(f"Task {task_id} failed. Reason: {error_message}")



def update_project_workflow(task_id: str, task_store: Dict, repo_name: str, code_prompt: str, attachments: list, checks: list, eval_url: str, eval_body:Dict):
    try:
        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Initializing update process"}
        gemini_service.configure_gemini()
        g = github_service.get_github_client()

        task_store[task_id] = {"status": "IN_PROGRESS", "details": f"Fetching existing repository '{repo_name}'"}
        repo = github_service.get_existing_repo(g, f"{repo_name}")
        repo_url = repo.html_url

        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Fetching current files from GitHub"}
        existing_code = github_service.get_file_content(repo, "index.html")
        existing_readme = github_service.get_file_content(repo, "README.md")

        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Generating updated HTML code with AI"}
        updated_code = gemini_service.generate_updated_html_code(code_prompt, existing_code, attachments, checks)

        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Generating updated README.md with AI"}
        updated_readme = gemini_service.generate_updated_read_me(code_prompt, existing_readme, updated_code)

        if not updated_code:
            raise ValueError("AI model returned empty updated code")
        if not updated_readme:
            raise ValueError("AI model returned empty updated README.md")

        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Committing updates to GitHub"}

        # github_service.update_file_to_repo(repo, "index.html", updated_code, "Update AI-generated HTML code")
        # github_service.update_file_to_repo(repo, "README.md", updated_readme, "Update AI-generated README.md")

        commit_sha = github_service.commit_multiple_files(
            repo,
            {
                "index.html": updated_code,
                "README.md": updated_readme
            },
            "chore: Update AI-generated code and documentation"
        )

        task_store[task_id] = {"status": "IN_PROGRESS", "details": "Posting to Eval url"}
        #github_service.enable_github_pages(repo) disabling it since we assume the page is already deployed
        pages_url = f"https://{repo.owner.login}.github.io/{repo.name}/"

        eval_body["commit_sha"] = commit_sha
        eval_body["repo_url"] = repo_url
        eval_body["pages_url"] = pages_url
        response = submit_evaluation(eval_url, eval_body)
        print(f"Eval success: {response}")

        task_store[task_id] = {
            "status": "SUCCESS",
            "details": "Project updated and redeployed successfully.",
            "repo_url": repo_url,
            "pages_url": pages_url,
            "commit_sha": commit_sha,
        }

        print(f"Task {task_id} completed successfully. Live site: {pages_url}")

    except Exception as e:
        error_message = f"An error occurred during update: {str(e)}"
        task_store[task_id] = {"status": "FAILED", "details": error_message}
        print(f"Task {task_id} failed. Reason: {error_message}")




def submit_evaluation(eval_url: str, eval_body: dict, max_retries: int = 10, timeout: int = 20):
    delay = 1
    attempt = 0

    while attempt < max_retries:
        try:
            print(f"Submitting evaluation attempt {attempt + 1}/{max_retries}")
            response = requests.post(eval_url, json=eval_body, timeout=timeout)

            if response.status_code == 200:
                print("Evaluation submitted successfully ")
                return response.json()
            else:
                print(f" Evaluation failed with status {response.status_code}: {response.text}")

        except requests.RequestException as e:
            print(f"Network error during evaluation submission: {e}")

        attempt += 1
        if attempt < max_retries:
            print(f"  Retrying in {delay} seconds")
            time.sleep(delay)
            delay *= 2

    print("All evaluation submission attempts failed")
    return None
