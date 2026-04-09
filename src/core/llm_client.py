import os
from google import genai
from pydantic import BaseModel
from typing import Type, Tuple
from src.core.prompts import SYSTEM_PROMPT

def analyze_provisioning_request(prompt: str, response_schema: Type[BaseModel]) -> Tuple[BaseModel, dict]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")
    
    # Initialize the client naturally allowing the SDK to pick the correct v1beta/v1 endpoint
    client = genai.Client(api_key=api_key)
    
    # Use gemini-2.5-flash (Default stable model fully supporting structured payloads)
    model_id = 'gemini-2.5-flash'
    
    # Call GenerateContent with structured outputs using the explicit types configuration class
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
        ),
    )
    
    # FinOps metrics via usage_metadata extraction
    prompt_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
    candidate_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0
    
    # Gemini Pricing (Sample): $0.35/1M input, $1.05/1M output
    cost_input = (prompt_tokens / 1_000_000) * 0.35
    cost_output = (candidate_tokens / 1_000_000) * 1.05
    total_cost = cost_input + cost_output
    
    finops_data = {
        "prompt_tokens": prompt_tokens,
        "candidate_tokens": candidate_tokens,
        "cost_input_usd": cost_input,
        "cost_output_usd": cost_output,
        "total_cost_usd": total_cost
    }
    
    # Construct the Pydantic model
    result_obj = response_schema.model_validate_json(response.text)
    
    return result_obj, finops_data