import yfinance as yf
import ccxt
import pandas as pd
from ta.momentum import RSIIndicator
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import platform

# ================== 설정 ==================
RSI = 30
DAYS = 30  # RSI 윈도우 (30일)

# 한글 폰트 설정
system_name = platform.system()
if system_name == "Windows":
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif system_name == "Darwin":  # Mac
    plt.rcParams['font.family'] = 'AppleGothic'
else:  # Linux
    plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

YF_TICKERS = {
    "삼성전자": "005930.KS",
    "코스피": "^KS11",
    "나스닥": "^IXIC",
    "원/엔 환율": "KRWJPY=X",
    "원/달러 환율": "KRW=X",
    "VIX": "^VIX"
}
CRYPTO_SYMBOL = 'BTC/USDT'
exchange = ccxt.binance()

# ================== 데이터 함수 ==================
def get_rsi_from_yf(ticker):
    try:
        df = yf.download(
            ticker,
            period="3y",
            interval="1d",
            progress=False,
            auto_adjust=False
        )
        if len(df) < 15 or 'Close' not in df.columns:
            return None, None
        close_series = df['Close'].squeeze()
        rsi = RSIIndicator(close=close_series, window=DAYS).rsi()
        return rsi.iloc[-1], df
    except Exception as e:
        print(f"[ERROR] {ticker}: {e}")
        return None, None

def get_rsi_from_binance(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe="1d", limit=1100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        rsi = RSIIndicator(close=df['close'], window=DAYS).rsi()
        return rsi.iloc[-1], df
    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        return None, None

# ================== 유틸 함수 ==================
def notify(title, message):
    root = tk.Tk()
    root.withdraw()
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

def plot_all_rsi(data_dict, status_dict):
    n = len(data_dict)

    # 🔹 각 행의 높이를 3 → 1.8로 줄임
    fig, axes = plt.subplots(nrows=n, ncols=2, figsize=(13, 1.8*n))
    plt.style.use("seaborn-v0_8-darkgrid")

    vertical_lines = []

    def on_move(event):
        for line in vertical_lines:
            line.remove()
        vertical_lines.clear()
        if event.inaxes:
            for ax_row in axes:
                for ax in ax_row:
                    line = ax.axvline(event.xdata, color='gray', linestyle='--', linewidth=0.8)
                    vertical_lines.append(line)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect('motion_notify_event', on_move)

    for i, (name, df) in enumerate(data_dict.items()):
        if df is None or len(df) < 15:
            continue

        close_series = df['Close'] if 'Close' in df.columns else df['close']
        close_series = close_series.squeeze()
        rsi = RSIIndicator(close=close_series, window=DAYS).rsi()

        state = status_dict.get(name)
        if state == '과매도':
            color_price = "red"
            color_rsi = "red"
            state_color = "red"
            highlight = (0.95, 0.8, 0.8, 0.3)
        elif state == '과매수':
            color_price = "green"
            color_rsi = "green"
            state_color = "green"
            highlight = (0.8, 0.95, 0.8, 0.3)
        else:
            color_price = "navy"
            color_rsi = "orange"
            state_color = "gray"
            highlight = None

        # ----------- 종가 차트 -----------
        ax1 = axes[i, 0]
        ax1.plot(df.index, close_series, color=color_price, linewidth=1.1, label="종가")
        ax1.set_title(f"{name} 종가", fontsize=9, fontweight="bold")
        if highlight:
            ax1.axvspan(df.index[-30], df.index[-1], color=highlight)

        current_price = close_series.iloc[-1]
        ax1.text(1.02, 0.8, f"{current_price:.0f}" if current_price > 1 else f"{current_price:.2f}",
                 transform=ax1.transAxes, fontsize=9, fontweight="bold",
                 color=color_price, ha="left", va="center")

        ax1.text(1.02, 0.5, state if state else "정상",
                 transform=ax1.transAxes, fontsize=9, fontweight="bold",
                 color=state_color, ha="left", va="center", fontname='Malgun Gothic')
        ax1.legend(fontsize=7, loc="upper left")

        # ----------- RSI 차트 -----------
        ax2 = axes[i, 1]
        ax2.plot(df.index, rsi, color=color_rsi, linewidth=1.1, label="RSI")
        ax2.axhline(30, color="red", linestyle="--", linewidth=0.8)
        ax2.axhline(70, color="green", linestyle="--", linewidth=0.8)
        ax2.fill_between(df.index, 0, 30, color="red", alpha=0.05)
        ax2.fill_between(df.index, 70, 100, color="green", alpha=0.05)
        last_rsi = rsi.iloc[-1]
        ax2.scatter(df.index[-1], last_rsi, color=color_rsi, zorder=5, s=20)
        if highlight:
            ax2.axvspan(df.index[-30], df.index[-1], color=highlight)
        ax2.set_ylim(0, 100)
        ax2.set_title(f"{name} RSI", fontsize=9, fontweight="bold")
        ax2.legend(fontsize=7, loc="upper left")
        ax2.text(1.02, 0.65, f"RSI {last_rsi:.1f}",
                 transform=ax2.transAxes, fontsize=9, fontweight="bold",
                 color=color_rsi, ha="left", va="center")

    # 🔹 여백 최소화
    plt.subplots_adjust(hspace=0.25, wspace=0.25)
    plt.tight_layout(pad=2)
    plt.show()

# ================== 메인 ==================
def main():
    print("📡 RSI 체크 시작")

    results = {}
    status_dict = {}  # 각 자산의 RSI 상태 저장

    # 야후 파이낸스 종목
    for name, ticker in YF_TICKERS.items():
        rsi, df = get_rsi_from_yf(ticker)
        print(f"{name} RSI: {rsi:.2f}" if rsi else f"{name}: RSI 계산 실패")
        status = rsi_status(rsi)
        results[name] = df
        status_dict[name] = status

    # 비트코인
    btc_rsi, btc_df = get_rsi_from_binance(CRYPTO_SYMBOL)
    print(f"비트코인 RSI: {btc_rsi:.2f}" if btc_rsi else "비트코인: RSI 계산 실패")
    status_dict["비트코인"] = rsi_status(btc_rsi)
    results["비트코인"] = btc_df

    # RSI 상태별 색 표시 포함
    plot_all_rsi(results, status_dict)
    print("✅ 체크 완료. 프로그램 종료")

# ================== 그래프 함수 수정 ==================
def plot_all_rsi(data_dict, status_dict):
    n = len(data_dict)
    fig, axes = plt.subplots(nrows=n, ncols=2, figsize=(14, 3*n))
    plt.style.use("seaborn-v0_8-darkgrid")

    vertical_lines = []

    def on_move(event):
        for line in vertical_lines:
            line.remove()
        vertical_lines.clear()

        if event.inaxes:
            for ax_row in axes:
                for ax in ax_row:
                    line = ax.axvline(event.xdata, color='gray', linestyle='--', linewidth=0.8)
                    vertical_lines.append(line)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect('motion_notify_event', on_move)

    for i, (name, df) in enumerate(data_dict.items()):
        if df is None or len(df) < 15:
            continue

        close_series = df['Close'] if 'Close' in df.columns else df['close']
        close_series = close_series.squeeze()
        rsi = RSIIndicator(close=close_series, window=DAYS).rsi()

        # RSI 상태별 스타일
        state = status_dict.get(name)
        if state == '과매도':
            color_price = "red"
            color_rsi = "red"
            state_color = "red"
            highlight = (0.95, 0.8, 0.8, 0.3)
        elif state == '과매수':
            color_price = "green"
            color_rsi = "green"
            state_color = "green"
            highlight = (0.8, 0.95, 0.8, 0.3)
        else:
            color_price = "navy"
            color_rsi = "orange"
            state_color = "gray"
            highlight = None

        # ----------- 종가 차트 -----------
        ax1 = axes[i, 0]
        ax1.plot(df.index, close_series, color=color_price, linewidth=1.3, label="종가")
        ax1.set_title(f"{name} 종가", fontsize=10, fontweight="bold")

        if highlight:
            ax1.axvspan(df.index[-30], df.index[-1], color=highlight)

        # 현재가 표시
        current_price = close_series.iloc[-1]
        ax1.text(1.02, 0.8, f"{current_price:.0f}" if current_price > 1 else f"{current_price:.2f}",
                 transform=ax1.transAxes, fontsize=10, fontweight="bold",
                 color=color_price, ha="left", va="center")

        # RSI 상태 텍스트 표시 (옆에)
        if state:
            ax1.text(1.02, 0.5, state, transform=ax1.transAxes,
                     fontsize=11, fontweight="bold", color=state_color,
                     ha="left", va="center", fontname='Malgun Gothic')
        else:
            ax1.text(1.02, 0.5, "정상", transform=ax1.transAxes,
                     fontsize=10, fontweight="bold", color="gray",
                     ha="left", va="center", fontname='Malgun Gothic')

        ax1.legend(fontsize=8, loc="upper left")

        # ----------- RSI 차트 -----------
        ax2 = axes[i, 1]
        ax2.plot(df.index, rsi, color=color_rsi, linewidth=1.3, label="RSI")
        ax2.axhline(30, color="red", linestyle="--", linewidth=0.8)
        ax2.axhline(70, color="green", linestyle="--", linewidth=0.8)
        ax2.fill_between(df.index, 0, 30, color="red", alpha=0.05)
        ax2.fill_between(df.index, 70, 100, color="green", alpha=0.05)
        last_rsi = rsi.iloc[-1]
        ax2.scatter(df.index[-1], last_rsi, color=color_rsi, zorder=5, s=25)
        if highlight:
            ax2.axvspan(df.index[-30], df.index[-1], color=highlight)
        ax2.set_ylim(0, 100)
        ax2.set_title(f"{name} RSI", fontsize=10, fontweight="bold")
        ax2.legend(fontsize=8, loc="upper left")

        # RSI 수치와 상태 표시
        ax2.text(1.02, 0.7, f"RSI {last_rsi:.1f}",
                 transform=ax2.transAxes, fontsize=10, fontweight="bold",
                 color=color_rsi, ha="left", va="center")
        if state:
            ax2.text(1.02, 0.5, state, transform=ax2.transAxes,
                     fontsize=11, fontweight="bold", color=state_color,
                     ha="left", va="center", fontname='Malgun Gothic')

    plt.tight_layout(pad=5)
    plt.show()
if __name__ == "__main__":
    main()
