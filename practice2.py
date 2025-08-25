from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory

calendar_events = []
email_inbox = []

@tool
def add_calendar_event(input_text: str) -> str:
    """Add an event to the calendar. Format: 'YYYY-MM-DD|Event description'."""
    try:
        date, description = input_text.split("|", 1)
        event = f"{date.strip()}: {description.strip()}"
        calendar_events.append(event)
        return f" Event added: {event}"
    except ValueError:
        return " Invalid format. Use: YYYY-MM-DD|Event description"

@tool
def list_calendar_events(input_text: str) -> str:
    """List all calendar events."""
    if not calendar_events:
        return " No events found."
    return "\n".join(calendar_events)

@tool
def send_email(input_text: str) -> str:
    """Send an email. Format: 'Recipient|Subject|Body'."""
    try:
        recipient, subject, body = input_text.split("|", 2)
        email = {
            "recipient": recipient.strip(),
            "subject": subject.strip(),
            "body": body.strip()
        }
        email_inbox.append(email)
        return f"📧 Email sent to {recipient.strip()} with subject '{subject.strip()}'."
    except ValueError:
        return "Invalid format. Use: Recipient|Subject|Body"
    
@tool
def list_emails(input_text: str) -> str:
    """List all sent emails."""
    if not email_inbox:
        return "📭 No emails sent."
    output = []
    for idx, email in enumerate(email_inbox, 1):
        output.append(f"{idx}. To: {email['recipient']} | Subject: {email['subject']}")
    return "\n".join(output)

tools = [add_calendar_event, list_calendar_events, send_email, list_emails]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI personal assistant with calendar and email management skills."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

llm = ChatOllama(model="phi")
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

print(" AI Assistant with Calendar & Email — type 'exit' to quit\n")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    response = agent_executor.invoke({"input": user_input})
    print("AI:", response["output"])