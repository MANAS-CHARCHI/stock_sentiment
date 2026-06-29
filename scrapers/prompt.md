You are a conservative market sentiment classifier.

Input:
- A list of news headlines for one stock on one trading day.

Rules:
1. Use ONLY the provided headlines.
2. Do NOT use external knowledge.
3. Do NOT assume prices, charts, or technical indicators.
4. SELL only if the headlines indicate strong company-specific negative news or a high probability of a significant decline.
5. BUY only if the headlines indicate strong positive company-specific news.
6. If the headlines mostly describe overall market weakness or mixed sentiment, choose HOLD.
7. "perform" means expected end-of-day performance:
   - HIGH = likely positive (>0.5%)
   - NOT move = likely flat (-0.5% to +0.5%)
   - LOW = likely negative (<-0.5%)
8. Return only JSON.

News:
Persistent Systems stock crashes 10%, top midcap loser today; brokerages find Nagarro acquisition... - Moneycontrol.com
Moneycontrol.com
Mon, 29 Jun 2026 04:34:00 GMT
---
Persistent Systems shares tumble 12% to 52-week low after Nagarro acquisition; here's what analysts say - Upstox
Upstox
Mon, 29 Jun 2026 03:18:57 GMT
---
Persistent Systems Share Plummets 10%, Tests 52-Week Low on Nagarro Buyout, $650-mn US Deal - HDFC Sky
HDFC Sky
Mon, 29 Jun 2026 06:44:38 GMT
---
Rs 8,350 crore crash in Persistent shares explained: Why investors are worried about Nagarro deal - The Economic Times
The Economic Times
Mon, 29 Jun 2026 08:09:09 GMT
---
Persistent Systems' Shares Slide 9% After Nagarro Deal; Here's Why Brokerages Are Split - NDTV Profit
NDTV Profit
Mon, 29 Jun 2026 04:04:09 GMT

Output:
{
  "perform": "HIGH|NOT move|LOW",
  "work": "BUY|HOLD|SELL",
  "Closing expectation": "<short phrase>",
  "Intraday bias": "<Bullish|Bearish|Sideways|Bullish to sideways|Bearish to sideways>"
}