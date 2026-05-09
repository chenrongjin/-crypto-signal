import requests
import pandas as pd

SEND_KEY = "SCT347411T9Z2D0Taq18lndnZQ0vGUjqgw"

def send_wechat(msg):
    try:
        url = f"https://sctapi.ftqq.com/{SEND_KEY}.send"
        data = {
            "title": "每日交易信号",
            "desp": msg
        }
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("微信发送失败:", e)


SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

def get_klines(symbol):
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": "1d", "limit": 100}

        data = requests.get(url, params=params, timeout=10).json()

        if not isinstance(data, list):
            print(symbol, "API error:", data)
            return None

        df = pd.DataFrame(data)
        df["close"] = df[4].astype(float)
        return df

    except Exception as e:
        print(symbol, "请求失败:", e)
        return None


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
        print(s, "数据不足60根")
        continue

    dev = (price - ma) / ma

    results.append({
        "symbol": s,
        "price": price,
        "ma": ma,
        "dev": dev,
        "abs": abs(dev)
    })

# ❗关键：防止空数据崩溃
if len(results) == 0:
    msg = "没有有效数据，无法生成信号"
    print(msg)
    send_wechat(msg)

else:
    best = sorted(results, key=lambda x: x["abs"])[0]

    print("\n📊 MA60偏差分析\n")

    for r in results:
        print(f"{r['symbol']} | 价格:{r['price']:.2f} | MA60:{r['ma']:.2f} | 偏差:{r['dev']*100:.2f}%")

    msg = f"推荐币种：{best['symbol']}\n偏差：{round(best['dev']*100,2)}%"

    print("\n🔥 推送内容:")
    print(msg)

    send_wechat(msg)
