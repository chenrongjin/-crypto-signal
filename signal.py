import requests
import pandas as pd

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

def get_klines(symbol):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1d",
        "limit": 100
    }
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","vol",
        "_","_","_","_","_","_"
    ])

    df["close"] = df["close"].astype(float)
    return df


def ma60(df):
    return df["close"].rolling(60).mean().iloc[-1]


results = []

for s in SYMBOLS:
    df = get_klines(s)

    price = df["close"].iloc[-1]
    ma = ma60(df)

    deviation = (price - ma) / ma

    results.append({
        "symbol": s,
        "price": price,
        "ma60": ma,
        "deviation": deviation,
        "abs_dev": abs(deviation)
    })


best = sorted(results, key=lambda x: x["abs_dev"])[0]

print("\n📊 MA60偏差分析\n")

for r in results:
    print(f"{r['symbol']} | 价格: {r['price']:.2f} | MA60: {r['ma60']:.2f} | 偏差: {r['deviation']*100:.2f}%")

print("\n🔥 推荐币种:")
print(best["symbol"], "偏差:", round(best["deviation"]*100, 2), "%")
