"""
Shared database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.utils.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    risk_tolerance = Column(String, default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Investment(Base):
    __tablename__ = "investments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    symbol = Column(String, index=True)
    asset_type = Column(String)
    quantity = Column(Float)
    purchase_price = Column(Float)
    current_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RiskAlert(Base):
    __tablename__ = "risk_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    investment_id = Column(Integer, nullable=True)
    risk_score = Column(Float)
    risk_level = Column(String)
    alert_message = Column(Text)
    human_readable_message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class FraudAlert(Base):
    __tablename__ = "fraud_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    alert_type = Column(String)
    description = Column(Text)
    severity = Column(String)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    module_name = Column(String)
    completion_percentage = Column(Float, default=0.0)
    quiz_score = Column(Float, nullable=True)
    last_accessed = Column(DateTime, default=datetime.utcnow)

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text)
    url = Column(String, unique=True, nullable=False, index=True)
    published_at = Column(DateTime, index=True)
    source = Column(String, nullable=True, index=True)
    content = Column(Text)
    sentiment = Column(String)
    sentiment_score = Column(Integer, default=0)
    fetched_at = Column(DateTime, default=datetime.utcnow)

class RecommendationOutcome(Base):
    __tablename__ = "recommendation_outcomes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    recommendation_type = Column(String)  # 'ai_recommendations' or 'portfolio_simulation'
    followed = Column(Boolean, default=False)  # Did user implement the recommendation?
    outcome = Column(String, nullable=True)  # 'positive', 'negative', 'neutral', 'pending'
    initial_portfolio_value = Column(Float, nullable=True)
    final_portfolio_value = Column(Float, nullable=True)
    percentage_change = Column(Float, nullable=True)
    recommendation_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime, nullable=True)  # When outcome was determined
