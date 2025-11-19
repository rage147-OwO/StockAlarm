import fear_and_greed
from datetime import datetime
import tkinter as tk
import winsound

# 기준점
BUY_THRESHOLD = 5
SELL_THRESHOLD = 95

# 현재 지수 가져오기
fg = fear_and_greed.get()
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
value = fg.value
status = fg.description

# 신호 판단
if value <= BUY_THRESHOLD:
    signal = "매수 신호 (극단적 공포)"
    alert_needed = True
elif value >= SELL_THRESHOLD:
    signal = "매도 신호 (극단적 탐욕)"
    alert_needed = True
else:
    signal = "관망 / 보유 유지"
    alert_needed = False

# 조건 충족 시만 팝업 + 사운드
if alert_needed:
    message = f"[{now}]\n현재 Fear & Greed Index: {value:.2f}\n상태: {status}\n신호: {signal}"
    
    # 사운드 알람 (1000Hz, 0.5초)
    winsound.Beep(1000, 500)
    
    # Tkinter 팝업 창
    root = tk.Tk()
    root.withdraw()  # 메인 윈도우 숨김
    
    popup = tk.Toplevel(root)
    popup.title("Fear & Greed Index 모니터")
    popup.geometry("350x130")
    popup.resizable(False, False)
    
    label = tk.Label(popup, text=message, justify="left", padx=10, pady=10)
    label.pack()
    
    btn = tk.Button(popup, text="닫기", command=root.destroy)
    btn.pack(pady=10)
    
    root.mainloop()
