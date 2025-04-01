# Required installations:
# pip install uagents openai python-dotenv requests
# Add at the top of your script
from pyngrok import ngrok
import time
ngrok.set_auth_token("2v4pO9ooU8CuoEWeNwZBVUoW8UJ_6oKS9xe2kdrJEio6RWQx4")

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import os
from dotenv import load_dotenv
import openai
import json
import requests


# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define message models
class UserQuery(Model):
    query: str
    user_id: str

class AgentResponse(Model):
    response: str
    agent_name: str

class TunnelRequest(Model):
    agent_name: str
    port: int

class TunnelResponse(Model):
    endpoint: str
    success: bool
    message: str

# Define common metadata for Innovation Lab category
innovation_lab_metadata = {
    "categories": ["Innovation Lab"],
    "tags": ["career", "guidance", "innovation", "hackathon"]
}

# Create the Orchestrator Agent with metadata
orchestrator = Agent(
    name="Career Guidance Orchestrator",
    seed=os.getenv("ORCHESTRATOR_SEED", "orchestrator_secret_seed_phrase"),
    port=8000,
    endpoint=None,  # Will be set dynamically
    mailbox=True,
    metadata={
        **innovation_lab_metadata,
        "description": "Central AI agent that coordinates all career guidance sub-agents and user interaction"
    }
)

# Create Skill Assessment Agent with metadata
skill_assessment = Agent(
    name="Skill Assessment Agent",
    seed=os.getenv("SKILL_ASSESSMENT_SEED", "skill_assessment_secret_seed_phrase"),
    port=8001,
    endpoint=None,  # Will be set dynamically
    mailbox=True,
    metadata={
        **innovation_lab_metadata,
        "description": "Analyzes user aptitude, experience, and interests to determine career readiness"
    }
)

# Create Demand Analysis Agent with metadata
demand_analysis = Agent(
    name="Demand Analysis Agent", 
    seed=os.getenv("DEMAND_ANALYSIS_SEED", "demand_analysis_secret_seed_phrase"),
    port=8002,
    endpoint=None,  # Will be set dynamically
    mailbox=True,
    metadata={
        **innovation_lab_metadata,
        "description": "Fetches real-time job market data to identify in-demand skills by role and location"
    }
)

# Create Training Resource Agent with metadata
training_resource = Agent(
    name="Training Resource Agent",
    seed=os.getenv("TRAINING_RESOURCE_SEED", "training_resource_secret_seed_phrase"),
    port=8003,
    endpoint=None,  # Will be set dynamically
    mailbox=True,
    metadata={
        **innovation_lab_metadata,
        "description": "Recommends relevant courses, certifications, and local government programs"
    }
)

# Create Job Matching Agent with metadata
job_matching = Agent(
    name="Job Matching Agent",
    seed=os.getenv("JOB_MATCHING_SEED", "job_matching_secret_seed_phrase"),
    port=8004,
    endpoint=None,  # Will be set dynamically
    mailbox=True,
    metadata={
        **innovation_lab_metadata,
        "description": "Finds tailored job listings from portals based on user profile and preferences"
    }
)

# Create Personal Assistant Agent with metadata
personal_assistant = Agent(
    name="Personal Career Assistant",
    seed=os.getenv("PERSONAL_ASSISTANT_SEED", "assistant_secret_seed_phrase"),
    port=8005,
    endpoint=None,  # Will be set dynamically
    mailbox=True,
    metadata={
        **innovation_lab_metadata,
        "description": "Personalized assistant that coordinates between specialized career agents"
    }
)
# Add this function to your code
def ensure_agent_funding(agent):
    from uagents.setup import fund_agent_if_low
    print(f"Ensuring {agent.name} has sufficient funds...")
    fund_agent_if_low(agent.wallet.address())
    print(f"Funding complete for {agent.name}")

# Call this function for each agent before running them
ensure_agent_funding(orchestrator)
ensure_agent_funding(skill_assessment)
ensure_agent_funding(demand_analysis)
ensure_agent_funding(training_resource)
ensure_agent_funding(job_matching)
ensure_agent_funding(personal_assistant)

# Tunnel Manager Class
class TunnelManager:
    def __init__(self, max_tunnels=3):
        self.max_tunnels = max_tunnels
        self.active_tunnels = {}  # {agent_name: ngrok_tunnel}
        self.tunnel_queue = []    # List of agent names waiting for tunnels
        self.endpoints = {}       # {agent_name: endpoint_url}
    
    def request_tunnel(self, agent_name, port):
        """Request a tunnel for an agent. If no tunnels are available, queue the request."""
        if len(self.active_tunnels) >= self.max_tunnels:
            # Queue the request
            self.tunnel_queue.append((agent_name, port))
            return None, f"No tunnels available. Request for {agent_name} queued."
        
        # Create a new tunnel
        return self._create_tunnel(agent_name, port)
    
    def release_tunnel(self, agent_name):
        """Release a tunnel for an agent."""
        if agent_name in self.active_tunnels:
            try:
                ngrok.disconnect(self.active_tunnels[agent_name].public_url)
                del self.active_tunnels[agent_name]
                del self.endpoints[agent_name]
                
                # Process queue if there are pending requests
                if self.tunnel_queue:
                    next_agent, next_port = self.tunnel_queue.pop(0)
                    self._create_tunnel(next_agent, next_port)
                
                return True, f"Tunnel for {agent_name} released."
            except Exception as e:
                return False, f"Failed to release tunnel for {agent_name}: {str(e)}"
        
        return False, f"No active tunnel for {agent_name}."
    
    def _create_tunnel(self, agent_name, port):
        """Create a new tunnel for an agent."""
        try:
            tunnel = ngrok.connect(port)
            self.active_tunnels[agent_name] = tunnel
            endpoint = f"{tunnel.public_url}/submit"
            self.endpoints[agent_name] = endpoint
            return endpoint, f"Tunnel created for {agent_name}: {endpoint}"
        except Exception as e:
            return None, f"Failed to create tunnel for {agent_name}: {str(e)}"
    
    def get_endpoint(self, agent_name):
        """Get the endpoint for an agent."""
        return self.endpoints.get(agent_name)

# Create tunnel manager
tunnel_manager = TunnelManager(max_tunnels=3)

# Register all agents with Agentverse
# Function to manually register agents with Agentverse
def register_agent_manually(agent, api_key):
    agentverse_url = "https://agentverse.ai/api/v1/register"
    
    # Check if agent has an endpoint
    if not agent.endpoint:
        return f"Agent {agent.name} has no endpoint. Not registered."
    
    # Prepare registration data
    registration_data = {
        "address": agent.address,
        "name": agent.name,
        "endpoint": agent.endpoint,
        "description": agent.metadata.get("description", ""),
        "categories": agent.metadata.get("categories", []),
        "tags": agent.metadata.get("tags", [])
    }
    
    # Set request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Send registration request
    try:
        response = requests.post(
            agentverse_url,
            json=registration_data,
            headers=headers
        )
        
        if response.status_code == 200:
            return f"Success: {response.json()}"
        else:
            return f"Failed: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error: {str(e)}"

# Register all agents with Agentverse
def register_agent_with_tunnel(agent, tunnel_manager):
    # Request a tunnel for the agent
    endpoint, message = tunnel_manager.request_tunnel(agent.name, agent._port)
    
    if endpoint:
        # Set the agent's endpoint
        agent.endpoint = endpoint
        print(f"Set endpoint for {agent.name}: {endpoint}")
        
        # Register the agent with Agentverse
        api_key = os.getenv("AGENTVERSE_API_KEY")
        result = register_agent_manually(agent, api_key)
        print(f"Registration result for {agent.name}: {result}")
        
        return True, result
    else:
        print(f"Could not get tunnel for {agent.name}: {message}")
        return False, message

# Skill Assessment Agent functionality
@skill_assessment.on_message(UserQuery, replies=AgentResponse)
async def handle_skill_assessment(ctx: Context, sender: str, msg: UserQuery):
    ctx.logger.info(f"Skill Assessment Agent received: {msg.query}")
    
    # Use OpenAI to analyze skills
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a career skills assessment expert. Analyze the user's skills and experience."},
            {"role": "user", "content": msg.query}
        ]
    )
    
    analysis = response.choices[0].message['content']
    
    await ctx.send(
        sender,
        AgentResponse(response=analysis, agent_name="Skill Assessment")
    )

# Demand Analysis Agent functionality
@demand_analysis.on_message(UserQuery, replies=AgentResponse)
async def handle_demand_analysis(ctx: Context, sender: str, msg: UserQuery):
    ctx.logger.info(f"Demand Analysis Agent received: {msg.query}")
    
    # Simulate fetching job market data (in a real implementation, you'd connect to an API)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a job market analyst. Provide information about current job market trends."},
            {"role": "user", "content": f"What are the current job market trends for someone with these skills and interests: {msg.query}"}
        ]
    )
    
    analysis = response.choices[0].message['content']
    
    await ctx.send(
        sender,
        AgentResponse(response=analysis, agent_name="Demand Analysis")
    )

# Training Resource Agent functionality
@training_resource.on_message(UserQuery, replies=AgentResponse)
async def handle_training_resource(ctx: Context, sender: str, msg: UserQuery):
    ctx.logger.info(f"Training Resource Agent received: {msg.query}")
    
    # Use OpenAI to suggest learning resources
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a career coach providing learning resources. Suggest online courses, books, or tutorials for skill enhancement."},
            {"role": "user", "content": f"Suggest learning resources for improving skills in: {msg.query}"}
        ]
    )
    
    resources = response.choices[0].message['content']
    
    await ctx.send(
        sender,
        AgentResponse(response=resources, agent_name="Training Resource")
    )

# Job Matching Agent functionality
@job_matching.on_message(UserQuery, replies=AgentResponse)
async def handle_job_matching(ctx: Context, sender: str, msg: UserQuery):
    ctx.logger.info(f"Job Matching Agent received: {msg.query}")
    
    # Use OpenAI to match jobs (in real-world, integrate with job listing APIs)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a job matching assistant. Find suitable job roles based on the user's skills and preferences."},
            {"role": "user", "content": f"Find job opportunities for someone with these skills and preferences: {msg.query}"}
        ]
    )
    
    job_listings = response.choices[0].message['content']
    
    await ctx.send(
        sender,
        AgentResponse(response=job_listings, agent_name="Job Matching")
    )

# Store all responses for a user query
user_responses = {}

# Orchestrator handling - modified to use active agents
@orchestrator.on_message(UserQuery)
async def handle_orchestration(ctx: Context, sender: str, msg: UserQuery):
    ctx.logger.info(f"Orchestrator received query: {msg.query}")
    
    # Initialize responses dictionary for this query
    query_id = f"{msg.user_id}_{len(user_responses)}"
    user_responses[query_id] = {
        "skill_assessment": None,
        "demand_analysis": None,
        "training_resource": None,
        "job_matching": None
    }
    
    # Get active agents
    active_agents = [agent for agent in [skill_assessment, demand_analysis, training_resource, job_matching]
                     if tunnel_manager.get_endpoint(agent.name)]
    
    # Send the query to all active agents
    for agent in active_agents:
        await ctx.send(agent.address, UserQuery(query=msg.query, user_id=query_id))
        ctx.logger.info(f"Sent query to {agent.name}")

# Handle agent responses
@orchestrator.on_message(AgentResponse)
async def handle_agent_response(ctx: Context, sender: str, msg: AgentResponse):
    ctx.logger.info(f"Received response from {msg.agent_name}")
    
    # In a real implementation, you would parse the user_id from the response
    # For simplicity, we'll use a global variable here
    current_query_id = list(user_responses.keys())[-1]
    
    # Store the response
    user_responses[current_query_id][msg.agent_name.lower().replace(" ", "_")] = msg.response
    
    # Check if we have all responses from active agents
    responses = user_responses[current_query_id]
    active_agents = [agent.name.lower().replace(" ", "_") for agent in [skill_assessment, demand_analysis, training_resource, job_matching]
                     if tunnel_manager.get_endpoint(agent.name)]
    
    all_received = True
    for agent_name in active_agents:
        if responses.get(agent_name) is None:
            all_received = False
            break
    
    if all_received:
        # Generate a consolidated response
        consolidated = "Career Guidance Summary:\n\n"
        
        for agent_name, response in responses.items():
            if response is not None:
                consolidated += f"{agent_name.replace('_', ' ').title()}: {response}\n\n"
        
        # In a real implementation, you would send this back to the user interface
        ctx.logger.info("Consolidated response ready")
        ctx.logger.info(consolidated)
        
        # Optionally, you could send this back to the user via a message or email
        await ctx.send(sender, UserQuery(query=consolidated, user_id=current_query_id))

# Custom tunnel request handler for orchestrator
@orchestrator.on_message(TunnelRequest, replies=TunnelResponse)
async def handle_tunnel_request(ctx: Context, sender: str, msg: TunnelRequest):
    # Request a tunnel for the agent
    endpoint, message = tunnel_manager.request_tunnel(msg.agent_name, msg.port)
    
    # Send the response
    await ctx.send(
        sender,
        TunnelResponse(
            endpoint=endpoint if endpoint else "",
            success=endpoint is not None,
            message=message
        )
    )

# Initialize the system
async def initialize_system():
    # Start with the orchestrator and 2 key agents
    register_agent_with_tunnel(orchestrator, tunnel_manager)
    register_agent_with_tunnel(skill_assessment, tunnel_manager)
    register_agent_with_tunnel(demand_analysis, tunnel_manager)
    
    # The other agents will be activated on-demand

# Helper function to rotate tunnels
def rotate_tunnels(release_agent_name, request_agent_name, request_port):
    print(f"Rotating tunnels: Releasing {release_agent_name}, requesting for {request_agent_name}")
    success, message = tunnel_manager.release_tunnel(release_agent_name)
    print(f"Release result: {message}")
    
    endpoint, message = tunnel_manager.request_tunnel(request_agent_name, request_port)
    print(f"Request result: {message}")
    
    return endpoint, message
import asyncio

async def run_all_agents():
    # Start all agents concurrently
    tasks = [
        orchestrator.run_async(),
        skill_assessment.run_async(),
        demand_analysis.run_async(),
        training_resource.run_async(),
        job_matching.run_async(),
        personal_assistant.run_async()
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Initialize the tunnel manager
    print("Initializing tunnel manager...")
    
    # Start with the orchestrator and 2 key agents
    print("Setting up initial agents...")
    register_agent_with_tunnel(orchestrator, tunnel_manager)
    register_agent_with_tunnel(skill_assessment, tunnel_manager)
    register_agent_with_tunnel(demand_analysis, tunnel_manager)
    
    # Ensure funding for all agents
    for agent in [orchestrator, skill_assessment, demand_analysis, training_resource, job_matching, personal_assistant]:
        ensure_agent_funding(agent)
    
    # Start the agents
    print("Starting agents...")
    try:
        asyncio.run(run_all_agents())
    except KeyboardInterrupt:
        print("Shutting down...")
        # Disconnect all tunnels
        for agent_name in list(tunnel_manager.active_tunnels.keys()):
            tunnel_manager.release_tunnel(agent_name)