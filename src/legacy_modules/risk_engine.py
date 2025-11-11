"""
AI/ML Risk Prediction Engine
"""
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
import random

class RiskPredictionEngine:
    """
    Risk prediction engine using simple heuristics and ML concepts
    In production, this would use LSTM, Transformers, and ensemble models
    """
    
    def __init__(self):
        self.risk_factors = {
            "volatility": 0.3,
            "market_sentiment": 0.2,
            "liquidity": 0.2,
            "historical_performance": 0.15,
            "sector_risk": 0.15
        }
    
    def calculate_price_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility (standard deviation)"""
        if len(prices) < 2:
            return 0.0
        
        prices_array = np.array(prices)
        returns = np.diff(prices_array) / prices_array[:-1]
        volatility = np.std(returns)
        
        return min(volatility, 1.0)
    
    def predict_risk_score(self, investment_data: Dict) -> Dict:
        """
        Predict risk score for an investment
        Returns a risk score between 0 (low risk) and 1 (high risk)
        """
        # Simulate price history if not available
        current_price = investment_data.get('current_price', 100)
        purchase_price = investment_data.get('purchase_price', 100)
        
        # Calculate price change percentage
        price_change_pct = abs((current_price - purchase_price) / purchase_price)
        
        # Simulate volatility (in production, use historical data)
        volatility = min(price_change_pct * 2, 1.0)
        
        # Asset type risk factors
        asset_type_risk = {
            "stock": 0.5,
            "crypto": 0.8,
            "mutual_fund": 0.3,
            "bond": 0.2,
            "etf": 0.4
        }
        
        base_risk = asset_type_risk.get(
            investment_data.get('asset_type', 'stock').lower(), 
            0.5
        )
        
        # Calculate weighted risk score
        risk_score = (
            base_risk * 0.4 +
            volatility * 0.3 +
            (1 if price_change_pct > 0.2 else 0) * 0.3
        )
        
        # Normalize to 0-1 range
        risk_score = min(max(risk_score, 0.0), 1.0)
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
            color = "🔴"
        elif risk_score >= 0.4:
            risk_level = "medium"
            color = "🟡"
        else:
            risk_level = "low"
            color = "🟢"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_score, investment_data)
        
        return {
            "risk_score": round(risk_score, 3),
            "risk_level": risk_level,
            "risk_indicator": color,
            "volatility": round(volatility, 3),
            "recommendations": recommendations,
            "predicted_trend": self._predict_trend(investment_data)
        }
    
    def _generate_recommendations(self, risk_score: float, investment_data: Dict) -> List[str]:
        """Generate risk-based recommendations"""
        recommendations = []
        
        if risk_score >= 0.7:
            recommendations.extend([
                "⚠️ High risk detected. Consider reducing position size.",
                "📊 Set a stop-loss order to limit potential losses.",
                "🔍 Monitor this investment closely for the next 7 days."
            ])
        elif risk_score >= 0.4:
            recommendations.extend([
                "👀 Moderate risk. Keep a close watch on market conditions.",
                "💡 Consider diversifying your portfolio to reduce risk.",
                "📈 Review your investment strategy regularly."
            ])
        else:
            recommendations.extend([
                "✅ Low risk investment. Continue monitoring periodically.",
                "🎯 Good stability. Consider this as a portfolio anchor.",
                "📚 Use this as a learning opportunity for future investments."
            ])
        
        # Asset-specific recommendations
        asset_type = investment_data.get('asset_type', '').lower()
        if asset_type == 'crypto':
            recommendations.append("🔐 Crypto markets are volatile. Never invest more than you can afford to lose.")
        elif asset_type == 'stock':
            recommendations.append("📰 Stay updated with company news and earnings reports.")
        
        return recommendations
    
    def _predict_trend(self, investment_data: Dict) -> str:
        """Simple trend prediction"""
        current = investment_data.get('current_price', 100)
        purchase = investment_data.get('purchase_price', 100)
        
        change_pct = ((current - purchase) / purchase) * 100
        
        if change_pct > 5:
            return "📈 Upward trend"
        elif change_pct < -5:
            return "📉 Downward trend"
        else:
            return "➡️ Stable"
    
    def detect_anomaly(self, prices: List[float]) -> Dict:
        """Detect anomalies in price movements"""
        if len(prices) < 5:
            return {"anomaly_detected": False, "reason": "Insufficient data"}
        
        prices_array = np.array(prices)
        mean_price = np.mean(prices_array)
        std_price = np.std(prices_array)
        
        # Check if latest price is an outlier (> 2 standard deviations)
        latest_price = prices[-1]
        z_score = abs((latest_price - mean_price) / std_price) if std_price > 0 else 0
        
        if z_score > 2:
            return {
                "anomaly_detected": True,
                "reason": "Unusual price movement detected",
                "severity": "high" if z_score > 3 else "medium",
                "z_score": round(z_score, 2)
            }
        
        return {"anomaly_detected": False, "reason": "Normal price behavior"}

# Global instance
risk_engine = RiskPredictionEngine()
