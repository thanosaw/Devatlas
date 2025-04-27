import requests
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

class GitHubFetcher:
    """Class to fetch and process GitHub pull request data."""
    
    def __init__(self, token: Optional[str] = None, owner: str = "", repo: str = ""):
        """Initialize with GitHub credentials."""
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.owner = owner
        self.repo = repo
        
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def set_repo(self, owner: str, repo: str):
        """Update repository information."""
        self.owner = owner
        self.repo = repo
    
    def fetch_pull_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch pull requests and format them according to the specified schema.
        
        Returns:
            List of pull requests with fields: id, number, title, body, state, createdAt
        """
        if not self.owner or not self.repo:
            raise ValueError("Repository owner and name must be set before fetching.")
        
        formatted_prs = []
        page = 1
        per_page = min(100, limit)  # GitHub API max is 100 per page
        remaining = limit
        
        while remaining > 0:
            response = requests.get(
                f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls",
                headers=self.headers,
                params={
                    "state": "all",  # Get open, closed, and merged PRs
                    "page": page,
                    "per_page": per_page
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"GitHub API error: {response.status_code}, {response.text}")
                
            prs = response.json()
            
            if not prs:
                break  # No more PRs to fetch
            
            for pr in prs[:remaining]:
                formatted_pr = {
                    "id": str(pr.get("id", "")),
                    "number": pr.get("number"),
                    "title": pr.get("title", ""),
                    "body": pr.get("body", ""),
                    "state": pr.get("state", ""),
                    "createdAt": pr.get("created_at", ""),
                    "authorId": f"user-{pr.get('user', {}).get('id', '')}" if pr.get('user') else None,
                    "repositoryId": f"repo-{self.owner}-{self.repo}"
                }
                
                formatted_prs.append(formatted_pr)
            
            remaining -= len(prs)
            page += 1
            
            # Check rate limits
            if "X-RateLimit-Remaining" in response.headers:
                remaining_requests = int(response.headers["X-RateLimit-Remaining"])
                if remaining_requests < 5:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    sleep_time = max(0, reset_time - time.time()) + 1
                    time.sleep(min(sleep_time, 60))  # Sleep at most a minute
        
        return formatted_prs
    
    def fetch_pull_request_by_number(self, pr_number: int) -> Dict[str, Any]:
        """
        Fetch a specific pull request by its number.
        
        Args:
            pr_number: The pull request number
            
        Returns:
            Pull request data formatted according to the schema
        """
        if not self.owner or not self.repo:
            raise ValueError("Repository owner and name must be set before fetching.")
        
        response = requests.get(
            f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr_number}",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"GitHub API error: {response.status_code}, {response.text}")
            
        pr = response.json()
        
        formatted_pr = {
            "id": str(pr.get("id", "")),
            "number": pr.get("number"),
            "title": pr.get("title", ""),
            "body": pr.get("body", ""),
            "state": pr.get("state", ""),
            "createdAt": pr.get("created_at", ""),
            "authorId": f"user-{pr.get('user', {}).get('id', '')}" if pr.get('user') else None,
            "repositoryId": f"repo-{self.owner}-{self.repo}"
        }
        
        return formatted_pr

    def fetch_all_pull_requests(self) -> List[Dict[str, Any]]:
        """
        Fetch all pull requests for the repository with no limit.
        
        Returns:
            List of all pull requests formatted according to the schema
        """
        if not self.owner or not self.repo:
            raise ValueError("Repository owner and name must be set before fetching.")
        
        formatted_prs = []
        page = 1
        per_page = 100  # Maximum allowed by GitHub API
        
        while True:
            response = requests.get(
                f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls",
                headers=self.headers,
                params={
                    "state": "all",  # Get open, closed, and merged PRs
                    "page": page,
                    "per_page": per_page
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"GitHub API error: {response.status_code}, {response.text}")
                
            prs = response.json()
            
            if not prs:
                break  # No more PRs to fetch
            
            for pr in prs:
                formatted_pr = {
                    "id": str(pr.get("id", "")),
                    "number": pr.get("number"),
                    "title": pr.get("title", ""),
                    "body": pr.get("body", ""),
                    "state": pr.get("state", ""),
                    "createdAt": pr.get("created_at", ""),
                    "authorId": f"user-{pr.get('user', {}).get('id', '')}" if pr.get('user') else None,
                    "repositoryId": f"repo-{self.owner}-{self.repo}"
                }
                
                formatted_prs.append(formatted_pr)
            
            page += 1
            
            # Check rate limits
            if "X-RateLimit-Remaining" in response.headers:
                remaining_requests = int(response.headers["X-RateLimit-Remaining"])
                if remaining_requests < 5:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    sleep_time = max(0, reset_time - time.time()) + 1
                    time.sleep(min(sleep_time, 60))  # Sleep at most a minute
        
        return formatted_prs

    def fetch_issues(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch issues and format them according to the specified schema.
        
        Returns:
            List of issues with fields: id, number, title, body, state, createdAt, authorId, repositoryId
        """
        if not self.owner or not self.repo:
            raise ValueError("Repository owner and name must be set before fetching.")
        
        formatted_issues = []
        page = 1
        per_page = min(100, limit)  # GitHub API max is 100 per page
        remaining = limit
        
        while remaining > 0:
            response = requests.get(
                f"https://api.github.com/repos/{self.owner}/{self.repo}/issues",
                headers=self.headers,
                params={
                    "state": "all",  # Get open, closed, and merged issues
                    "page": page,
                    "per_page": per_page
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"GitHub API error: {response.status_code}, {response.text}")
                
            issues = response.json()
            
            if not issues:
                break  # No more issues to fetch
            
            for issue in issues[:remaining]:
                # Skip pull requests which also appear in the issues endpoint
                if "pull_request" in issue:
                    continue
                    
                formatted_issue = {
                    "id": f"issue-{issue.get('id', '')}",
                    "number": issue.get("number"),
                    "title": issue.get("title", ""),
                    "body": issue.get("body", ""),
                    "state": issue.get("state", ""),
                    "createdAt": issue.get("created_at", ""),
                    "authorId": f"user-{issue.get('user', {}).get('id', '')}" if issue.get('user') else None,
                    "repositoryId": f"repo-{self.owner}-{self.repo}"
                }
                
                formatted_issues.append(formatted_issue)
            
            remaining -= len(issues)
            page += 1
            
            # Check rate limits
            if "X-RateLimit-Remaining" in response.headers:
                remaining_requests = int(response.headers["X-RateLimit-Remaining"])
                if remaining_requests < 5:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    sleep_time = max(0, reset_time - time.time()) + 1
                    time.sleep(min(sleep_time, 60))  # Sleep at most a minute
        
        return formatted_issues
    
    def fetch_all_issues(self) -> List[Dict[str, Any]]:
        """
        Fetch all issues for the repository with no limit.
        
        Returns:
            List of all issues formatted according to the schema
        """
        if not self.owner or not self.repo:
            raise ValueError("Repository owner and name must be set before fetching.")
        
        formatted_issues = []
        page = 1
        per_page = 100  # Maximum allowed by GitHub API
        
        while True:
            response = requests.get(
                f"https://api.github.com/repos/{self.owner}/{self.repo}/issues",
                headers=self.headers,
                params={
                    "state": "all",  # Get open, closed, and merged issues
                    "page": page,
                    "per_page": per_page
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"GitHub API error: {response.status_code}, {response.text}")
                
            issues = response.json()
            
            if not issues:
                break  # No more issues to fetch
            
            for issue in issues:
                # Skip pull requests which also appear in the issues endpoint
                if "pull_request" in issue:
                    continue
                    
                formatted_issue = {
                    "id": f"issue-{issue.get('id', '')}",
                    "number": issue.get("number"),
                    "title": issue.get("title", ""),
                    "body": issue.get("body", ""),
                    "state": issue.get("state", ""),
                    "createdAt": issue.get("created_at", ""),
                    "authorId": f"user-{issue.get('user', {}).get('id', '')}" if issue.get('user') else None,
                    "repositoryId": f"repo-{self.owner}-{self.repo}"
                }
                
                formatted_issues.append(formatted_issue)
            
            page += 1
            
            # Check rate limits
            if "X-RateLimit-Remaining" in response.headers:
                remaining_requests = int(response.headers["X-RateLimit-Remaining"])
                if remaining_requests < 5:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    sleep_time = max(0, reset_time - time.time()) + 1
                    time.sleep(min(sleep_time, 60))  # Sleep at most a minute
        
        return formatted_issues

    def fetch_repository_info(self) -> Dict[str, Any]:
        """
        Fetch detailed information about the repository.
        
        Returns:
            Repository information in the required format
        """
        if not self.owner or not self.repo:
            raise ValueError("Repository owner and name must be set before fetching.")
            
        response = requests.get(
            f"https://api.github.com/repos/{self.owner}/{self.repo}",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"GitHub API error: {response.status_code}, {response.text}")
            
        repo_data = response.json()
        
        formatted_repo = {
            "id": f"repo-{repo_data.get('id', '')}",
            "name": repo_data.get("name", ""),
            "fullName": repo_data.get("full_name", ""),
            "description": repo_data.get("description", "")
        }
        
        return formatted_repo
    
    def fetch_contributors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch contributors for the repository.
        
        Returns:
            List of contributors with fields: id, githubLogin, name
        """
        if not self.owner or not self.repo:
            raise ValueError("Repository owner and name must be set before fetching.")
            
        formatted_contributors = []
        page = 1
        per_page = min(100, limit)
        remaining = limit
        
        while remaining > 0:
            response = requests.get(
                f"https://api.github.com/repos/{self.owner}/{self.repo}/contributors",
                headers=self.headers,
                params={
                    "page": page,
                    "per_page": per_page
                }
            )
            
            if response.status_code != 200:
                if response.status_code == 404:
                    print(f"No contributors found for {self.owner}/{self.repo}")
                    break
                raise Exception(f"GitHub API error: {response.status_code}, {response.text}")
                
            contributors = response.json()
            
            if not contributors:
                break
                
            for contrib in contributors[:remaining]:
                # Get detailed user information
                user_response = requests.get(
                    contrib.get("url", ""),
                    headers=self.headers
                )
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    formatted_contributor = {
                        "id": f"user-{contrib.get('id', '')}",
                        "githubLogin": contrib.get("login", ""),
                        "name": user_data.get("name", ""),
                        "email": user_data.get("email", "")
                    }
                    
                    formatted_contributors.append(formatted_contributor)
                
            remaining -= len(contributors)
            page += 1
            
            # Handle rate limiting
            if "X-RateLimit-Remaining" in response.headers:
                remaining_requests = int(response.headers["X-RateLimit-Remaining"])
                if remaining_requests < 5:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    sleep_time = max(0, reset_time - time.time()) + 1
                    time.sleep(min(sleep_time, 60))
        
        return formatted_contributors
    
    def fetch_all_contributors(self) -> List[Dict[str, Any]]:
        """
        Fetch all contributors for the repository with no limit.
        
        Returns:
            List of all contributors in the required format
        """
        if not self.owner or not self.repo:
            raise ValueError("Repository owner and name must be set before fetching.")
            
        formatted_contributors = []
        page = 1
        per_page = 100
        
        while True:
            response = requests.get(
                f"https://api.github.com/repos/{self.owner}/{self.repo}/contributors",
                headers=self.headers,
                params={
                    "page": page,
                    "per_page": per_page
                }
            )
            
            if response.status_code != 200:
                if response.status_code == 404:
                    print(f"No contributors found for {self.owner}/{self.repo}")
                    break
                raise Exception(f"GitHub API error: {response.status_code}, {response.text}")
                
            contributors = response.json()
            
            if not contributors:
                break
                
            for contrib in contributors:
                # Get detailed user information
                user_response = requests.get(
                    contrib.get("url", ""),
                    headers=self.headers
                )
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    formatted_contributor = {
                        "id": f"user-{contrib.get('id', '')}",
                        "githubLogin": contrib.get("login", ""),
                        "name": user_data.get("name", ""),
                        "email": user_data.get("email", "")
                    }
                    
                    formatted_contributors.append(formatted_contributor)
                
            page += 1
            
            # Handle rate limiting
            if "X-RateLimit-Remaining" in response.headers:
                remaining_requests = int(response.headers["X-RateLimit-Remaining"])
                if remaining_requests < 5:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    sleep_time = max(0, reset_time - time.time()) + 1
                    time.sleep(min(sleep_time, 60))
        
        return formatted_contributors

# Function to fetch all pull requests and save to collective.json
def fetch_and_save_all_pull_requests(owner: str, repo: str, output_file: str = "collective.json") -> Dict[str, Any]:
    """
    Fetch all pull requests for a repository and save them to a JSON file.
    
    Args:
        owner: Repository owner/organization
        repo: Repository name
        output_file: Path to save the JSON file (default: collective.json)
        
    Returns:
        Dictionary with repository info and the list of pull requests
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    fetcher = GitHubFetcher(token=token)
    fetcher.set_repo(owner, repo)
    
    try:
        # Fetch all pull requests
        pull_requests = fetcher.fetch_all_pull_requests()
        
        # Create result object with metadata
        result = {
            "repository": f"{owner}/{repo}",
            "timestamp": datetime.now().isoformat(),
            "count": len(pull_requests),
            "pull_requests": pull_requests
        }
        
        # Save to JSON file
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Saved {len(pull_requests)} pull requests to {output_file}")
        
        return result
    except Exception as e:
        error_msg = f"Error fetching pull requests: {str(e)}"
        print(error_msg)
        
        # Save error information
        error_result = {
            "repository": f"{owner}/{repo}",
            "timestamp": datetime.now().isoformat(),
            "error": error_msg,
            "pull_requests": []
        }
        
        with open(output_file, 'w') as f:
            json.dump(error_result, f, indent=2)
        
        return error_result

# Function to fetch all issues and save to collective.json
def fetch_and_save_all_issues(owner: str, repo: str, output_file: str = "collective.json") -> Dict[str, Any]:
    """
    Fetch all issues for a repository and save them to a JSON file.
    
    Args:
        owner: Repository owner/organization
        repo: Repository name
        output_file: Path to save the JSON file (default: collective.json)
        
    Returns:
        Dictionary with repository info and the list of issues
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    fetcher = GitHubFetcher(token=token)
    fetcher.set_repo(owner, repo)
    
    try:
        # Fetch all issues
        issues = fetcher.fetch_all_issues()
        
        # Create result object with metadata
        result = {
            "repository": f"{owner}/{repo}",
            "timestamp": datetime.now().isoformat(),
            "count": len(issues),
            "issues": issues
        }
        
        # Save to JSON file
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Saved {len(issues)} issues to {output_file}")
        
        return result
    except Exception as e:
        error_msg = f"Error fetching issues: {str(e)}"
        print(error_msg)
        
        # Save error information
        error_result = {
            "repository": f"{owner}/{repo}",
            "timestamp": datetime.now().isoformat(),
            "error": error_msg,
            "issues": []
        }
        
        with open(output_file, 'w') as f:
            json.dump(error_result, f, indent=2)
        
        return error_result

# Function to fetch all pull requests and issues, combining them into one dataset
def fetch_and_save_all_pr_and_issues(owner: str, repo: str, output_file: str = "collective.json") -> Dict[str, Any]:
    """
    Fetch all pull requests and issues for a repository and add them to an existing JSON file
    or create a new one if it doesn't exist.
    
    Args:
        owner: Repository owner/organization
        repo: Repository name
        output_file: Path to save the JSON file (default: collective.json)
        
    Returns:
        Dictionary with repository info and the combined list of PRs and issues
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    fetcher = GitHubFetcher(token=token)
    fetcher.set_repo(owner, repo)
    
    try:
        # Fetch repository info
        repository = fetcher.fetch_repository_info()
        
        # Fetch all contributors
        contributors = fetcher.fetch_all_contributors()
        
        # Fetch all pull requests and issues
        pull_requests = fetcher.fetch_all_pull_requests()
        issues = fetcher.fetch_all_issues()
        
        # Check if the file exists and load existing data
        existing_data = {
            "users": [],
            "repositories": [],
            "pullRequests": [],
            "issues": []
        }
        
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    existing_data = json.load(f)
                print(f"Loaded existing data from {output_file}")
            except json.JSONDecodeError:
                print(f"Error parsing {output_file}, creating new file")
        
        # Merge new data with existing data
        # For users (avoid duplicates by id)
        existing_user_ids = {user.get("id") for user in existing_data.get("users", [])}
        for user in contributors:
            if user.get("id") not in existing_user_ids:
                existing_data["users"].append(user)
                existing_user_ids.add(user.get("id"))
        
        # For repositories (avoid duplicates by id)
        existing_repo_ids = {repo.get("id") for repo in existing_data.get("repositories", [])}
        if repository.get("id") not in existing_repo_ids:
            existing_data["repositories"].append(repository)
        
        # For pull requests (avoid duplicates by id)
        existing_pr_ids = {pr.get("id") for pr in existing_data.get("pullRequests", [])}
        for pr in pull_requests:
            if pr.get("id") not in existing_pr_ids:
                existing_data["pullRequests"].append(pr)
                existing_pr_ids.add(pr.get("id"))
        
        # For issues (avoid duplicates by id)
        existing_issue_ids = {issue.get("id") for issue in existing_data.get("issues", [])}
        for issue in issues:
            if issue.get("id") not in existing_issue_ids:
                existing_data["issues"].append(issue)
                existing_issue_ids.add(issue.get("id"))
        
        # Save the updated data back to the file
        with open(output_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        print(f"Updated {output_file} with new data:")
        print(f"- Users: {len(existing_data['users'])} (added {len(contributors) - len(existing_user_ids.intersection([u.get('id') for u in contributors]))})")
        print(f"- Repositories: {len(existing_data['repositories'])}")
        print(f"- Pull Requests: {len(existing_data['pullRequests'])} (added {len(pull_requests) - len(existing_pr_ids.intersection([pr.get('id') for pr in pull_requests]))})")
        print(f"- Issues: {len(existing_data['issues'])} (added {len(issues) - len(existing_issue_ids.intersection([i.get('id') for i in issues]))})")
        
        # Add metadata for return value
        metadata = {
            "repository": f"{owner}/{repo}",
            "timestamp": datetime.now().isoformat()
        }
        
        return {**existing_data, **metadata}
    except Exception as e:
        error_msg = f"Error fetching repository data: {str(e)}"
        print(error_msg)
        
        # Create error result but don't overwrite existing file
        error_result = {
            "repository": f"{owner}/{repo}",
            "timestamp": datetime.now().isoformat(),
            "error": error_msg
        }
        
        return error_result

# Updated function to fetch all data in the specified format
def fetch_and_save_all_github_data(owner: str, repo: str, output_file: str = "collective.json") -> Dict[str, Any]:
    """
    Fetch all GitHub data (contributors, repository, pull requests, issues) and add them to
    an existing collective.json file or create a new one if it doesn't exist.
    
    Args:
        owner: Repository owner/organization
        repo: Repository name
        output_file: Path to the JSON file to update (default: collective.json)
        
    Returns:
        Dictionary with all GitHub data in the required format
    """
    return fetch_and_save_all_pr_and_issues(owner, repo, output_file)

# Example function that can be called from an API endpoint
def get_repository_pull_requests(owner: str, repo: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get pull requests for a repository in the specified format.
    
    Args:
        owner: Repository owner/organization
        repo: Repository name
        limit: Maximum number of PRs to fetch
        
    Returns:
        List of pull requests in the specified format
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    fetcher = GitHubFetcher(token=token)
    fetcher.set_repo(owner, repo)
    
    try:
        return fetcher.fetch_pull_requests(limit=limit)
    except Exception as e:
        print(f"Error fetching pull requests: {str(e)}")
        return []

def get_pull_request(owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
    """
    Get a specific pull request in the specified format.
    
    Args:
        owner: Repository owner/organization
        repo: Repository name
        pr_number: Pull request number
        
    Returns:
        Pull request data in the specified format
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    fetcher = GitHubFetcher(token=token)
    fetcher.set_repo(owner, repo)
    
    try:
        return fetcher.fetch_pull_request_by_number(pr_number)
    except Exception as e:
        print(f"Error fetching pull request: {str(e)}")
        return {}

def get_repository_issues(owner: str, repo: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get issues for a repository in the specified format.
    
    Args:
        owner: Repository owner/organization
        repo: Repository name
        limit: Maximum number of issues to fetch
        
    Returns:
        List of issues in the specified format
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    fetcher = GitHubFetcher(token=token)
    fetcher.set_repo(owner, repo)
    
    try:
        return fetcher.fetch_issues(limit=limit)
    except Exception as e:
        print(f"Error fetching issues: {str(e)}")
        return []