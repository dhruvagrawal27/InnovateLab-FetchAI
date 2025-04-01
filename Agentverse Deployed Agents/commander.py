from uagents import Agent, Context, Model
import os
import requests
import json
import re

# Environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
# Models
class TaskRequest(Model):
    query: str

class TaskResponse(Model):
    result: str

# Initialize commander agent
commander = Agent(name="commander", seed="commander_secret_seed")

# Updated workers with all five agent addresses
WORKERS = {
    "test-agent://agent1qvpk7cwgjfdtzfsxv092gcdu0sdsu43z6p0z8nrfckxmcmzd532dgxuy0x5": "Resume Expert",
    "test-agent://agent1qgys89d7tr5rxxamvdhkdg80z9q99jf7sfq08kx0yftt59yjggpsk4ewgm4": "Skill Assessment",
    "test-agent://agent1qfvyd3y9qf9cmsl2waatsdchumu8gjj2fl6ynuzy0mlqcjwpge6ekp74qen": "Demand Analysis",
    "test-agent://agent1qvfed9rmxdz4j488gqvannjs6fatpl3u0ehk2kelez6pz8tr2u8nyxjg5kc": "Training Resource",
    "test-agent://agent1qv4xn6kxtylzyvf5zc4ywx4qcq2g3q6cp2mpvz8twkwmtnm27gl6xp9x7av": "Job Matching"
}

# Function to extract agent addresses from Agentverse Marketplace
async def search_marketplace_agents(ctx: Context, search_terms):
    """
    Search the Agentverse Marketplace for agents based on keywords.
    This simulates interacting with the marketplace to discover agent addresses.
    
    In a complete implementation, this would involve:
    1. Making HTTP requests to the marketplace search API or
    2. Web scraping the marketplace if no API is available
    """
    # For demonstration purposes, we'll log the search attempt
    search_query = " ".join(search_terms)
    ctx.logger.info(f"🔍 Searching Agentverse Marketplace for: {search_query}")
    
    # In a real implementation, this would be where you'd make the actual request
    # to the Agentverse Marketplace API or scrape the website
    
    # For now, simulate the discovery process by returning sample agents
    # that might be found for these search terms
    
    # This is a simplified simulation - in production you would actually query the marketplace
    discovered_agents = {}
    
    # Simulate discovering different agents based on search terms
    for term in search_terms:
        term_lower = term.lower()
        
        # Simulate finding specific agents based on search terms
        if any(word in term_lower for word in ["resume", "cv"]):
            discovered_agents["test-agent://agent1qvpk7cwgjfdtzfsxv092gcdu0sdsu43z6p0z8nrfckxmcmzd532dgxuy0x5"] = "Resume Expert"
        
        if any(word in term_lower for word in ["skill", "assessment", "evaluate"]):
            discovered_agents["test-agent://agent1qgys89d7tr5rxxamvdhkdg80z9q99jf7sfq08kx0yftt59yjggpsk4ewgm4"] = "Skill Assessment"
        
        if any(word in term_lower for word in ["market", "trend", "demand", "analysis"]):
            discovered_agents["test-agent://agent1qfvyd3y9qf9cmsl2waatsdchumu8gjj2fl6ynuzy0mlqcjwpge6ekp74qen"] = "Demand Analysis"
        
        if any(word in term_lower for word in ["training", "learn", "course", "education"]):
            discovered_agents["test-agent://agent1qvfed9rmxdz4j488gqvannjs6fatpl3u0ehk2kelez6pz8tr2u8nyxjg5kc"] = "Training Resource"
        
        if any(word in term_lower for word in ["job", "match", "position", "opportunity"]):
            discovered_agents["test-agent://agent1qv4xn6kxtylzyvf5zc4ywx4qcq2g3q6cp2mpvz8twkwmtnm27gl6xp9x7av"] = "Job Matching"
    
    # Log the discovered agents
    if discovered_agents:
        ctx.logger.info(f"✅ Found {len(discovered_agents)} agents on Agentverse Marketplace")
        for addr, desc in discovered_agents.items():
            ctx.logger.info(f"  - {desc}: {addr}")
    else:
        ctx.logger.info("⚠️ No agents found on Marketplace for these terms")
    
    return discovered_agents

# Function to extract keywords from user query using OpenAI
async def extract_keywords(query):
    """Extract keywords from a user query using OpenAI."""
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    
    keyword_prompt = f"""
    Extract 3-5 key capability keywords from this query that would help find the right specialized agent on the Agentverse Marketplace.
    Return ONLY a comma-separated list of keywords, no explanation.
    
    Query: "{query}"
    """
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You extract keywords for agent discovery."},
            {"role": "user", "content": keyword_prompt}
        ]
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
        keywords = response.json()["choices"][0]["message"]["content"].strip().split(",")
        return [k.strip() for k in keywords]
    except Exception as e:
        return []

# Handler for user queries
@commander.on_message(model=TaskRequest)
async def handle_user_query(ctx: Context, sender: str, msg: TaskRequest):
    ctx.logger.info(f"✅ Commander received query from {sender}: {msg.query}")
    
    # Store user address for later response
    ctx.storage.set("user_address", sender)
    ctx.storage.set("current_query", msg.query)
    
    # Get available workers - combine pre-defined and dynamically discovered
    available_workers = WORKERS.copy()
    
    # Try to extract keywords and discover new agents from the marketplace
    try:
        keywords = await extract_keywords(msg.query)
        ctx.logger.info(f"🔑 Extracted keywords: {keywords}")
        
        if keywords:
            # Search the Agentverse Marketplace for agents based on keywords
            marketplace_agents = await search_marketplace_agents(ctx, keywords)
            
            # Add discovered workers to available workers
            for address, description in marketplace_agents.items():
                available_workers[address] = description
                ctx.logger.info(f"➕ Added marketplace agent: {address} - {description}")
    except Exception as e:
        ctx.logger.error(f"❌ Error in marketplace search process: {e}")
    
    # Select the best worker using OpenAI
    choices_text = "\n".join([f"{name}: {desc}" for name, desc in available_workers.items()])
    prompt = f""" 
    You are a routing assistant. Based on the user query, select the best suited agent.
    
    User Query: "{msg.query}"
    
    Available Workers: 
    {choices_text}
    
    Reply ONLY with the agent address (no explanation), like: test-agent://agent1qv...
    """
    
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an expert agent router."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
        selected_agent = response.json()["choices"][0]["message"]["content"].strip()
        
        # Clean up the selected agent address if it contains extra text
        if "test-agent://" in selected_agent:
            # Extract the agent address using regex to handle potential formatting issues
            match = re.search(r'(test-agent://agent1[a-zA-Z0-9]+)', selected_agent)
            if match:
                selected_agent = match.group(1)
        
        # Store the description of the selected agent
        selected_description = available_workers.get(selected_agent, "Unknown agent")
        ctx.storage.set("selected_agent_desc", selected_description)
        
        ctx.logger.info(f"🤖 OpenAI selected worker: {selected_agent} ({selected_description})")
        await ctx.send(selected_agent, msg)
    except Exception as e:
        ctx.logger.error(f"❌ OpenAI failed to select worker: {e}")
        # Fallback to first available worker
        if available_workers:
            first_agent = next(iter(available_workers))
            first_desc = available_workers[first_agent]
            ctx.logger.info(f"⚠️ Falling back to first available worker: {first_agent} ({first_desc})")
            ctx.storage.set("selected_agent_desc", first_desc)
            await ctx.send(first_agent, msg)

# Handler for responses from worker agents
@commander.on_message(model=TaskResponse)
async def gather_responses(ctx: Context, sender: str, msg: TaskResponse):
    raw = ctx.storage.get("responses") or "[]"
    responses = json.loads(raw)
    
    # Get the agent description if available
    agent_desc = WORKERS.get(sender, "Agent")
    stored_desc = ctx.storage.get("selected_agent_desc")
    if stored_desc and sender != ctx.storage.get("user_address"):
        agent_desc = stored_desc
    
    # Add response with agent information
    response_with_source = f"Response from {agent_desc}:\n{msg.result}"
    responses.append(response_with_source)
    
    ctx.logger.info(f"🧠 Response from {sender} ({agent_desc})")
    ctx.logger.info(f"Current response count: {len(responses)}")
    
    ctx.storage.set("responses", json.dumps(responses))
    
    # When we have received a response, send it back to the user
    if len(responses) >= 1:
        query = ctx.storage.get("current_query") or "your query"
        final_output = f"Results for: \"{query}\"\n\n" + "\n\n---\n\n".join(responses)
        user_address = ctx.storage.get("user_address")
        
        if not user_address:
            ctx.logger.error("❌ No user address found in storage.")
            return
        
        try:
            ctx.logger.info(f"📦 Sending final output to user: {user_address}")
            await ctx.send(user_address, TaskResponse(result=final_output))
            ctx.logger.info("✅ Final response sent to user!")
        except Exception as e:
            ctx.logger.error(f"❌ Failed to send to user: {e}")
        
        # Clear responses after sending
        ctx.storage.set("responses", json.dumps([]))
