import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
import matplotlib.pyplot as plt

RSI = 30
DAYS = 10
ticker = "BTC-USD"
df = yf.download(ticker, period='2y', interval='1d', progress=False)

close_series = df['Close']
if isinstance(close_series, pd.DataFrame):
    close_series = close_series.squeeze()

rsi = RSIIndicator(close=close_series, window=DAYS).rsi()

oversold_count = (rsi <= 100-RSI).sum()
overbought_count = (rsi >= RSI).sum()

print(f"BTC-USD RSI(50) 30 이하인 날: {oversold_count}일")
print(f"BTC-USD RSI(50) 70 이상인 날: {overbought_count}일")

plt.figure(figsize=(12,6))
plt.plot(df.index, rsi, label='RSI (window=50)')
plt.axhline(RSI, color='red', linestyle='--', label='RSI 30 (Oversold)')
plt.axhline(100-RSI, color='green', linestyle='--', label='RSI 70 (Overbought)')
plt.title('비트코인 RSI(50) 최근 2년 (일봉)')
plt.legend()
plt.show()
