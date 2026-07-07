from sqlalchemy import Column, Integer, Float, BigInteger, String, DateTime, ForeignKey, UniqueConstraint, Date, Text, func
from db.database import Base
from sqlalchemy.orm import relationship


class AnalystRecommendation(Base):
    __tablename__ = "analyst_recommendations"

    id = Column(Integer, primary_key=True)
    all_nse_stock_id = Column(
        Integer,
        ForeignKey("all_nse_stocks.id", ondelete="CASCADE"),
        nullable=False,
    )
    snapshot_date = Column(Date, nullable=False)

    strong_buy = Column(Integer, default=0)
    buy = Column(Integer, default=0)
    hold = Column(Integer, default=0)
    sell = Column(Integer, default=0)
    strong_sell = Column(Integer, default=0)

    all_nse_stock = relationship(
        "AllNSEStocks",
        back_populates="analyst_recommendations",
    )


class StockHistory(Base):
    __tablename__ = "stock_history"

    id = Column(Integer, primary_key=True)
    stock_id = Column(
        Integer,
        ForeignKey("watched_stocks.id", ondelete="CASCADE"),
        nullable=False,
    )

    snapshot_date = Column(Date, nullable=False)

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

    volume = Column(BigInteger)

    dividends = Column(Float)
    stock_splits = Column(Float)

    stock = relationship(
        "WatchedStock",
        back_populates="stock_history",
    )


class StocksAnalyticsInfo(Base):
    __tablename__ = "stocks_analytics_info"

    id = Column(Integer, primary_key=True)
    stock_id = Column(
        Integer,
        ForeignKey("watched_stocks.id", ondelete="CASCADE"),
        nullable=False,
    )

    dividend_yield = Column(Float)
    dividend_rate = Column(Float)
    dividend_time = Column(DateTime)

    marketCap = Column(BigInteger)
    trailingPE = Column(Float)
    priceToBook = Column(Float)
    high52Week = Column(Float)
    low52Week = Column(Float)
    fiftyDayAverage = Column(Float)
    twoHundredDayAverage = Column(Float)

    currentPrice = Column(Float)
    mean = Column(Float)
    median = Column(Float)

    fiftyDayAverage = Column(Float)
    twoHundredDayAverage = Column(Float)

    currentPrice = Column(Float)
    high52Week = Column(Float)
    low52Week = Column(Float)

    mean = Column(Float)
    median = Column(Float)

    stock = relationship(
        "WatchedStock",
        back_populates="stock_analytics_info",
    )