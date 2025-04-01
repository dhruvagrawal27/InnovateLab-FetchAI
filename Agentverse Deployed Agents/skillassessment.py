from uagents import Agent, Context, Model
import os
import requests

# OpenAI API key (set this via environment variable or hardcode for testing)
openai_api_key = os.getenv("OPENAI_API_KEY") or "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"

class TaskRequest(Model):
    query: str

class TaskResponse(Model):
    result: str

skill_assessment = Agent(name="skill_assessment", seed="skill_assessment_secret_seed")

@skill_assessment.on_message(model=TaskRequest)
async def handle_task(ctx: Context, sender: str, msg: TaskRequest):
    ctx.logger.info(f"Skill Assessment Agent received task: {msg.query}")
    
    # Request headers for OpenAI API
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    
    # Define the message for the OpenAI API
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a Skill Assessment specialist. Evaluate skill sets, identify skill gaps, benchmark against industry standards, and provide a gap analysis with recommendations. Focus on providing clear, measurable skills assessment."},
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
        result = f"Skill Assessment Agent failed to process: {str(e)}"
    
    # Send the result back to the commander
    await ctx.send(sender, TaskResponse(result=result))