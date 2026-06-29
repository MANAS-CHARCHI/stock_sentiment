from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Date
from db.database import Base
from sqlalchemy.orm import relationship

class AnalystRecommendation(Base):
    __tablename__ = "analyst_recommendations"

    id = Column(Integer, primary_key=True)
    all_nse_stock_id = Column(Integer, ForeignKey("all_nse_stocks.id", ondelete="CASCADE"), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    strong_buy  = Column(Integer, default=0)
    buy         = Column(Integer, default=0)
    hold        = Column(Integer, default=0)
    sell        = Column(Integer, default=0)
    strong_sell = Column(Integer, default=0)

    all_nse_stock = relationship("AllNSEStocks", back_populates="analyst_recommendations")

class StockHistory(Base):
    __tablename__ = "stock_history"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("watched_stocks.id", ondelete="CASCADE"), nullable=False)
    snapshot_date = Column(DateTime, nullable=False)
    open = Column(Integer)
    high = Column(Integer)
    low = Column(Integer)
    close = Column(Integer)
    volume = Column(Integer)
    dividends = Column(Integer)
    stock_splits = Column(Integer)

    stock = relationship("WatchedStock", back_populates="stock_history")

class StocksAnalyticsInfo(Base):
    __tablename__ = "stocks_analytics_info"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("watched_stocks.id", ondelete="CASCADE"), nullable=False)

    dividend_yield = Column(Integer)
    dividend_rate = Column(Integer)
    dividend_time = Column(DateTime)

    marketCap = Column(Integer)
    trailingPE = Column(Integer)
    priceToBook = Column(Integer)
    fiftyTwoWeekHigh = Column(Integer)
    fiftyTwoWeekLow = Column(Integer)
    fiftyDayAverage = Column(Integer)
    twoHundredDayAverage = Column(Integer)

    currentPrice = Column(Integer)
    high52Week = Column(Integer)
    low52Week = Column(Integer)
    mean = Column(Integer)
    median = Column(Integer)


    stock = relationship("WatchedStock", back_populates="stock_analytics_info")
    