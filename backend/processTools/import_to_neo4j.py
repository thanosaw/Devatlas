"""
Script to import data with embeddings into a Neo4j graph database.
"""

import json
import os
import logging
import argparse
from typing import Dict, List, Any, Optional
from neo4j_service import Neo4jService

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Node type mapping
NODE_TYPE_LABELS = {
    "users": "User",
    "repositories": "Repository", 
    "pullRequests": "PullRequest",
    "issues": "Issue",
    "slackChannels": "Channel",
    "slackMessages": "Message",
    "textChunks": "TextChunk"
}

# Configure argument parser
parser = argparse.ArgumentParser(description='Import data into Neo4j graph database')
parser.add_argument('--input', type=str, default='backend/processTools/mock_with_embeddings.json', 
                    help='Input JSON file with embeddings')
parser.add_argument('--neo4j-uri', type=str, default='neo4j://localhost:7687', 
                    help='Neo4j connection URI')
parser.add_argument('--neo4j-user', type=str, default='neo4j', 
                    help='Neo4j username')
parser.add_argument('--neo4j-password', type=str, default='password', 
                    help='Neo4j password')
parser.add_argument('--clear-db', action='store_true', 
                    help='Clear the database before importing')
parser.add_argument('--create-indexes', action='store_true', 
                    help='Create vector indexes for nodes with embeddings')
parser.add_argument('--include-all-messages', action='store_true',
                    help='Include all Slack messages (including join messages)')
args = parser.parse_args()

def load_data(file_path: str) -> Dict[str, Any]:
    """Load JSON data from file"""
    logger.info(f"Loading data from {file_path}")
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def clear_database(neo4j: Neo4jService) -> bool:
    """Clear all data from the Neo4j database"""
    logger.info("Clearing database")
    
    try:
        with neo4j.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        return True
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        return False

def import_nodes(neo4j: Neo4jService, data: Dict[str, Any]) -> Dict[str, int]:
    """Import nodes from data into Neo4j"""
    results = {}
    
    for collection_name, nodes in data.items():
        if collection_name not in NODE_TYPE_LABELS:
            logger.info(f"Skipping collection {collection_name} - no mapping defined")
            continue
        
        label = NODE_TYPE_LABELS[collection_name]
        
        # Filter out join messages unless --include-all-messages is specified
        if collection_name == "slackMessages" and not args.include_all_messages:
            original_count = len(nodes)
            nodes = [msg for msg in nodes if not msg.get("text", "").endswith("has joined the channel")]
            filtered_count = original_count - len(nodes)
            logger.info(f"Filtered out {filtered_count} join messages from {original_count} total messages")
        
        logger.info(f"Importing {len(nodes)} {label} nodes")
        
        success_count = 0
        for node in nodes:
            # For User nodes, ensure slackId is preserved if it exists
            if label == "User" and "slackId" in node:
                logger.info(f"User {node.get('name', 'Unknown')} has slackId: {node['slackId']}")
            
            # Log when PullRequest nodes have authorLogin
            if label == "PullRequest" and "authorLogin" in node:
                logger.info(f"PullRequest #{node.get('number', 'Unknown')} has authorLogin: {node['authorLogin']}")
            
            # Log when Issue nodes have authorLogin
            if label == "Issue" and "authorLogin" in node:
                logger.info(f"Issue #{node.get('number', 'Unknown')} has authorLogin: {node['authorLogin']}")
            
            # Log when Message nodes have author information
            if label == "Message" and "authorId" in node and "authorLogin" in node:
                logger.info(f"Message {node.get('id', 'Unknown')} connected to author: {node['authorLogin']}")
            
            if neo4j.create_node(label, node):
                success_count += 1
        
        results[label] = success_count
        logger.info(f"Imported {success_count}/{len(nodes)} {label} nodes")
    
    return results

def create_relationships(neo4j: Neo4jService, data: Dict[str, Any]) -> Dict[str, int]:
    """Create relationships between nodes based on references in data"""
    results = {}
    
    # Import Pull Request author relationships
    if "pullRequests" in data and "users" in data:
        rel_type = "AUTHORED"
        logger.info(f"Creating {rel_type} relationships for Pull Requests")
        
        success_count = 0
        for pr in data["pullRequests"]:
            author_id = pr.get("authorId")
            if author_id:
                if neo4j.create_relationship("User", author_id, "PullRequest", pr["id"], rel_type):
                    success_count += 1
        
        results[f"User-{rel_type}->PullRequest"] = success_count
        logger.info(f"Created {success_count} {rel_type} relationships")
    
    # Import Issue author relationships
    if "issues" in data and "users" in data:
        rel_type = "AUTHORED"
        logger.info(f"Creating {rel_type} relationships for Issues")
        
        success_count = 0
        for issue in data["issues"]:
            author_id = issue.get("authorId")
            if author_id:
                if neo4j.create_relationship("User", author_id, "Issue", issue["id"], rel_type):
                    success_count += 1
        
        results[f"User-{rel_type}->Issue"] = success_count
        logger.info(f"Created {success_count} {rel_type} relationships")
    
    # Import Repository relationships for PRs and Issues
    if "repositories" in data:
        rel_type = "BELONGS_TO"
        logger.info(f"Creating {rel_type} relationships for PRs and Issues")
        
        pr_count = 0
        if "pullRequests" in data:
            for pr in data["pullRequests"]:
                repo_id = pr.get("repositoryId")
                if repo_id:
                    if neo4j.create_relationship("PullRequest", pr["id"], "Repository", repo_id, rel_type):
                        pr_count += 1
        
        issue_count = 0
        if "issues" in data:
            for issue in data["issues"]:
                repo_id = issue.get("repositoryId")
                if repo_id:
                    if neo4j.create_relationship("Issue", issue["id"], "Repository", repo_id, rel_type):
                        issue_count += 1
        
        results[f"PullRequest-{rel_type}->Repository"] = pr_count
        results[f"Issue-{rel_type}->Repository"] = issue_count
        logger.info(f"Created {pr_count} PR and {issue_count} Issue {rel_type} relationships")
    
    # Import PR reference relationships to Issues
    if "pullRequests" in data and "issues" in data:
        rel_type = "REFERENCES"
        logger.info(f"Creating {rel_type} relationships between PRs and Issues")
        
        success_count = 0
        # This is a simplified approach - in a real system you'd parse the PR body
        # to extract issue references like "fixes #123" or "closes #456"
        for pr in data["pullRequests"]:
            # Fix to safely handle None values in body
            body = pr.get("body", "") or ""
            body = body.lower()
            
            # Find issues referenced in the PR body
            for issue in data["issues"]:
                issue_number = issue.get("number")
                if not issue_number:
                    continue
                
                # Check for common reference patterns
                reference_patterns = [
                    f"fixes #{issue_number}",
                    f"closes #{issue_number}",
                    f"resolves #{issue_number}",
                    f"related to #{issue_number}",
                    f"##{issue_number}"
                ]
                
                referenced = any(pattern in body for pattern in reference_patterns)
                if referenced:
                    properties = {"referenceType": "fixes" if "fixes" in body else "related"}
                    if neo4j.create_relationship("PullRequest", pr["id"], "Issue", issue["id"], rel_type, properties):
                        success_count += 1
        
        results[f"PullRequest-{rel_type}->Issue"] = success_count
        logger.info(f"Created {success_count} {rel_type} relationships")
    
    # Import Slack Message author relationships - now using authorId from the messages
    if "slackMessages" in data and "users" in data:
        rel_type = "AUTHORED"
        logger.info(f"Creating {rel_type} relationships for Slack Messages")
        
        # Filter out join messages if needed
        slack_messages = data["slackMessages"]
        if not args.include_all_messages:
            slack_messages = [msg for msg in slack_messages if not msg.get("text", "").endswith("has joined the channel")]
        
        success_count = 0
        for msg in slack_messages:
            author_id = msg.get("authorId")
            if author_id:
                if neo4j.create_relationship("User", author_id, "Message", msg["id"], rel_type):
                    success_count += 1
        
        results[f"User-{rel_type}->Message"] = success_count
        logger.info(f"Created {success_count} {rel_type} relationships")
    
    # Import Slack Message channel relationships
    if "slackMessages" in data and "slackChannels" in data:
        rel_type = "POSTED_IN"
        logger.info(f"Creating {rel_type} relationships for Slack Messages")
        
        # Filter out join messages if needed
        slack_messages = data["slackMessages"]
        if not args.include_all_messages:
            slack_messages = [msg for msg in slack_messages if not msg.get("text", "").endswith("has joined the channel")]
        
        success_count = 0
        for msg in slack_messages:
            channel_id = msg.get("channelId")
            if channel_id:
                if neo4j.create_relationship("Message", msg["id"], "Channel", channel_id, rel_type):
                    success_count += 1
        
        results[f"Message-{rel_type}->Channel"] = success_count
        logger.info(f"Created {success_count} {rel_type} relationships")
    
    # Import Slack Message reply relationships
    if "slackMessages" in data:
        rel_type = "REPLIES_TO"
        logger.info(f"Creating {rel_type} relationships for Slack Messages")
        
        # Filter out join messages if needed
        slack_messages = data["slackMessages"]
        if not args.include_all_messages:
            slack_messages = [msg for msg in slack_messages if not msg.get("text", "").endswith("has joined the channel")]
        
        # Debug: Check how many messages have threadTs
        thread_ts_count = sum(1 for msg in slack_messages if msg.get("threadTs"))
        logger.info(f"Found {thread_ts_count} messages with threadTs field")
        
        # Create a mapping of threadTs to message IDs
        thread_ts_to_id = {}
        ts_to_id = {}
        for msg in slack_messages:
            # Map the message timestamp (in createdAt) to its ID
            created_at = msg.get("createdAt")
            if created_at:
                # Convert to string format that matches threadTs
                ts_value = created_at.replace('Z', '')
                ts_to_id[ts_value] = msg["id"]
                logger.info(f"Mapped timestamp {ts_value} to message ID {msg['id']}")
        
        success_count = 0
        for msg in slack_messages:
            thread_ts = msg.get("threadTs")
            if thread_ts and thread_ts in ts_to_id:
                parent_id = ts_to_id[thread_ts]
                # Don't create a relationship to itself
                if parent_id != msg["id"]:
                    if neo4j.create_relationship("Message", msg["id"], "Message", parent_id, rel_type):
                        success_count += 1
        
        results[f"Message-{rel_type}->Message"] = success_count
        logger.info(f"Created {success_count} {rel_type} relationships")
    
    # Import Slack Message references to GitHub PRs and Issues - now using authorLogin to improve connections
    if "slackMessages" in data:
        rel_type = "REFERENCES_GITHUB"
        logger.info(f"Creating {rel_type} relationships for Slack Messages")
        
        # Filter out join messages if needed
        slack_messages = data["slackMessages"]
        if not args.include_all_messages:
            slack_messages = [msg for msg in slack_messages if not msg.get("text", "").endswith("has joined the channel")]
        
        # Debug: Check how many messages have authorLogin
        author_login_count = sum(1 for msg in slack_messages if msg.get("authorLogin"))
        logger.info(f"Found {author_login_count} messages with authorLogin field")
        
        pr_refs = 0
        issue_refs = 0
        
        # Create a set of all PR numbers and their IDs for quicker lookup
        pr_number_to_id = {}
        if "pullRequests" in data:
            for pr in data["pullRequests"]:
                pr_number = pr.get("number")
                if pr_number:
                    pr_number_to_id[pr_number] = pr["id"]
            logger.info(f"Indexed {len(pr_number_to_id)} PR numbers for reference matching")
        
        # Create a set of all issue numbers and their IDs for quicker lookup
        issue_number_to_id = {}
        if "issues" in data:
            for issue in data["issues"]:
                issue_number = issue.get("number")
                if issue_number:
                    issue_number_to_id[issue_number] = issue["id"]
            logger.info(f"Indexed {len(issue_number_to_id)} issue numbers for reference matching")
        
        # Create a mapping of GitHub logins to PR and issue IDs
        author_login_to_prs = {}
        author_login_to_issues = {}
        
        if "pullRequests" in data:
            for pr in data["pullRequests"]:
                author_login = pr.get("authorLogin")
                if author_login:
                    if author_login not in author_login_to_prs:
                        author_login_to_prs[author_login] = []
                    author_login_to_prs[author_login].append(pr["id"])
            
            logger.info(f"Mapped {len(author_login_to_prs)} GitHub logins to their PRs")
        
        if "issues" in data:
            for issue in data["issues"]:
                author_login = issue.get("authorLogin")
                if author_login:
                    if author_login not in author_login_to_issues:
                        author_login_to_issues[author_login] = []
                    author_login_to_issues[author_login].append(issue["id"])
            
            logger.info(f"Mapped {len(author_login_to_issues)} GitHub logins to their issues")
        
        # Process each Slack message
        for msg in slack_messages:
            text = msg.get("text", "").lower()
            author_login = msg.get("authorLogin")
            
            # Skip messages without text
            if not text or text == "":
                continue
            
            # Check for PR references in text
            for pr_number in pr_number_to_id:
                # Check for common reference patterns
                pr_patterns = [
                    f"pr #{pr_number}",
                    f"pr#{pr_number}",
                    f"pr {pr_number}",
                    f"pull request #{pr_number}",
                    f"pull request {pr_number}",
                    f"pull/{pr_number}",
                    f"#{pr_number}"
                ]
                
                if any(pattern in text for pattern in pr_patterns):
                    pr_id = pr_number_to_id[pr_number]
                    # Find the PR's author login for comparison
                    pr_author = None
                    for pr in data["pullRequests"]:
                        if pr["id"] == pr_id:
                            pr_author = pr.get("authorLogin")
                            break
                    
                    # Check if this PR was authored by the message author
                    is_author_match = author_login and pr_author and author_login == pr_author
                    
                    properties = {
                        "referenceType": "mention",
                        "authorMatch": is_author_match
                    }
                    
                    if neo4j.create_relationship("Message", msg["id"], "PullRequest", pr_id, rel_type, properties):
                        pr_refs += 1
                        logger.info(f"Created {rel_type} from message to PR #{pr_number}")
            
            # Check for Issue references in text
            for issue_number in issue_number_to_id:
                # Check for common reference patterns
                issue_patterns = [
                    f"issue #{issue_number}",
                    f"issue#{issue_number}",
                    f"issue {issue_number}",
                    f"#{issue_number}",
                    f"issues/{issue_number}"
                ]
                
                if any(pattern in text for pattern in issue_patterns):
                    issue_id = issue_number_to_id[issue_number]
                    # Find the issue's author login for comparison
                    issue_author = None
                    for issue in data["issues"]:
                        if issue["id"] == issue_id:
                            issue_author = issue.get("authorLogin")
                            break
                    
                    # Check if this issue was authored by the message author
                    is_author_match = author_login and issue_author and author_login == issue_author
                    
                    properties = {
                        "referenceType": "mention",
                        "authorMatch": is_author_match
                    }
                    
                    if neo4j.create_relationship("Message", msg["id"], "Issue", issue_id, rel_type, properties):
                        issue_refs += 1
                        logger.info(f"Created {rel_type} from message to Issue #{issue_number}")
            
            # If message has author login, also connect to all PRs/issues created by this author
            if author_login:
                # Connect to all PRs by this author
                if author_login in author_login_to_prs:
                    for pr_id in author_login_to_prs[author_login]:
                        # Only create a relationship if not already mentioned explicitly
                        properties = {
                            "referenceType": "author_context",
                            "authorMatch": True
                        }
                        if neo4j.create_relationship("Message", msg["id"], "PullRequest", pr_id, f"{rel_type}_BY_AUTHOR", properties):
                            pr_refs += 1
                
                # Connect to all issues by this author
                if author_login in author_login_to_issues:
                    for issue_id in author_login_to_issues[author_login]:
                        properties = {
                            "referenceType": "author_context",
                            "authorMatch": True
                        }
                        if neo4j.create_relationship("Message", msg["id"], "Issue", issue_id, f"{rel_type}_BY_AUTHOR", properties):
                            issue_refs += 1
        
        results[f"Message-{rel_type}->PullRequest"] = pr_refs
        results[f"Message-{rel_type}->Issue"] = issue_refs
        logger.info(f"Created {pr_refs} PR and {issue_refs} Issue reference relationships")
    
    # Import TextChunk relationships
    if "textChunks" in data:
        rel_type = "CHUNKED_FROM"
        logger.info(f"Creating {rel_type} relationships for TextChunks")
        
        success_count = 0
        for chunk in data["textChunks"]:
            source_id = chunk.get("sourceId")
            source_type = chunk.get("sourceType")
            
            if source_id and source_type:
                # Map source type to label
                if source_type == "PullRequest":
                    if neo4j.create_relationship("TextChunk", chunk["id"], "PullRequest", source_id, rel_type):
                        success_count += 1
                elif source_type == "Issue":
                    if neo4j.create_relationship("TextChunk", chunk["id"], "Issue", source_id, rel_type):
                        success_count += 1
                elif source_type == "SlackMessage":
                    if neo4j.create_relationship("TextChunk", chunk["id"], "Message", source_id, rel_type):
                        success_count += 1
        
        results[f"TextChunk-{rel_type}->Source"] = success_count
        logger.info(f"Created {success_count} {rel_type} relationships")
    
    return results

def create_vector_indexes(neo4j: Neo4jService) -> Dict[str, bool]:
    """Create vector indexes for nodes with embeddings"""
    results = {}
    
    # Node types with embeddings
    node_types = ["PullRequest", "Issue", "Message", "TextChunk"]
    
    for node_type in node_types:
        logger.info(f"Creating vector index for {node_type}")
        success = neo4j.create_vector_index(node_type)
        results[node_type] = success
    
    return results

def main():
    # Check if the input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file {args.input} not found")
        return
    
    # Load the data
    data = load_data(args.input)
    
    # Initialize Neo4j service
    neo4j = Neo4jService(args.neo4j_uri, args.neo4j_user, args.neo4j_password)
    
    # Test connection
    node_count = neo4j.test_connection()
    if node_count < 0:
        logger.error("Failed to connect to Neo4j")
        return
    
    logger.info(f"Connected to Neo4j database with {node_count} nodes")
    
    # Clear database if requested
    if args.clear_db:
        if not clear_database(neo4j):
            logger.error("Failed to clear database")
            neo4j.close()
            return
    
    # Create constraints
    if not neo4j.create_constraints():
        logger.error("Failed to create constraints")
        neo4j.close()
        return
    
    # Import nodes
    node_results = import_nodes(neo4j, data)
    logger.info(f"Node import results: {node_results}")
    
    # Create relationships
    rel_results = create_relationships(neo4j, data)
    logger.info(f"Relationship creation results: {rel_results}")
    
    # Create vector indexes if requested
    if args.create_indexes:
        index_results = create_vector_indexes(neo4j)
        logger.info(f"Vector index creation results: {index_results}")
    
    # Close Neo4j connection
    neo4j.close()
    
    logger.info("Import completed successfully")

if __name__ == "__main__":
    main()