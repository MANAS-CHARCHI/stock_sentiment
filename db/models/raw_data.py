from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base

class RedditPost(Base):
    __tablename__ = "reddit_posts"

    id             = Column(Integer, primary_key=True)
    stock_id       = Column(Integer, ForeignKey("watched_stocks.id"), nullable=False)
    post_id        = Column(String(20), unique=True, nullable=False)
    title          = Column(Text)
    content        = Column(Text)
    author         = Column(String(100))
    upvotes        = Column(Integer, default=0)
    num_comments   = Column(Integer, default=0)
    subreddit      = Column(String(100))
    post_url       = Column(Text)
    published_at   = Column(DateTime)
    collected_date = Column(Date, nullable=False)
    created_at     = Column(DateTime, server_default=func.now())

    stock = relationship("WatchedStock", back_populates="reddit_posts")
    
    
class NewsArticle(Base):
    __tablename__ = "news_articles"

    id             = Column(Integer, primary_key=True)
    stock_id       = Column(Integer, ForeignKey("watched_stocks.id"), nullable=False)
    source         = Column(String(50))
    title          = Column(Text)
    content        = Column(Text)
    author         = Column(String(100))
    article_url    = Column(Text)
    published_at   = Column(DateTime)
    collected_date = Column(Date, nullable=False)
    created_at     = Column(DateTime, server_default=func.now())

    stock = relationship("WatchedStock", back_populates="news_articles")

class YFSummary(Base):
    __tablename__ = "yf_summaries"

    id             = Column(Integer, primary_key=True)
    stock_id       = Column(Integer, ForeignKey("watched_stocks.id"), nullable=False)
    title          = Column(Text)
    summary        = Column(Text)
    pub_date       = Column(Date, nullable=False)
    created_at     = Column(DateTime, server_default=func.now())

    stock = relationship("WatchedStock", back_populates="yf_summaries")