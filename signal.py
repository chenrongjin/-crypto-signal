import requests
import pandas as pd
import requests

SEND_KEY = "SCT347411T9Z2D0Taq18lndnZQ0vGUjqgw"

def send_wechat(msg):
    url = f"https://sctapi.ftqq.com/{SEND_KEY}.send"
    data = {
        "title": "每日交易信号",
        "desp": msg
    }
    requests.post(url, data=data)
    
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

def get_klines(symbol):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1d",
        "limit": 100
    }

    r = requests.get(url, params=params)
    data = r.json()

    # ❗防止API错误
    if not isinstance(data, list):
        print(f"{symbol} API error:", data)
        return None

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","vol",
        "_","_","_","_","_","_"
    ])

    df["close"] = df["close"].astype(float)
    return df


def ma60(df):
    if df is None or len(df) < 60:
        return None
    return df["close"].rolling(60).mean().iloc[-1]


results = []

for s in SYMBOLS:
    df = get_klines(s)

    if df is None:
        continue

    price = df["close"].iloc[-1]
    ma = ma60(df)

    if ma is None:
        print(f"{s} 数据不足60根K线")
        continue

    deviation = (price - ma) / ma

    results.append({
        "symbol": s,
        "price": price,
        "ma": ma,
        "dev": deviation,
        "abs_dev": abs(deviation)
    })


if not results:
    print("没有有效数据")
else:
    best = sorted(results, key=lambda x: x["abs_dev"])[0]

    print("\n📊 MA60偏差分析\n")

    for r in results:
        print(f"{r['symbol']} | 价格:{r['price']:.2f} | MA60:{r['ma']:.2f} | 偏差:{r['dev']*100:.2f}%")

    print("\n🔥 推荐:")
    print(best["symbol"])

msg = f"推荐币种：{best['symbol']}\n偏差：{round(best['dev']*100,2)}%"
send_wechat(msg)
