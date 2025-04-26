# app/services/github_service.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def process_push_event(payload):
    """Process a GitHub push event and log commit information (similar to git log)."""
    try:
        # Extract relevant information from the payload
        repo_name = payload["repository"]["full_name"]
        pusher = payload["pusher"]["name"]
        ref = payload["ref"]  # e.g., refs/heads/main
        branch = ref.split("/")[-1]
        
        # Get commit information
        commits = payload.get("commits", [])
        
        # Print header
        print(f"\n==== Push Event: {repo_name} - {branch} ====")
        print(f"Pushed by: {pusher}")
        print(f"Total Commits: {len(commits)}")
        print("-" * 50)
        
        # Process and print each commit (similar to git log)
        for commit in commits:
            commit_id = commit["id"]
            commit_message = commit["message"]
            commit_timestamp = commit["timestamp"]
            commit_url = commit["url"]
            author = commit["author"]
            
            # Format timestamp if needed
            try:
                dt = datetime.fromisoformat(commit_timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = commit_timestamp
            
            # Get changed files
            added_files = commit.get("added", [])
            modified_files = commit.get("modified", [])
            removed_files = commit.get("removed", [])
            
            # Print commit information like git log
            print(f"commit {commit_id}")
            print(f"Author: {author['name']} <{author['email']}>")
            print(f"Date:   {formatted_time}")
            print(f"URL:    {commit_url}")
            print()
            
            # Fix the f-string with newline issue
            newline = "\n"
            indented_message = commit_message.strip().replace(newline, f"{newline}    ")
            print(f"    {indented_message}")
            print()
            
            # Print file changes summary
            if added_files:
                print(f"    Added ({len(added_files)}):")
                for file in added_files[:5]:  # Limit to first 5 files to avoid clutter
                    print(f"      + {file}")
                if len(added_files) > 5:
                    print(f"      + ... {len(added_files)-5} more files")
            
            if modified_files:
                print(f"    Modified ({len(modified_files)}):")
                for file in modified_files[:5]:
                    print(f"      ~ {file}")
                if len(modified_files) > 5:
                    print(f"      ~ ... {len(modified_files)-5} more files")
            
            if removed_files:
                print(f"    Removed ({len(removed_files)}):")
                for file in removed_files[:5]:
                    print(f"      - {file}")
                if len(removed_files) > 5:
                    print(f"      - ... {len(removed_files)-5} more files")
            
            print("-" * 50)
            
        logger.info(f"Processed push event for {repo_name}, branch {branch}, {len(commits)} commits")
        
    except Exception as e:
        logger.error(f"Error processing push event: {str(e)}")
        raise