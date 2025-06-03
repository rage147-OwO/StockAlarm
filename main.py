import yfinance as yf
import ccxt
import pandas as pd
from ta.momentum import RSIIndicator
import tkinter as tk
from tkinter import messagebox

RSI = 30
DAYS = 10
#pyinstaller --onefile --noconsole --add-binary "C:/Users/lim/miniconda3/envs/builder/Library/bin/libcrypto-1_1-x64.dll;." --add-binary "C:/Users/lim/miniconda3/envs/builder/Library/bin/libssl-1_1-x64.dll;." main.py

# 감시할 종목들
YF_TICKERS = {
    "삼성전자": "005930.KS",
    "코스피": "^KS11",
    "나스닥": "^IXIC",
    "원/엔 환율": "KRWJPY=X",
    "원/달러 환율": "KRW=X"
}
CRYPTO_SYMBOL = 'BTC/USDT'
exchange = ccxt.binance()

def get_rsi_from_yf(ticker):
    try:
        df = yf.download(ticker, period='7d', interval='1h', progress=False, auto_adjust=False)
        if len(df) < 15 or 'Close' not in df.columns:
            return None
        close_series = df['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.squeeze()
        rsi = RSIIndicator(close=close_series, window=DAYS).rsi()
        return rsi.iloc[-1]
    except Exception as e:
        print(f"[ERROR] {ticker}: {e}")
        return None

def get_rsi_from_binance(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        rsi = RSIIndicator(close=df['close'], window=DAYS).rsi()
        return rsi.iloc[-1]
    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        return None

def notify(title, message):
    root = tk.Tk()
    root.withdraw()  # GUI 창 숨김
    messagebox.showinfo(title, message)
    root.destroy()

def rsi_status(rsi):
    if rsi is None:
        return None
    if rsi < RSI:
        return '과매도'
    elif rsi > (100 - RSI):
        return '과매수'
    return None

def main():
    print("📡 RSI 알림 시작")

    # 야후 파이낸스 종목
    for name, ticker in YF_TICKERS.items():
        rsi = get_rsi_from_yf(ticker)
        print(f"{name} RSI: {rsi:.2f}" if rsi else f"{name}: RSI 계산 실패")
        status = rsi_status(rsi)
        if status:
            notify(f"{name} RSI {status} 경고", f"{status} 상태입니다! (RSI: {rsi:.2f})")

    # 비트코인
    btc_rsi = get_rsi_from_binance(CRYPTO_SYMBOL)
    print(f"비트코인 RSI: {btc_rsi:.2f}" if btc_rsi else "비트코인: RSI 계산 실패")
    status = rsi_status(btc_rsi)
    if status:
        notify(f"비트코인 RSI {status} 경고", f"{status} 상태입니다! (RSI: {btc_rsi:.2f})")

    print("✅ 체크 완료. 프로그램 종료")

if __name__ == "__main__":
    main()

