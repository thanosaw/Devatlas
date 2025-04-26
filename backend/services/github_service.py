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

async def process_pull_request_event(payload):
    """Process a GitHub pull request event."""
    try:
        # Extract relevant information from the payload
        action = payload["action"]  # opened, closed, reopened, etc.
        pr_number = payload["number"]
        pr_title = payload["pull_request"]["title"]
        pr_body = payload["pull_request"]["body"] or ""
        pr_url = payload["pull_request"]["html_url"]
        
        repo_name = payload["repository"]["full_name"]
        user = payload["pull_request"]["user"]["login"]
        
        # Get source and target branch information
        head_branch = payload["pull_request"]["head"]["ref"]
        base_branch = payload["pull_request"]["base"]["ref"]
        
        is_merged = payload["pull_request"].get("merged", False)
        
        # Print header
        print(f"\n==== Pull Request Event: {repo_name} ====")
        print(f"Action: {action.upper()}")
        print(f"PR #{pr_number}: {pr_title}")
        print(f"User: {user}")
        print(f"URL: {pr_url}")
        print("-" * 50)
        
        # Print PR details
        print(f"Source: {head_branch} → Target: {base_branch}")
        
        # Handle different PR actions
        if action == "opened" or action == "reopened":
            print(f"Status: {action.upper()}")
            print(f"\nDescription:")
            
            # Format PR body with indentation
            newline = "\n"
            if pr_body:
                indented_body = pr_body.strip().replace(newline, f"{newline}    ")
                print(f"    {indented_body}")
            else:
                print("    No description provided.")
                
        elif action == "closed":
            if is_merged:
                print("Status: MERGED")
                merged_by = payload["pull_request"]["merged_by"]["login"]
                print(f"Merged by: {merged_by}")
            else:
                print("Status: CLOSED (not merged)")
                
        elif action == "synchronize":
            print("Status: UPDATED (new commits pushed)")
            
        elif action == "review_requested":
            reviewers = payload["pull_request"]["requested_reviewers"]
            reviewer_names = [reviewer["login"] for reviewer in reviewers]
            print(f"Review requested from: {', '.join(reviewer_names)}")
            
        # If the PR was merged, get the changed files
        if action == "closed" and is_merged:
            # In a real implementation, you'd need to make additional API calls
            # to get the full list of changed files in the PR
            print("\nThis PR modified files (showing few examples):")
            print("    * Add file list API call in production version")
            
        print("-" * 50)
            
        logger.info(f"Processed pull request event for {repo_name}, PR #{pr_number}, action: {action}")
        
    except Exception as e:
        logger.error(f"Error processing pull request event: {str(e)}")
        raise