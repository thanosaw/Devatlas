# from uagents import Agent, Context, Model
# import json
# from typing import Union, List, Dict, Any

# # Data model for regular messages
# class Message(Model):
#     message: str
#     field: int

# # Data model for JSON content
# class JsonMessage(Model):
#     content: Union[List[Any], Dict[str, Any]]
#     source_file: str

# my_second_agent = Agent(
#     name = 'My Second Agent',
#     port = 5051,
#     endpoint = ['http://localhost:5051/submit']
# )

# @my_second_agent.on_event('startup')
# async def startup_handler(ctx: Context):
#     ctx.logger.info(f'My name is {ctx.agent.name} and my address is {ctx.agent.address}')

# # Handle incoming messages with the Request model
# @my_second_agent.on_message(model=Message)
# async def message_handler(ctx: Context, sender: str, msg: Message):
#     ctx.logger.info(f'I have received a message from {sender}.')
#     ctx.logger.info(f'I have received a message {msg.message}.')

# @my_second_agent.on_message(model=JsonMessage)
# async def json_handler(ctx: Context, sender: str, msg: JsonMessage):
#     ctx.logger.info(f'Received JSON content from {sender} from file: {msg.source_file}')
    
#     # Format and print the JSON content nicely
#     formatted_json = json.dumps(msg.content, indent=2)
#     ctx.logger.info("JSON Content:")
    
#     # Print the content in chunks to avoid overwhelming the console
#     max_line_length = 100
    
#     # Split the formatted JSON into lines
#     json_lines = formatted_json.split('\n')
    
#     # Print each line (or chunk if line is too long)
#     for line in json_lines:
#         if len(line) <= max_line_length:
#             ctx.logger.info(line)
#         else:
#             # Break long lines into chunks
#             for i in range(0, len(line), max_line_length):
#                 chunk = line[i:i+max_line_length]
#                 ctx.logger.info(chunk)
    
#     # Also log the number of items if it's a list
#     if isinstance(msg.content, list):
#         ctx.logger.info(f"Received {len(msg.content)} items in the JSON array")

# if __name__ == "__main__":
#     my_second_agent.run()