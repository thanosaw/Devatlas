"""
Script to process all nodes in the mock data and add embeddings to them.
"""

import json
import os
import requests
import sys
from typing import Dict, Any, List
from embedding_service import EmbeddingService
from update_mock_data import update_mock_with_slack_data, update_mock_with_github_data

# from backend.services.github_fetch import (
#     fetch_and_save_all_pull_requests, 
#     fetch_and_save_all_issues, 
#     fetch_and_save_all_pr_and_issues,
#     fetch_and_save_all_github_data
# )

# Using more flexible path resolution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(CURRENT_DIR, "mock.json")
OUTPUT_FILE = os.path.join(CURRENT_DIR, "mock_with_embeddings.json")

NODE_TYPE_MAPPING = {
    "users": "User",
    "repositories": "Repository",
    "pullRequests": "PullRequest",
    "issues": "Issue",
    "slackChannels": "Channel",
    "slackMessages": "Message",
    "textChunks": "TextChunk"
}

# Hard-coded mapping of GitHub logins to Slack IDs
GITHUB_TO_SLACK_MAPPING = {
    "MichaelPeng123": "michael123.peng",
    "thanosaw": "uswangandrew",
    "Yatsz": "hyunkim03"
}

def load_data(file_path: str) -> Dict[str, Any]:
    """Load JSON data from file"""
    print(f"Loading data from {file_path}")
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def save_data(data: Dict[str, Any], file_path: str):
    """Save JSON data to file"""
    print(f"Saving data to {file_path}")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def add_slack_ids_to_users(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add hard-coded Slack IDs to specific users based on their GitHub login"""
    updated_users = []
    
    for user in users:
        github_login = user.get("githubLogin")
        if github_login in GITHUB_TO_SLACK_MAPPING:
            # Add or update the slackId field
            user["slackId"] = GITHUB_TO_SLACK_MAPPING[github_login]
            print(f"Added slackId '{GITHUB_TO_SLACK_MAPPING[github_login]}' to user '{github_login}'")
        
        updated_users.append(user)
    
    return updated_users

def create_user_id_to_login_mapping(users: List[Dict[str, Any]]) -> Dict[str, str]:
    """Create a mapping of user IDs to GitHub logins"""
    user_id_to_login = {}
    
    for user in users:
        user_id = user.get("id")
        github_login = user.get("githubLogin")
        
        if user_id and github_login:
            user_id_to_login[user_id] = github_login
    
    print(f"Created mapping for {len(user_id_to_login)} users")
    return user_id_to_login

def create_slack_id_to_user_mapping(users: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
    """Create a mapping of Slack IDs to user information (ID and GitHub login)"""
    slack_id_to_user = {}
    
    for user in users:
        slack_id = user.get("slackId")
        user_id = user.get("id")
        github_login = user.get("githubLogin")
        
        if slack_id and user_id and github_login:
            slack_id_to_user[slack_id] = {
                "userId": user_id,
                "githubLogin": github_login
            }
            print(f"Mapped Slack ID '{slack_id}' to user '{github_login}' with ID '{user_id}'")
    
    print(f"Created Slack ID to user mapping for {len(slack_id_to_user)} users")
    return slack_id_to_user

def add_github_login_to_pull_requests(pull_requests: List[Dict[str, Any]], user_id_to_login: Dict[str, str]) -> List[Dict[str, Any]]:
    """Add GitHub login to pull requests based on the author ID"""
    updated_pull_requests = []
    login_added_count = 0
    
    for pr in pull_requests:
        author_id = pr.get("authorId")
        
        if author_id and author_id in user_id_to_login:
            # Add or update the authorLogin field
            pr["authorLogin"] = user_id_to_login[author_id]
            login_added_count += 1
        
        updated_pull_requests.append(pr)
    
    print(f"Added GitHub login to {login_added_count} pull requests")
    return updated_pull_requests

def add_github_login_to_issues(issues: List[Dict[str, Any]], user_id_to_login: Dict[str, str]) -> List[Dict[str, Any]]:
    """Add GitHub login to issues based on the author ID"""
    updated_issues = []
    login_added_count = 0
    
    for issue in issues:
        author_id = issue.get("authorId")
        
        if author_id and author_id in user_id_to_login:
            # Add or update the authorLogin field
            issue["authorLogin"] = user_id_to_login[author_id]
            login_added_count += 1
        
        updated_issues.append(issue)
    
    print(f"Added GitHub login to {login_added_count} issues")
    return updated_issues

def enrich_slack_messages(messages: List[Dict[str, Any]], slack_id_to_user: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
    """Enrich Slack messages with user ID and GitHub login"""
    updated_messages = []
    enriched_count = 0
    skipped_count = 0
    
    # Debug: print all available Slack IDs in our mapping
    print(f"Available Slack IDs in mapping: {list(slack_id_to_user.keys())}")
    
    for msg in messages:
        slack_id = msg.get("slackId")
        
        if slack_id and slack_id in slack_id_to_user:
            # Add user information to the message
            msg["authorId"] = slack_id_to_user[slack_id]["userId"]
            msg["authorLogin"] = slack_id_to_user[slack_id]["githubLogin"]
            enriched_count += 1
            print(f"Enriched message with Slack ID '{slack_id}', added authorId '{msg['authorId']}' and authorLogin '{msg['authorLogin']}'")
        else:
            # Debug why we couldn't enrich this message
            if not slack_id:
                print(f"Message {msg.get('id', 'unknown')} has no slackId field")
            elif slack_id not in slack_id_to_user:
                print(f"Message has Slack ID '{slack_id}' but not found in our mapping")
            skipped_count += 1
        
        updated_messages.append(msg)
    
    print(f"Enriched {enriched_count} Slack messages with user information, skipped {skipped_count}")
    return updated_messages

def process_all_nodes(data: Dict[str, Any], embedding_service: EmbeddingService) -> Dict[str, Any]:
    """Process all nodes in the data and add embeddings"""
    result = {}
    
    # First pass to handle users and create the mapping
    if "users" in data:
        users = data["users"]
        # Apply hard-coded Slack IDs to users
        users = add_slack_ids_to_users(users)
        result["users"] = users
        
        # Create user ID to GitHub login mapping
        user_id_to_login = create_user_id_to_login_mapping(users)
        
        # Create Slack ID to user mapping
        slack_id_to_user = create_slack_id_to_user_mapping(users)
        
        # Process pull requests with GitHub logins
        if "pullRequests" in data:
            pull_requests = data["pullRequests"]
            pull_requests = add_github_login_to_pull_requests(pull_requests, user_id_to_login)
            result["pullRequests"] = pull_requests
        
        # Process issues with GitHub logins
        if "issues" in data:
            issues = data["issues"]
            issues = add_github_login_to_issues(issues, user_id_to_login)
            result["issues"] = issues
        
        # Process Slack messages with user information
        if "slackMessages" in data:
            messages = data["slackMessages"]
            messages = enrich_slack_messages(messages, slack_id_to_user)
            result["slackMessages"] = messages
    
    # Process remaining collections
    for collection_name, nodes in data.items():
        if collection_name in ["users", "pullRequests", "issues", "slackMessages"]:
            # Already processed
            continue
        elif collection_name in NODE_TYPE_MAPPING:
            node_type = NODE_TYPE_MAPPING[collection_name]
            print(f"Processing {len(nodes)} {node_type} nodes")
            
            processed_nodes = []
            for node in nodes:
                try:
                    node_with_embedding = embedding_service.add_embedding_to_node(node, node_type)
                    processed_nodes.append(node_with_embedding)
                except Exception as e:
                    print(f"Error processing node {node.get('id')}: {e}")
                    processed_nodes.append(node)
            
            result[collection_name] = processed_nodes
        else:
            result[collection_name] = nodes
    
    return result

def main():
    # First fetch the latest GitHub data from the API
    # Only continue here if GitHub data was successfully fetched
    
    print("GitHub data successfully fetched, continuing with process...")
    
    # Update mock.json with Slack data
    print("Updating mock.json with Slack data...")
    update_result = update_mock_with_slack_data()
    if not update_result:
        print("Failed to update mock.json with Slack data")
        
        # Create an empty mock file if needed
        if not os.path.exists(INPUT_FILE):
            print(f"Creating empty mock file at {INPUT_FILE}")
            empty_data = {"users":[],"repositories":[],"pullRequests":[],"issues":[],"slackChannels":[],"slackMessages":[],"textChunks":[]}
            with open(INPUT_FILE, 'w') as f:
                json.dump(empty_data, f, indent=2)
    
    update_result = update_mock_with_github_data()
    if not update_result:
        print("Failed to update mock.json with github data")
        return

    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found")
        return
    
    data = load_data(INPUT_FILE)
    
    embedding_service = EmbeddingService()
    
    processed_data = process_all_nodes(data, embedding_service)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    save_data(processed_data, OUTPUT_FILE)
    
    print(f"Successfully processed data and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()