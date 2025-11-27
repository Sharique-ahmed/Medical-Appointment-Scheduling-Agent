import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from agentConfig import agent,get_memory_as_text,summarize_response,add_to_memory,llm

# Declaring the fastAPI
app = FastAPI()

class ChatRequest(BaseModel):
    message: str

# The base route to handle all things
@app.post("/chat")
async def chat(req: ChatRequest):    

    memoryText = get_memory_as_text()

    chatPrompt = f"""
    Here is the conversation so far:
    {memoryText}

    Now the user says: {req.message}
    """

    inputs = {"input":chatPrompt}
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, agent.invoke, inputs)
    
    # Extract the final assistant message content
    assistant_result = result.get("output",str(result))  # Assumes last message is AI response

    # Summarizing the response
    short_reply = summarize_response(llm, assistant_result)

    # Save back to memory only if it's not a suggestion
    add_to_memory(req.message, short_reply)

    return {
        "answer": assistant_result
    }

