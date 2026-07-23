from pydantic import BaseModel
from typing import Optional, List

class AIChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[str] = None
    use_knowledge: bool = True
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    model: Optional[str] = None

class AIChatResponse(BaseModel):
    response: str
    conversation_id: str
    model_used: str
    confidence: float
    sources: List[dict] = []
    prompt_tokens: int = 0
    completion_tokens: int = 0

class AIConfigUpdate(BaseModel):
    ai_model: Optional[str] = None
    ai_temperature: Optional[float] = None
    ai_max_tokens: Optional[int] = None
    ai_system_prompt: Optional[str] = None
    ai_knowledge_enabled: Optional[bool] = None
    ai_safety_rules: Optional[dict] = None
