from openai import OpenAI
from pydantic import BaseModel, Field
from models import ProjectAnalysis

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

def analyze_project_with_ai(title: str, description: str) -> ProjectAnalysis:
    prompt = (
        f"Analyze the following SaaS project and respond STRICTLY in valid JSON matching the requested fields."
        f"(category: string, complexity_score: integer, suggested_tags: array of strings(3 to 5), summary: string).\n\n"
        f"Title: {title}\n"
        f"Description: {description}"
    )
    
    response = client.chat.completions.create(
        model="llama3.2",  
        messages=[
            {"role": "system", "content": "You are an expert software architect. You always output valid JSON objects."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    
    content = response.choices[0].message.content
    
    return ProjectAnalysis.model_validate_json(content)