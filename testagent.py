from uagents import Agent, Context, Model
import re

class TaskRequest(Model):
    query: str

class TaskResponse(Model):
    result: str

user = Agent(
    name="test_user",
    seed="test_user_secret",
    mailbox=True
)

@user.on_event("startup")
async def ask(ctx: Context):
    print("🚀 Sending query to Commander...")
    await ctx.send(
        "test-agent://agent1qtjjk3xfvel6qkqk48n2he4kwqmytwcc6tplvszvwty9qp38nfs4w3r3xme",  # Commander
        TaskRequest(query="Tell me top 5 resouces to learn data analysis using python?")  # User's query
    )

def strip_markdown(md_text):
    import re
    # Remove bold, italics, and other markdown
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', md_text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'[*_]{1,2}', '', text)
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'\n\s+', '\n', text)
    return text.strip()


@user.on_message(model=TaskResponse)
async def handle(ctx: Context, sender: str, msg: TaskResponse):
    print("\n✅ Final Response from Commander:\n")
    clean_text = strip_markdown(msg.result)
    print(clean_text)

user.run()
