from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class WatchedStock(Base):
    __tablename__ = "watched_stocks"
    
    id          = Column(Integer, primary_key=True)
    ticker      = Column(String(20), unique=True, nullable=False)
    exchange    = Column(String(10), nullable=False)
    name        = Column(String(100), nullable=False)
    short_name  = Column(String(50))
    country     = Column(String(5))
    industry    = Column(String(100))
    description = Column(Text)
    added_at    = Column(DateTime, server_default=func.now())
    
    reddit_posts      = relationship("RedditPost", back_populates="stock")
    news_articles     = relationship("NewsArticle", back_populates="stock")
    agent_results     = relationship("AgentResult", back_populates="stock")
    sentiment_results = relationship("SentimentResult", back_populates="stock")
    accuracy_tracking = relationship("AccuracyTracking", back_populates="stock")