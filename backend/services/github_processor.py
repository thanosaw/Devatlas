import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class GitHubProcessor:
    """Process GitHub webhook events and convert them to standardized JSON entities."""
    
    ACTIONS_FILE = "actions.json"
    
    @staticmethod
    def process_webhook(event_type: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a GitHub webhook event and return a list of standardized JSON entities.
        
        Args:
            event_type: The GitHub event type (push, pull_request, etc.)
            payload: The webhook payload data
            
        Returns:
            List of standardized JSON entities
        """
        entities = []
        
        try:
            # Process based on event type
            if event_type == "pull_request":
                entities.extend(GitHubProcessor._process_pull_request(payload))
            elif event_type == "issues":
                entities.extend(GitHubProcessor._process_issue(payload))
            elif event_type == "issue_comment":
                entities.extend(GitHubProcessor._process_issue_comment(payload))
            elif event_type == "pull_request_review_comment" or event_type == "pull_request_review":
                entities.extend(GitHubProcessor._process_pr_comment(payload))
            elif event_type == "discussion":
                entities.extend(GitHubProcessor._process_discussion(payload))
            elif event_type == "discussion_comment":
                entities.extend(GitHubProcessor._process_discussion_comment(payload))
            elif event_type == "label":
                entities.extend(GitHubProcessor._process_label(payload))
            elif event_type == "push":
                # For merge events that come as push events
                if GitHubProcessor._is_merge_event(payload):
                    entities.extend(GitHubProcessor._process_merge(payload))
                # Otherwise process as regular push
                else:
                    entities.extend(GitHubProcessor._process_push(payload))
            
            # If we have entities, save them to the actions.txt file
            if entities:
                GitHubProcessor._save_to_actions_file(entities)
                
            return entities
            
        except Exception as e:
            logger.error(f"Error processing {event_type} webhook: {str(e)}")
            return []
    
    @staticmethod
    def _extract_repository_data(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract repository data from the payload."""
        repo = payload.get("repository", {})
        return {
            "id": repo.get("id"),
            "name": repo.get("name"),
            "fullname": repo.get("full_name"),
            "description": repo.get("description")
        }
    
    @staticmethod
    def _extract_contributor(payload: Dict[str, Any], event_type: str) -> str:
        """Extract contributor information (username or email) from the payload based on event type."""
        # Default contributor information
        contributor = "unknown"
        
        try:
            if event_type == "push" or event_type == "merge":
                # For push/merge events, use the pusher
                pusher = payload.get("pusher", {})
                contributor = pusher.get("name") or pusher.get("email", "unknown")
            elif event_type == "pull_request":
                # For PR events, use the PR creator
                pr = payload.get("pull_request", {})
                user = pr.get("user", {})
                contributor = user.get("login", "unknown")
            elif event_type in ["issue_comment", "pull_request_review_comment"]:
                # For comments, use the comment author
                comment = payload.get("comment", {})
                user = comment.get("user", {})
                contributor = user.get("login", "unknown")
            elif event_type == "pull_request_review":
                # For PR reviews, use the reviewer
                review = payload.get("review", {})
                user = review.get("user", {})
                contributor = user.get("login", "unknown")
            elif event_type == "issues":
                # For issues, use the issue creator
                issue = payload.get("issue", {})
                user = issue.get("user", {})
                contributor = user.get("login", "unknown")
            elif event_type == "discussion" or event_type == "discussion_comment":
                # For discussions/comments, use the discussion author or commenter
                if "comment" in payload:
                    user = payload.get("comment", {}).get("user", {})
                else:
                    user = payload.get("discussion", {}).get("user", {})
                contributor = user.get("login", "unknown")
            elif event_type == "label":
                # For label events, use the sender
                sender = payload.get("sender", {})
                contributor = sender.get("login", "unknown")
        except Exception as e:
            logger.warning(f"Error extracting contributor: {str(e)}")
            
        return contributor
    
    @staticmethod
    def _process_pull_request(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a pull request event and return standardized entities."""
        entities = []
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        
        # Extract contributor
        contributor = GitHubProcessor._extract_contributor(payload, "pull_request")
        
        # Normalize PR state to one of: "open", "closed", or "merged"
        state = pr.get("state", "").lower()
        if state == "closed" and pr.get("merged", False):
            state = "merged"
        elif state not in ["open", "closed", "merged"]:
            # Default to 'open' if state is unknown
            state = "open"
        
        # Create PR entity
        pr_entity = {
            "type": "pullrequest",
            "repository": GitHubProcessor._extract_repository_data(payload),
            "pullrequest": {
                "id": pr.get("id"),
                "number": payload.get("number"),
                "title": pr.get("title"),
                "body": pr.get("body"),
                "state": state,
                "createdAt": pr.get("created_at")
            },
            "contributor": contributor
        }
        entities.append(pr_entity)
        
        return entities
    
    @staticmethod
    def _process_issue(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process an issue event and return standardized entities."""
        entities = []
        action = payload.get("action")
        issue = payload.get("issue", {})
        
        # Extract contributor
        contributor = GitHubProcessor._extract_contributor(payload, "issues")
        
        # Create issue entity
        issue_entity = {
            "type": "issue",
            "repository": GitHubProcessor._extract_repository_data(payload),
            "issue": {
                "id": issue.get("id"),
                "number": issue.get("number"),
                "title": issue.get("title"),
                "body": issue.get("body"),
                "state": issue.get("state"),
                "createdAt": issue.get("created_at"),
                "embedding": None  # This would be populated by an AI embedding service
            },
            "contributor": contributor
        }
        entities.append(issue_entity)
        
        return entities
    
    @staticmethod
    def _process_issue_comment(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process an issue comment event and return standardized entities."""
        entities = []
        action = payload.get("action")
        comment = payload.get("comment", {})
        issue = payload.get("issue", {})
        
        # Extract contributor
        contributor = GitHubProcessor._extract_contributor(payload, "issue_comment")
        
        # Determine if this is a PR comment or issue comment
        # GitHub sometimes sends PR comments as issue comments with a pull_request field
        platform_type = "issue"
        if "pull_request" in issue:
            platform_type = "pr"
            
        # Create comment entity
        comment_entity = {
            "type": "comment",
            "repository": GitHubProcessor._extract_repository_data(payload),
            "comments": {
                "id": comment.get("id"),
                "description": f"Comment on {platform_type} #{issue.get('number')}: {issue.get('title', '')}",
                "platform-type": platform_type,
                "content-type": "comment",
                "body": comment.get("body"),
                "createdAt": comment.get("created_at")
            },
            "contributor": contributor
        }
        entities.append(comment_entity)
        
        return entities
    
    @staticmethod
    def _process_pr_comment(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a pull request review or review comment event."""
        entities = []
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        
        # Handle review comments
        if "comment" in payload:
            comment = payload.get("comment", {})
            
            # Extract contributor
            contributor = GitHubProcessor._extract_contributor(payload, "pull_request_review_comment")
            
            # Determine content type based on review state
            content_type = "comment"  # default
            
            comment_entity = {
                "type": "comment",
                "repository": GitHubProcessor._extract_repository_data(payload),
                "comments": {
                    "id": comment.get("id"),
                    "description": f"Comment on PR #{pr.get('number')}: {pr.get('title', '')}",
                    "platform-type": "pr",
                    "content-type": content_type,
                    "body": comment.get("body"),
                    "createdAt": comment.get("created_at")
                },
                "contributor": contributor
            }
            entities.append(comment_entity)
            
        # Handle full reviews
        elif "review" in payload:
            review = payload.get("review", {})
            
            # Extract contributor
            contributor = GitHubProcessor._extract_contributor(payload, "pull_request_review")
            
            # Determine content type based on review state
            content_type = "comment"  # default
            state = review.get("state", "").lower()
            if state == "approved":
                content_type = "approval"
            elif state == "changes_requested":
                content_type = "change_request"
                
            review_entity = {
                "type": "comment",
                "repository": GitHubProcessor._extract_repository_data(payload),
                "comments": {
                    "id": review.get("id"),
                    "description": f"Review on PR #{pr.get('number')}: {pr.get('title', '')}",
                    "platform-type": "pr",
                    "content-type": content_type,
                    "body": review.get("body", ""),
                    "createdAt": review.get("submitted_at")
                },
                "contributor": contributor
            }
            entities.append(review_entity)
            
        return entities
    
    @staticmethod
    def _process_discussion(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a discussion event and return standardized entities."""
        entities = []
        action = payload.get("action")
        discussion = payload.get("discussion", {})
        
        # Extract contributor
        contributor = GitHubProcessor._extract_contributor(payload, "discussion")
        
        # Discussions don't perfectly map to our entity types, so we'll treat them as issues
        discussion_entity = {
            "type": "discussion",
            "repository": GitHubProcessor._extract_repository_data(payload),
            "issue": {  # Map to issue format for consistency
                "id": discussion.get("id"),
                "number": discussion.get("number"),
                "title": discussion.get("title"),
                "body": discussion.get("body"),
                "state": "open" if not discussion.get("closed_at") else "closed",
                "createdAt": discussion.get("created_at"),
                "embedding": None
            },
            "contributor": contributor
        }
        entities.append(discussion_entity)
        
        return entities
    
    @staticmethod
    def _process_discussion_comment(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a discussion comment event and return standardized entities."""
        entities = []
        action = payload.get("action")
        comment = payload.get("comment", {})
        discussion = payload.get("discussion", {})
        
        # Extract contributor
        contributor = GitHubProcessor._extract_contributor(payload, "discussion_comment")
        
        # Create comment entity
        comment_entity = {
            "type": "comment",
            "repository": GitHubProcessor._extract_repository_data(payload),
            "comments": {
                "id": comment.get("id"),
                "description": f"Comment on discussion '{discussion.get('title', '')}'",
                "platform-type": "discussion",
                "content-type": "comment",
                "body": comment.get("body"),
                "createdAt": comment.get("created_at")
            },
            "contributor": contributor
        }
        entities.append(comment_entity)
        
        return entities
    
    @staticmethod
    def _process_label(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a label event and return standardized entities."""
        entities = []
        action = payload.get("action")
        label = payload.get("label", {})
        
        # Extract contributor
        contributor = GitHubProcessor._extract_contributor(payload, "label")
        
        # Create a comment-like entity for label events
        label_entity = {
            "type": "label",
            "repository": GitHubProcessor._extract_repository_data(payload),
            "comments": {
                "id": label.get("id") or f"label-{label.get('node_id', '0')}",
                "description": f"Label {action}: {label.get('name', '')}",
                "platform-type": "label",
                "content-type": action,  # created, edited, deleted
                "body": label.get("description", ""),
                "createdAt": datetime.utcnow().isoformat()
            },
            "contributor": contributor
        }
        entities.append(label_entity)
        
        return entities
    
    @staticmethod
    def _is_merge_event(payload: Dict[str, Any]) -> bool:
        """Determine if a push event represents a merge."""
        # Check if this is a merge commit by looking at the commit message
        commits = payload.get("commits", [])
        if not commits:
            return False
            
        # GitHub typically creates merge commits with messages like "Merge pull request #X from branch"
        for commit in commits:
            message = commit.get("message", "")
            if message.startswith("Merge pull request") or message.startswith("Merge branch"):
                return True
                
        return False
    
    @staticmethod
    def _process_merge(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a merge event (from push) and return standardized entities."""
        entities = []
        commits = payload.get("commits", [])
        
        # Extract contributor (merger)
        contributor = GitHubProcessor._extract_contributor(payload, "merge")
        
        for commit in commits:
            # Only process merge commits
            if not (commit.get("message", "").startswith("Merge pull request") or 
                    commit.get("message", "").startswith("Merge branch")):
                continue
                
            # Extract PR number if available
            message = commit.get("message", "")
            pr_number = None
            if "Merge pull request #" in message:
                pr_number_str = message.split("Merge pull request #")[1].split(" ")[0]
                try:
                    pr_number = int(pr_number_str)
                except ValueError:
                    pass
            
            # Create merge entity (as a specialized comment)
            merge_entity = {
                "type": "merge",
                "repository": GitHubProcessor._extract_repository_data(payload),
                "comments": {
                    "id": commit.get("id"),
                    "description": f"Merge commit: {message}",
                    "platform-type": "pr" if pr_number else "branch",
                    "content-type": "merge",
                    "body": message,
                    "createdAt": commit.get("timestamp")
                },
                "contributor": contributor
            }
            entities.append(merge_entity)
        
        return entities
    
    @staticmethod
    def _process_push(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a regular push event and return standardized entities."""
        entities = []
        commits = payload.get("commits", [])
        
        # Extract contributor (pusher)
        contributor = GitHubProcessor._extract_contributor(payload, "push")
        
        # We'll represent pushes as comments
        if commits:
            commit_message = ", ".join([c.get("message", "").split("\n")[0] for c in commits[:3]])
            if len(commits) > 3:
                commit_message += f" ... and {len(commits) - 3} more commits"
                
            push_entity = {
                "type": "push",
                "repository": GitHubProcessor._extract_repository_data(payload),
                "comments": {
                    "id": f"push-{commits[0].get('id', '0')}",
                    "description": f"Pushed {len(commits)} commits to {payload.get('ref', '').split('/')[-1]}",
                    "platform-type": "branch",
                    "content-type": "push",
                    "body": commit_message,
                    "createdAt": commits[0].get("timestamp")
                },
                "contributor": contributor
            }
            entities.append(push_entity)
        
        return entities
    
    @staticmethod
    def _save_to_actions_file(entities: List[Dict[str, Any]]) -> None:
        """Save entities to the actions.txt file."""
        try:
            # Create the file if it doesn't exist
            if not os.path.exists(GitHubProcessor.ACTIONS_FILE):
                with open(GitHubProcessor.ACTIONS_FILE, 'w') as f:
                    f.write("[]")
            
            # Read existing content
            with open(GitHubProcessor.ACTIONS_FILE, 'r') as f:
                try:
                    existing_data = json.loads(f.read())
                except json.JSONDecodeError:
                    existing_data = []
            
            # Append new entities
            existing_data.extend(entities)
            
            # Write back to file
            with open(GitHubProcessor.ACTIONS_FILE, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
            logger.info(f"Saved {len(entities)} entities to {GitHubProcessor.ACTIONS_FILE}")
            
        except Exception as e:
            logger.error(f"Error saving entities to {GitHubProcessor.ACTIONS_FILE}: {str(e)}") 