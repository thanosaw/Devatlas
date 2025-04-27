import json
import os
import sys

def update_mock_with_slack_data():
    """
    Updates the mock.json file by replacing only the Slack data
    (slackChannels and slackMessages) with data from slack_entities.json
    while preserving all GitHub-related data.
    """
    # Define file paths - adjusting to be more flexible with relative paths
    mock_file_path = os.path.join(os.path.dirname(__file__), 'mock.json')
    slack_entities_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'slack_entities.json')
    
    # Also check alternative locations
    if not os.path.exists(slack_entities_path):
        alt_paths = [
            'data/slack_entities.json',
            '../data/slack_entities.json',
            'backend/data/slack_entities.json'
        ]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                slack_entities_path = alt_path
                break
    
    # Check if files exist
    if not os.path.exists(mock_file_path):
        print(f"Error: {mock_file_path} not found")
        
        # Create empty mock file if it doesn't exist
        print(f"Creating empty mock file at {mock_file_path}")
        empty_data = {"users":[],"repositories":[],"pullRequests":[],"issues":[],"slackChannels":[],"slackMessages":[],"textChunks":[]}
        with open(mock_file_path, 'w') as f:
            json.dump(empty_data, f, indent=2)
        return True
        
    if not os.path.exists(slack_entities_path):
        print(f"Error: {slack_entities_path} not found")
        return False
    
    try:
        # Load the existing mock data
        with open(mock_file_path, 'r') as f:
            mock_data = json.load(f)
        
        # Load the slack entities data
        with open(slack_entities_path, 'r') as f:
            slack_data = json.load(f)
        
        # Replace only the Slack-related parts of the mock data
        mock_data['slackChannels'] = slack_data.get('channels', [])
        mock_data['slackMessages'] = slack_data.get('messages', [])
        
        # Create a backup of the original mock file
        backup_path = f"{mock_file_path}.bak"
        with open(backup_path, 'w') as f:
            json.dump(mock_data, f, indent=2)
        print(f"Created backup of original mock file at {backup_path}")
        
        # Write the updated mock data back to the file
        with open(mock_file_path, 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        print(f"Successfully updated {mock_file_path} with Slack data from {slack_entities_path}")
        print(f"- Added {len(mock_data['slackChannels'])} channels")
        print(f"- Added {len(mock_data['slackMessages'])} messages")
        return True
        
    except Exception as e:
        print(f"Error updating mock data: {str(e)}")
        return False

if __name__ == "__main__":
    update_mock_with_slack_data() 