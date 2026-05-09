import requests
import pandas as pd

SEND_KEY = "SCT347411T9Z2D0Taq18lndnZQ0vGUjqgw"

def send_wechat(msg):
    url = f"https://sctapi.ftqq.com/{SEND_KEY}.send"
    requests.post(url, data={"title": "信号", "desp": msg})


SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

def get_klines(symbol):
    try:
        url = "https://api.binance.com/api/v3/klines"
        r = requests.get(url, params={"symbol": symbol, "interval": "1d", "limit": 100}, timeout=10)
        data = r.json()

        if not isinstance(data, list):
            print(symbol, "API异常:", data)
            return None

        df = pd.DataFrame(data, columns=[
            "t","o","h","l","c","v","1","2","3","4","5","6"
        ])

        df["c"] = df["c"].astype(float)
        return df

    except Exception as e:
        print(symbol, "请求失败:", e)
        return None


def ma60(series):
    if len(series) < 60:
        return None
    return series.rolling(60).mean().iloc[-1]


results = []

for s in SYMBOLS:
    df = get_klines(s)

    if df is None:
        continue

    price = df["c"].iloc[-1]
    ma = ma60(df["c"])

    if ma is None:
        print(s, "数据不足60天")
        continue

    dev = (price - ma) / ma

    results.append((s, dev))


# 🧠 fallback（关键修复）
if len(results) == 0:
    msg = "API未返回有效数据（请检查Binance访问）"
    print(msg)
    send_wechat(msg)

else:
    best = min(results, key=lambda x: abs(x[1]))

    msg = f"推荐币种：{best[0]}\n偏差：{round(best[1]*100,2)}%"
    print(msg)
    send_wechat(msg)
