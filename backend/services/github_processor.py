import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class GitHubProcessor:
    """
    Class to process GitHub webhook events and save data to collective.json
    in a structured format with users, repositories, pullRequests, and issues.
    """
    
    # Path to collective.json file
    COLLECTIVE_FILE_PATH = "collective.json"
    
    @classmethod
    def process_webhook(cls, event_type: str, payload: Dict[Any, Any]) -> List[Dict]:
        """
        Process a GitHub webhook event and store data in collective.json
        
        Args:
            event_type: The type of GitHub event (push, pull_request, etc.)
            payload: The webhook payload from GitHub
            
        Returns:
            List of entities that were added or updated
        """
        # Load existing data or create structure if file doesn't exist
        collective_data = cls._load_collective_data()
        
        # Track entities that were added or updated
        processed_entities = []
        
        # Process repository data
        if "repository" in payload:
            repo_data = cls._process_repository(payload["repository"])
            if repo_data:
                # Check if repository already exists
                existing_repo = next((r for r in collective_data["repositories"] 
                                    if r["id"] == repo_data["id"]), None)
                if not existing_repo:
                    collective_data["repositories"].append(repo_data)
                    processed_entities.append({"type": "repository", "id": repo_data["id"]})
        
        # Process user/contributor data
        if "sender" in payload or "user" in payload:
            user_data = cls._process_user(payload.get("sender") or 
                                         payload.get("user") or 
                                         payload.get("pull_request", {}).get("user") or
                                         payload.get("issue", {}).get("user"))
            if user_data:
                # Check if user already exists
                existing_user = next((u for u in collective_data["users"] 
                                    if u["id"] == user_data["id"]), None)
                if not existing_user:
                    collective_data["users"].append(user_data)
                    processed_entities.append({"type": "user", "id": user_data["id"]})
        
        # Process PR data
        if event_type == "pull_request" and "pull_request" in payload:
            pr_data = cls._process_pull_request(payload["pull_request"], payload["repository"])
            if pr_data:
                # Check if PR already exists with this author
                author_pr_exists = False
                for existing_pr in collective_data["pullRequests"]:
                    if (existing_pr["number"] == pr_data["number"] and 
                        existing_pr["repositoryId"] == pr_data["repositoryId"] and
                        existing_pr["authorId"] == pr_data["authorId"]):
                        author_pr_exists = True
                        # Update existing PR
                        existing_pr.update(pr_data)
                        processed_entities.append({"type": "pull_request", "id": pr_data["id"]})
                        break
                
                # If PR with this author doesn't exist, add it
                if not author_pr_exists:
                    collective_data["pullRequests"].append(pr_data)
                    processed_entities.append({"type": "pull_request", "id": pr_data["id"]})
        
        # Process Issue data
        if event_type == "issues" and "issue" in payload:
            issue_data = cls._process_issue(payload["issue"], payload["repository"])
            if issue_data:
                # Check if issue already exists
                existing_issue = next((i for i in collective_data["issues"] 
                                     if i["id"] == issue_data["id"]), None)
                if existing_issue:
                    # Update existing issue
                    existing_issue.update(issue_data)
                    processed_entities.append({"type": "issue", "id": issue_data["id"]})
                else:
                    collective_data["issues"].append(issue_data)
                    processed_entities.append({"type": "issue", "id": issue_data["id"]})
        
        # Save the updated collective data
        cls._save_collective_data(collective_data)
        
        return processed_entities
    
    @classmethod
    def _load_collective_data(cls) -> Dict[str, List[Dict]]:
        """Load data from collective.json or create empty structure"""
        if os.path.exists(cls.COLLECTIVE_FILE_PATH):
            try:
                with open(cls.COLLECTIVE_FILE_PATH, 'r') as f:
                    data = json.load(f)
                
                # Ensure all required sections exist
                for section in ["users", "repositories", "pullRequests", "issues"]:
                    if section not in data:
                        data[section] = []
                
                return data
            except json.JSONDecodeError:
                logger.error(f"Error parsing {cls.COLLECTIVE_FILE_PATH}, creating new file")
        
        # Return empty structure if file doesn't exist or is invalid
        return {
            "users": [],
            "repositories": [],
            "pullRequests": [],
            "issues": []
        }
    
    @classmethod
    def _save_collective_data(cls, data: Dict[str, List[Dict]]) -> None:
        """Save data to collective.json file"""
        with open(cls.COLLECTIVE_FILE_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Updated collective.json with {len(data['users'])} users, "
                   f"{len(data['repositories'])} repositories, "
                   f"{len(data['pullRequests'])} pull requests, "
                   f"{len(data['issues'])} issues")
    
    @staticmethod
    def _process_repository(repo_data: Dict) -> Dict:
        """Process repository data into the required format"""
        if not repo_data:
            return None
        
        return {
            "id": f"repo-{repo_data.get('id', '')}",
            "name": repo_data.get("name", ""),
            "fullName": repo_data.get("full_name", ""),
            "description": repo_data.get("description", "")
        }
    
    @staticmethod
    def _process_user(user_data: Dict) -> Dict:
        """Process user data into the required format"""
        if not user_data:
            return None
        
        return {
            "id": f"user-{user_data.get('id', '')}",
            "githubLogin": user_data.get("login", ""),
            "name": user_data.get("name", ""),
            "email": user_data.get("email")
        }
    
    @staticmethod
    def _process_pull_request(pr_data: Dict, repo_data: Dict) -> Dict:
        """Process PR data into the required format"""
        if not pr_data:
            return None
        
        return {
            "id": str(pr_data.get("id", "")),
            "number": pr_data.get("number"),
            "title": pr_data.get("title", ""),
            "body": pr_data.get("body", ""),
            "state": pr_data.get("state", ""),
            "createdAt": pr_data.get("created_at", ""),
            "authorId": f"user-{pr_data.get('user', {}).get('id', '')}" if pr_data.get('user') else None,
            "repositoryId": f"repo-{repo_data.get('id', '')}" if repo_data else None
        }
    
    @staticmethod
    def _process_issue(issue_data: Dict, repo_data: Dict) -> Dict:
        """Process issue data into the required format"""
        if not issue_data:
            return None
        
        # Skip issues that are actually pull requests
        if "pull_request" in issue_data:
            return None
            
        return {
            "id": f"issue-{issue_data.get('id', '')}",
            "number": issue_data.get("number"),
            "title": issue_data.get("title", ""),
            "body": issue_data.get("body", ""),
            "state": issue_data.get("state", ""),
            "createdAt": issue_data.get("created_at", ""),
            "authorId": f"user-{issue_data.get('user', {}).get('id', '')}" if issue_data.get('user') else None,
            "repositoryId": f"repo-{repo_data.get('id', '')}" if repo_data else None
        } 