"""
Gemini AI Service for LLM-powered financial companion
"""
import google.generativeai as genai
from typing import Optional, Dict, List
import json
import logging
import sys
import os

# Add parent path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.config import settings

logger = logging.getLogger(__name__)

class GeminiFinancialCompanion:
    def __init__(self):
        logger.info("🤖 Initializing Gemini Financial Companion...")
        
        if not settings.GEMINI_API_KEY:
            logger.error("❌ GEMINI_API_KEY not set in environment variables")
            raise ValueError("GEMINI_API_KEY not set in environment variables")
        
        logger.info(f"✅ GEMINI_API_KEY found: {settings.GEMINI_API_KEY[:10]}...")
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"✅ Gemini model '{settings.GEMINI_MODEL}' initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
            raise
        
    async def explain_financial_term(self, term: str) -> str:
        """Explain financial jargon in simple terms"""
        logger.info(f"📚 Explaining term: {term}")
        
        prompt = f"""You are a friendly financial advisor explaining concepts to beginners.
        
Explain the following financial term in simple, everyday language that a first-time investor can understand:

Term: {term}

Provide a clear, concise explanation (2-3 sentences) without using complex jargon."""
        
        try:
            response = self.model.generate_content(prompt)
            logger.info(f"✅ Term explanation generated for: {term}")
            return response.text
        except Exception as e:
            logger.error(f"❌ Error explaining term '{term}': {str(e)}")
            raise
    
    async def analyze_investment_risk(self, investment_data: Dict) -> Dict:
        """Analyze investment risk using Gemini"""
        logger.info(f"📊 Analyzing investment risk for: {investment_data.get('symbol', 'N/A')}")
        
        prompt = f"""You are a financial risk analyst. Analyze the following investment and provide a risk assessment.

Investment Details:
- Symbol: {investment_data.get('symbol', 'N/A')}
- Asset Type: {investment_data.get('asset_type', 'N/A')}
- Purchase Price: ${investment_data.get('purchase_price', 0)}
- Current Price: ${investment_data.get('current_price', 0)}
- Quantity: {investment_data.get('quantity', 0)}

Provide your analysis in the following JSON format:
{{
    "risk_score": <float between 0 and 1>,
    "risk_level": "<low/medium/high>",
    "summary": "<brief risk summary>",
    "recommendations": ["<recommendation 1>", "<recommendation 2>"]
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            logger.info(f"✅ Risk analysis response received")
            
            # Extract JSON from response
            text = response.text.strip()
            logger.debug(f"Raw response: {text[:200]}...")
            
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(text)
            logger.info(f"✅ Risk analysis successful: {result.get('risk_level', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing risk: {str(e)}")
            # Fallback response
            return {
                "risk_score": 0.5,
                "risk_level": "medium",
                "summary": "Unable to analyze risk at this time",
                "recommendations": ["Monitor your investment regularly"],
                "error": str(e)
            }
    
    async def translate_to_simple_language(self, technical_text: str) -> str:
        """Convert technical financial language to simple terms"""
        prompt = f"""You are a financial translator. Convert the following technical financial text into simple, everyday language that a beginner investor can understand:

Technical Text: {technical_text}

Simple Explanation:"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    async def detect_scam_language(self, message: str) -> Dict:
        """Detect potential scam or phishing language"""
        logger.info(f"🔍 Detecting scam language in message: {message[:50]}...")
        
        prompt = f"""You are a fraud detection expert. Analyze the following message for signs of financial scams, phishing, or fraudulent schemes.

Message: {message}

Respond in JSON format:
{{
    "is_suspicious": <true/false>,
    "confidence": <float between 0 and 1>,
    "red_flags": ["<flag 1>", "<flag 2>"],
    "explanation": "<brief explanation>"
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            logger.info(f"✅ Scam detection response received")
            
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(text)
            logger.info(f"✅ Scam detection: {'⚠️ SUSPICIOUS' if result.get('is_suspicious') else '✅ Safe'}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error detecting scam: {str(e)}")
            return {
                "is_suspicious": False,
                "confidence": 0.0,
                "red_flags": [],
                "explanation": "Unable to analyze message",
                "error": str(e)
            }
    
    async def chat_with_user(self, user_query: str, context: Optional[Dict] = None) -> str:
        """Interactive chatbot for financial questions"""
        logger.info(f"💬 User chat: {user_query[:50]}...")
        
        context_str = ""
        if context:
            context_str = f"\nUser Context: {json.dumps(context, indent=2)}"
        
        prompt = f"""You are FinBuddy, a friendly and knowledgeable AI financial advisor for beginner investors. 
Your goal is to educate, protect, and empower users to make smart investment decisions.{context_str}

User Question: {user_query}

Provide a helpful, clear, and encouraging response. Keep it concise but informative."""
        
        try:
            response = self.model.generate_content(prompt)
            logger.info(f"✅ Chat response generated")
            return response.text
        except Exception as e:
            logger.error(f"❌ Error in chat: {str(e)}")
            raise
    
    async def generate_learning_content(self, topic: str, difficulty: str = "beginner") -> Dict:
        """Generate educational content for financial literacy"""
        prompt = f"""Create a {difficulty}-level educational module about: {topic}

Generate content in the following JSON format:
{{
    "title": "<module title>",
    "introduction": "<engaging introduction>",
    "key_points": ["<point 1>", "<point 2>", "<point 3>"],
    "example": "<real-world example>",
    "quiz_questions": [
        {{
            "question": "<question text>",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "<A/B/C/D>",
            "explanation": "<why this is correct>"
        }}
    ]
}}"""
        
        response = self.model.generate_content(prompt)
        try:
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except:
            return {
                "title": topic,
                "introduction": "Learn about " + topic,
                "key_points": ["Understanding the basics", "Practical applications", "Common mistakes"],
                "example": "Coming soon",
                "quiz_questions": []
            }
    
    async def summarize_document(self, document_text: str) -> str:
        """Summarize complex financial documents"""
        prompt = f"""Summarize the following financial document in simple terms for a beginner investor:

Document:
{document_text[:3000]}  

Provide a clear, concise summary highlighting the most important points."""
        
        response = self.model.generate_content(prompt)
        return response.text

# Global instance
gemini_companion = GeminiFinancialCompanion()
