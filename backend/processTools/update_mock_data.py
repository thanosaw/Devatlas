import json
import os
import sys

def update_mock_with_slack_data():
    """
    Updates the mock.json file by replacing only the Slack data
    (slackChannels and slackMessages) with data from slack_entities.json
    while preserving all GitHub-related data.
    """
    # Define file paths
    mock_file_path = 'backend/processTools/mock.json'
    slack_entities_path = 'data/slack_entities.json'
    
    # Check if files exist
    if not os.path.exists(mock_file_path):
        print("Error: {} not found".format(mock_file_path))
        return False
        
    if not os.path.exists(slack_entities_path):
        print("Error: {} not found".format(slack_entities_path))
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
        backup_path = "{}.bak".format(mock_file_path)
        with open(backup_path, 'w') as f:
            json.dump(mock_data, f, indent=2)
        print("Created backup of original mock file at {}".format(backup_path))
        
        # Write the updated mock data back to the file
        with open(mock_file_path, 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        print("Successfully updated {} with Slack data from {}".format(mock_file_path, slack_entities_path))
        print("- Added {} channels".format(len(mock_data['slackChannels'])))
        print("- Added {} messages".format(len(mock_data['slackMessages'])))
        return True
        
    except Exception as e:
        print("Error updating mock data: {}".format(str(e)))
        return False

if __name__ == "__main__":
    update_mock_with_slack_data() 