from datetime import datetime
from utils import OPENAI_API_KEY
from tools.faqTool import faq_tool
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from tools.calendlyTools import event_types_tool,availability_tool,booking_tool

currentDatetime = datetime.now().strftime("%Y-%m-%d %I:%M %p")


llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY, 
    model_name="gpt-4o-mini", 
    temperature=0.2
)

# Simple dictionary-based memory
custom_memory = {
    "chat_history": []
}

def summarize_response(llm, reply_text: str) -> str:
    """Use LLM to generate a short summary of the reply."""
    prompt = f"""
    Summarize the following chatbot reply into 2-3 short lines, keep important informat the same
    {reply_text}
    """
    summary = llm.invoke(prompt)
    return summary.content if hasattr(summary, "content") else str(summary)

def add_to_memory(user_input: str, agent_reply: str):
    """Append conversation to memory dictionary if store=True."""
    custom_memory["chat_history"].append(f"User: {user_input}")
    custom_memory["chat_history"].append(f"Agent: {agent_reply}")

def get_memory_as_text(max_turns: int = 10) -> str:
    """Return last N exchanges as a single string."""
    return "\n".join(custom_memory["chat_history"][-max_turns*2:])  # 2 lines per turn

agent = initialize_agent(
    llm=llm,
    tools=[faq_tool,event_types_tool,availability_tool,booking_tool],
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs = {
        "system_message": f"""
            You are a clinic receptionist assistant. 
            Your job is simple:
            the current Date time is - {currentDatetime}
            Help users to book appoinments and help with FAQ.
            Always confirm the time slot with the user before creating an appointment.
            Collect missing details (name, dateTime, email , appointment Type).
            Provide basic clinic info (hours, services, address, payment) but no medical/diagnostic advice.
            If the user's date phrase is vague, ask for exact confirmation (e.g., “Did you mean 29 Nov 2025?”).
        """
    }
)