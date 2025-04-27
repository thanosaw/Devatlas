from uagents import Agent, Context, Model
import json
import os
from typing import Union, List, Dict, Any

# Data model for sending JSON content
class JsonMessage(Model):
    content: Union[List[Any], Dict[str, Any]]
    source_file: str

my_first_agent = Agent(
    name = 'My First Agent',
    port = 5050,
    endpoint = ['http://localhost:5050/submit']
)

second_agent = 'agent1qvt7sh20f449muck0ej0we69x9hdxj90jkt5usx5df4hph0ehj38g0hwrd3'

@my_first_agent.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info(f'My name is {ctx.agent.name} and my address is {ctx.agent.address}')
    
    # Read actions.json file
    actions_file = "actions.json"
    
    try:
        # Create the file with empty array if it doesn't exist
        if not os.path.exists(actions_file):
            with open(actions_file, 'w') as f:
                json.dump([], f)
            ctx.logger.info(f"Created empty {actions_file}")
        
        # Read the file
        with open(actions_file, 'r') as f:
            actions_data = json.load(f)
            
        # Only send if there's data to send
        if actions_data:
            # Send the JSON data to the second agent
            await ctx.send(
                second_agent, 
                JsonMessage(
                    content=actions_data,
                    source_file=actions_file
                )
            )
            ctx.logger.info(f"Sent {actions_file} contents ({len(actions_data) if isinstance(actions_data, list) else 'object'}) to second agent")
            
            # Clear the file by writing an empty array
            with open(actions_file, 'w') as f:
                json.dump([], f)
            ctx.logger.info(f"Cleared {actions_file}")
        else:
            ctx.logger.info(f"No data in {actions_file} to send")
        
    except Exception as e:
        ctx.logger.error(f"Error processing {actions_file}: {str(e)}")

if __name__ == "__main__":
    my_first_agent.run()