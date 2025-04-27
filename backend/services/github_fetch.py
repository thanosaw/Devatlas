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
                    "createdAt": pr.get("created_at", "")
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
            "createdAt": pr.get("created_at", "")
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
                    "createdAt": pr.get("created_at", "")
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