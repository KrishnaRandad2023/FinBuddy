"""
Fraud & Scam Detection Engine
"""
from typing import Dict, List
import re

class FraudDetectionEngine:
    """
    Fraud and scam detection using NLP and pattern matching
    """
    
    def __init__(self):
        # Common scam keywords and phrases
        self.scam_keywords = [
            "guaranteed returns", "risk-free", "get rich quick",
            "limited time offer", "act now", "secret system",
            "double your money", "free money", "no risk",
            "urgent", "wire transfer", "send money now",
            "investment opportunity of a lifetime", "exclusive offer",
            "congratulations you've won", "verify your account",
            "suspended account", "click here immediately",
            "tax refund", "inheritance", "lottery winner"
        ]
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'\b\d{16}\b',  # Credit card numbers
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'password\s*[:=]\s*\S+',  # Password requests
            r'pin\s*[:=]\s*\d+',  # PIN requests
        ]
        
        # Known scam domains (simplified)
        self.blacklisted_domains = [
            "scamsite.com", "fakebank.net", "phishing-alert.org"
        ]
    
    def analyze_message(self, message: str, sender: str = "") -> Dict:
        """
        Analyze a message for scam indicators
        """
        message_lower = message.lower()
        
        # Check for scam keywords
        detected_keywords = [
            keyword for keyword in self.scam_keywords 
            if keyword in message_lower
        ]
        
        # Check for suspicious patterns
        suspicious_patterns_found = []
        for pattern in self.suspicious_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                suspicious_patterns_found.append(pattern)
        
        # Check for urgency indicators
        urgency_words = ["urgent", "immediately", "now", "hurry", "limited time"]
        urgency_count = sum(1 for word in urgency_words if word in message_lower)
        
        # Check for money requests
        money_requests = any(phrase in message_lower for phrase in [
            "send money", "wire transfer", "payment required", 
            "update payment", "verify payment"
        ])
        
        # Calculate risk score
        risk_score = 0.0
        risk_factors = []
        
        if detected_keywords:
            risk_score += len(detected_keywords) * 0.15
            risk_factors.append(f"Found {len(detected_keywords)} scam keywords")
        
        if suspicious_patterns_found:
            risk_score += len(suspicious_patterns_found) * 0.25
            risk_factors.append("Suspicious data patterns detected")
        
        if urgency_count >= 2:
            risk_score += 0.2
            risk_factors.append("High urgency language")
        
        if money_requests:
            risk_score += 0.3
            risk_factors.append("Direct money request")
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        # Determine alert level
        if risk_score >= 0.7:
            alert_level = "critical"
            recommendation = "🚨 DANGER: This message shows multiple scam indicators. Do NOT respond or send money."
        elif risk_score >= 0.4:
            alert_level = "high"
            recommendation = "⚠️ WARNING: This message is suspicious. Verify the sender's identity before taking action."
        elif risk_score >= 0.2:
            alert_level = "medium"
            recommendation = "⚡ CAUTION: Be careful. This message has some red flags."
        else:
            alert_level = "low"
            recommendation = "✅ This message appears safe, but always stay vigilant."
        
        return {
            "is_suspicious": risk_score >= 0.4,
            "risk_score": round(risk_score, 3),
            "alert_level": alert_level,
            "detected_keywords": detected_keywords[:5],  # Top 5
            "risk_factors": risk_factors,
            "recommendation": recommendation,
            "should_block": risk_score >= 0.7
        }
    
    def analyze_url(self, url: str) -> Dict:
        """
        Analyze a URL for phishing indicators
        """
        url_lower = url.lower()
        
        risk_score = 0.0
        risk_factors = []
        
        # Check for blacklisted domains
        for domain in self.blacklisted_domains:
            if domain in url_lower:
                risk_score += 0.8
                risk_factors.append(f"Blacklisted domain: {domain}")
        
        # Check for suspicious URL patterns
        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
            risk_score += 0.3
            risk_factors.append("IP address instead of domain name")
        
        # Check for common phishing patterns
        phishing_patterns = ["secure-", "verify-", "account-update", "login-"]
        for pattern in phishing_patterns:
            if pattern in url_lower:
                risk_score += 0.2
                risk_factors.append(f"Suspicious URL pattern: {pattern}")
        
        # Check for excessive subdomains
        subdomain_count = url.split("//")[-1].split("/")[0].count(".")
        if subdomain_count > 3:
            risk_score += 0.2
            risk_factors.append("Excessive subdomains")
        
        risk_score = min(risk_score, 1.0)
        
        return {
            "is_safe": risk_score < 0.4,
            "risk_score": round(risk_score, 3),
            "risk_factors": risk_factors,
            "recommendation": "Do not click" if risk_score >= 0.4 else "Appears safe, but verify"
        }
    
    def check_transaction_anomaly(self, transaction_data: Dict, user_history: List[Dict]) -> Dict:
        """
        Check for anomalous transaction behavior
        """
        amount = transaction_data.get('amount', 0)
        
        if not user_history:
            return {
                "is_anomalous": False,
                "reason": "No historical data available"
            }
        
        # Calculate average transaction amount
        historical_amounts = [t.get('amount', 0) for t in user_history]
        avg_amount = sum(historical_amounts) / len(historical_amounts) if historical_amounts else 0
        
        # Check if transaction is significantly larger
        if amount > avg_amount * 3 and amount > 1000:
            return {
                "is_anomalous": True,
                "reason": "Transaction amount is unusually high",
                "severity": "high",
                "recommendation": "Verify this transaction carefully before proceeding"
            }
        
        # Check for rapid successive transactions
        # (In production, check timestamps)
        if len(user_history) > 0 and "timestamp" in transaction_data:
            # Simplified check
            pass
        
        return {
            "is_anomalous": False,
            "reason": "Transaction appears normal"
        }

# Global instance
fraud_detector = FraudDetectionEngine()
