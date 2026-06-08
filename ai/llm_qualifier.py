import os
import json
import logging
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# You can swap this to your local Qwen model using a base_url, 
# but for the portfolio we default to standard OpenAI architecture.
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "mock-key-for-portfolio"),
    base_url=os.getenv("OPENAI_BASE_URL") # E.g., http://localhost:11434/v1 for Ollama
)

async def qualify_lead(inquiry_text: str) -> dict:
    """
    Takes an inbound message and strictly formats it into JSON via the LLM.
    Acts exactly like a high-end bot node in Make.com/GHL.
    """
    
    system_prompt = """
    You are a qualification engine for a financial advisory firm.
    Analyze the user's inquiry text. Extract the following fields:
    - "estimated_capital": string (e.g., "$10k", "Unknown")
    - "urgency_score": integer (1-5, where 5 is highly urgent)
    - "primary_goal": string (brief summary of what they want)
    - "status": string (MUST be exactly "qualified" if they show intent, or "handoff" if garbage/unclear)
    
    Output STRICTLY as a JSON object. No markdown formatting, no conversational text.
    """
    
    try:
        response = await client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": inquiry_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            timeout=10.0
        )
        
        raw_json = response.choices[0].message.content
        return json.loads(raw_json)
        
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        raise
