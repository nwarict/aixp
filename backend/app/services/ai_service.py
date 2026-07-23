import httpx
import json
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.config import get_settings

settings = get_settings()

class AIService:
    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.default_model = settings.default_ai_model
        self.fallback_provider = settings.fallback_ai_provider
        self.openai_key = settings.openai_api_key

    async def chat(
        self,
        message: str,
        tenant_id: str,
        conversation_id: Optional[str] = None,
        context: Optional[str] = None,
        use_knowledge: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict:
        """Process chat message with AI."""

        # Use tenant-specific model or default
        ai_model = model or self.default_model

        # Build system prompt
        system_prompt = await self._get_system_prompt(tenant_id, db)

        # Get relevant knowledge if enabled
        knowledge_context = ""
        if use_knowledge and db:
            knowledge_context = await self._search_knowledge(message, tenant_id, db)

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        if knowledge_context:
            messages.append({"role": "system", "content": f"Relevant knowledge: {knowledge_context}"})

        if context:
            messages.append({"role": "system", "content": f"Conversation context: {context}"})

        # Add conversation history
        if conversation_id and db:
            history = await self._get_conversation_history(conversation_id, db)
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        # Try Ollama first
        try:
            response = await self._call_ollama(messages, ai_model, temperature, max_tokens)
            return {
                "response": response["content"],
                "model_used": ai_model,
                "confidence": 0.9,
                "sources": [],
                "prompt_tokens": response.get("prompt_eval_count", 0),
                "completion_tokens": response.get("eval_count", 0)
            }
        except Exception as e:
            # Fallback to OpenAI if configured
            if self.fallback_provider == "openai" and self.openai_key:
                return await self._call_openai(messages, temperature, max_tokens)
            raise Exception(f"AI service error: {str(e)}")

    async def _call_ollama(self, messages: List[Dict], model: str, temperature: float, max_tokens: int) -> Dict:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["message"]["content"],
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "eval_count": data.get("eval_count", 0)
            }

    async def _call_openai(self, messages: List[Dict], temperature: float, max_tokens: int) -> Dict:
        import openai
        client = openai.AsyncOpenAI(api_key=self.openai_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return {
            "response": response.choices[0].message.content,
            "model_used": "gpt-3.5-turbo",
            "confidence": 0.95,
            "sources": [],
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens
        }

    async def _get_system_prompt(self, tenant_id: str, db: Optional[AsyncSession]) -> str:
        if db:
            from app.models.tenant import Tenant
            result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = result.scalar_one_or_none()
            if tenant and tenant.ai_system_prompt:
                return tenant.ai_system_prompt
        return "You are a helpful AI customer service assistant. Respond in the same language as the user. Be concise and professional."

    async def _search_knowledge(self, query: str, tenant_id: str, db: AsyncSession) -> str:
        """Search knowledge base using PostgreSQL full-text search."""
        result = await db.execute(
            text("""
                SELECT title, content 
                FROM knowledge_base 
                WHERE tenant_id = :tenant_id 
                AND is_published = true
                AND to_tsvector('simple', content) @@ plainto_tsquery('simple', :query)
                ORDER BY ts_rank(to_tsvector('simple', content), plainto_tsquery('simple', :query)) DESC
                LIMIT 3
            """),
            {"tenant_id": tenant_id, "query": query}
        )
        results = result.fetchall()
        if results:
            return "\n\n".join([f"{r[0]}: {r[1][:500]}" for r in results])
        return ""

    async def _get_conversation_history(self, conversation_id: str, db: AsyncSession) -> List[Dict]:
        from app.models.message import Message
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(10)
        )
        messages = result.scalars().all()
        history = []
        for msg in reversed(messages):
            role = "user" if msg.sender_type == "customer" else "assistant"
            history.append({"role": role, "content": msg.content})
        return history

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate text embedding using Ollama."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.ollama_host}/api/embeddings",
                json={"model": self.default_model, "prompt": text}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])

    async def score_lead(self, lead_data: dict) -> Dict:
        """AI-powered lead scoring."""
        prompt = f"""Analyze this lead and provide a score (0-100) and insights:
        Title: {lead_data.get('title', '')}
        Description: {lead_data.get('description', '')}
        Source: {lead_data.get('source', '')}
        Value: {lead_data.get('value', 0)}

        Respond in JSON format: {{"score": number, "insights": "string", "recommendations": ["string"]}}"""

        try:
            result = await self.chat(
                message=prompt,
                tenant_id=lead_data.get('tenant_id', 'default'),
                use_knowledge=False,
                temperature=0.3,
                max_tokens=500
            )
            import re
            json_match = re.search(r'\{.*\}', result['response'], re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {"score": 50, "insights": "Unable to analyze", "recommendations": []}

    async def summarize_conversation(self, messages: List[str]) -> str:
        """Generate conversation summary."""
        text = "\n".join(messages)
        prompt = f"Summarize this customer conversation in 2-3 sentences:\n\n{text}"

        try:
            result = await self.chat(
                message=prompt,
                tenant_id="default",
                use_knowledge=False,
                temperature=0.5,
                max_tokens=200
            )
            return result['response']
        except:
            return "Summary unavailable"
