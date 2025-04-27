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

def process_all_nodes(data: Dict[str, Any], embedding_service: EmbeddingService) -> Dict[str, Any]:
    """Process all nodes in the data and add embeddings"""
    result = {}
    
    for collection_name, nodes in data.items():
        if collection_name in NODE_TYPE_MAPPING:
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

    print("Fetching latest GitHub data from API...")
    try:
        response = requests.get("http://127.0.0.1:8000/fetch-github-data/MichaelPeng123/lahacks2025")
        if response.status_code == 200:
            print(f"Successfully fetched GitHub data: {response.json().get('message', '')}")
        else:
            print(f"Failed to fetch GitHub data: {response.status_code}")
            print("Stopping execution - cannot proceed without fresh GitHub data")
            sys.exit(1)  # Exit with error code
    except Exception as e:
        print(f"Error calling GitHub data endpoint: {str(e)}")
        print("Stopping execution - cannot proceed without fresh GitHub data")

    
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