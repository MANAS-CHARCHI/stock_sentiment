from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from db.database import Base
from sqlalchemy.orm import relationship

class AllNSEStocks(Base):
    __tablename__ = "all_nse_stocks"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    symbol = Column(String(20), nullable=False)
    date_of_listing= Column(DateTime, nullable=False)
    isin_number= Column(String(20), nullable=False)
    face_value= Column(Integer, nullable=False)

    watched_by = relationship("WatchedStock", back_populates="master_stock")
    analyst_recommendations = relationship("AnalystRecommendation", back_populates="all_nse_stock")


class WatchedStock(Base):
    __tablename__ = "watched_stocks"
    
    id          = Column(Integer, primary_key=True)
    master_stock_id = Column(Integer, ForeignKey("all_nse_stocks.id"), nullable=True)
    ticker      = Column(String(20), unique=True, nullable=False)
    exchange    = Column(String(10), nullable=False)
    name        = Column(String(100), nullable=False)
    short_name  = Column(String(50))
    country     = Column(String(5))
    industry    = Column(String(100))
    description = Column(Text)
    added_at    = Column(DateTime, server_default=func.now())
    active      = Column(Boolean, nullable=False, default=True)
    
    master_stock      = relationship("AllNSEStocks", back_populates="watched_by")
    reddit_posts      = relationship("RedditPost", back_populates="stock")
    news_articles     = relationship("NewsArticle", back_populates="stock")
    agent_results     = relationship("AgentResult", back_populates="stock")
    sentiment_results = relationship("SentimentResult", back_populates="stock")
    accuracy_tracking = relationship("AccuracyTracking", back_populates="stock")
    yf_summaries      = relationship("YFSummary", back_populates="stock")
    stock_history     = relationship("StockHistory", back_populates="stock")
    stock_analytics_info = relationship("StocksAnalyticsInfo", back_populates="stock")
    