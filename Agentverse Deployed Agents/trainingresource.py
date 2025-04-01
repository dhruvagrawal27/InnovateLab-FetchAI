from uagents import Agent, Context, Model
import os
import requests

# OpenAI API key (set this via environment variable or hardcode for testing)
openai_api_key = os.getenv("OPENAI_API_KEY") 
class TaskRequest(Model):
    query: str

class TaskResponse(Model):
    result: str

training_resource = Agent(name="training_resource", seed="training_resource_secret_seed")

@training_resource.on_message(model=TaskRequest)
async def handle_task(ctx: Context, sender: str, msg: TaskRequest):
    ctx.logger.info(f"Training Resource Agent received task: {msg.query}")
    
    # Request headers for OpenAI API
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    
    # Define the message for the OpenAI API
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a Training Resource Expert. Identify relevant learning resources, courses, certifications, and development opportunities based on career goals and skill gaps. Suggest specific platforms, courses, and learning paths with cost and time estimates."},
            {"role": "user", "content": msg.query}
        ]
    }
    
    try:
        # Make a request to OpenAI API for a response
        response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
        response_json = response.json()
        
        # Extract result from the response
        result = response_json['choices'][0]['message']['content']
    except Exception as e:
        result = f"Training Resource Agent failed to process: {str(e)}"
    
    # Send the result back to the commander
    await ctx.send(sender, TaskResponse(result=result))