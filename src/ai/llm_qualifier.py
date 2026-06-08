import os
import json
import logging
import litellm
from src.core.models import LeadQualification

logger = logging.getLogger(__name__)

async def qualify_lead(inquiry_text: str) -> LeadQualification:
    """
    Qualifies a lead using litellm and validates the structured output via Pydantic.
    """
    system_prompt = f"""
    You are a qualification engine for a financial advisory firm.
    Analyze the user's inquiry text. Extract the fields defined in this JSON schema:
    {json.dumps(LeadQualification.model_json_schema(), indent=2)}
    
    Output STRICTLY as a JSON object. No markdown formatting, no conversational text.
    """
    
    model = os.getenv("LLM_MODEL", "gpt-4o")
    api_key = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    api_base = os.getenv("LLM_API_BASE")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": inquiry_text}
    ]
    
    try:
        # We only pass response_format if the model supports it (like OpenAI)
        kwargs = {}
        if "gpt" in model or "openai" in model:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            api_key=api_key if api_key else None,
            api_base=api_base,
            temperature=0.1,
            **kwargs
        )
        
        raw_json = response.choices[0].message.content.strip()
        # Strip markdown code blocks if the model hallucinates them
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:-3].strip()
        elif raw_json.startswith("```"):
            raw_json = raw_json[3:-3].strip()
            
        return LeadQualification.model_validate_json(raw_json)
        
    except Exception as e:
        logger.error(f"LLM Qualification failed using {model}: {e}")
        raise
