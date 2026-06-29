from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class AgentResult(Base):
    __tablename__ = "agent_results"

    id            = Column(Integer, primary_key=True)
    stock_id      = Column(Integer, ForeignKey("watched_stocks.id"), nullable=False)
    agent         = Column(String(50), nullable=False)   # reddit_agent, news_agent
    analysis_date = Column(Date, nullable=False)
    score         = Column(Float)
    summary       = Column(Text)
    top_theme     = Column(Text)
    buzz_level    = Column(String(10))                   # LOW, MEDIUM, HIGH
    result_json   = Column(JSON)
    created_at    = Column(DateTime, server_default=func.now())

    stock = relationship("WatchedStock", back_populates="agent_results")


class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    id              = Column(Integer, primary_key=True)
    stock_id        = Column(Integer, ForeignKey("watched_stocks.id"), nullable=False)
    analysis_date   = Column(Date, nullable=False)
    verdict         = Column(String(10))                 # BUY, SELL, HOLD
    score           = Column(Float)
    confidence      = Column(String(10))                 # HIGH, MEDIUM, LOW
    reason          = Column(Text)
    alerts          = Column(JSON)
    reddit_score    = Column(Float)
    news_score      = Column(Float)
    risk_flag       = Column(Text)
    rolling_summary = Column(Text)
    created_at      = Column(DateTime, server_default=func.now())

    stock = relationship("WatchedStock", back_populates="sentiment_results")


class AccuracyTracking(Base):
    __tablename__ = "accuracy_tracking"

    id                = Column(Integer, primary_key=True)
    stock_id          = Column(Integer, ForeignKey("watched_stocks.id"), nullable=False)
    analysis_date     = Column(Date, nullable=False)
    verdict           = Column(String(10))
    price_at_analysis = Column(Float)
    price_next_day    = Column(Float)
    price_change_pct  = Column(Float)
    was_correct       = Column(Boolean)
    created_at        = Column(DateTime, server_default=func.now())

    stock = relationship("WatchedStock", back_populates="accuracy_tracking")