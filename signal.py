import requests
import pandas as pd
import time

# ===== 微信推送 =====
SEND_KEY = "SCT347411T9Z2D0Taq18lndnZQ0vGUjqgw"

def send_wechat(msg):
    try:
        url = f"https://sctapi.ftqq.com/{SEND_KEY}.send"
        requests.post(url, data={
            "title": "每日交易信号",
            "desp": msg
        }, timeout=10)
    except Exception as e:
        print("微信发送失败:", e)


# ===== 币种 =====
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]


# ===== OKX获取K线 =====
def get_klines(symbol):
    try:
        url = "https://www.okx.com/api/v5/market/candles"

        instId = symbol.replace("USDT", "-USDT")

        params = {
            "instId": instId,
            "bar": "1D",
            "limit": "100"
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()

        if data.get("code") != "0":
            print(symbol, "API错误:", data)
            return None

        candles = data.get("data", [])
        if not candles:
            print(symbol, "无数据")
            return None

        candles = candles[::-1]

        df = pd.DataFrame(candles)
        df = df.iloc[:, :5]
        df.columns = ["ts", "open", "high", "low", "close"]

        df["close"] = df["close"].astype(float)

        time.sleep(0.2)

        return df

    except Exception as e:
        print(symbol, "请求失败:", e)
        return None


# ===== MA60 =====
def ma60(df):
    if df is None or len(df) < 60:
        return None
    return df["close"].rolling(60).mean().iloc[-1]


# ===== 主逻辑 =====
results = []

for s in SYMBOLS:
    df = get_klines(s)

    if df is None:
        continue

    price = df["close"].iloc[-1]
    ma = ma60(df)

    if ma is None:
        print(s, "数据不足60根K线")
        continue

    dev = (price - ma) / ma

    results.append({
        "symbol": s,
        "price": price,
        "ma": ma,
        "dev": dev,
        "abs": abs(dev)
    })


# ===== 防崩处理 =====
if len(results) == 0:
    msg = "⚠️ 没有获取到有效数据"
    print(msg)
    send_wechat(msg)

else:
    results = sorted(results, key=lambda x: x["abs"])
    best = results[0]

    msg = "📊 MA60交易信号\n\n"

    print("\n📊 MA60分析结果\n")

    for r in results:
        line = (
            f"{r['symbol']} | "
            f"价格:{r['price']:.2f} | "
            f"MA60:{r['ma']:.2f} | "
            f"偏差:{r['dev']*100:.2f}%"
        )
        print(line)
        msg += line + "\n"

    msg += f"\n🔥 推荐买入：{best['symbol']}\n"
    msg += f"偏差最小：{best['dev']*100:.2f}%"

    print("\n" + msg)

    send_wechat(msg)
