import requests
import pandas as pd

SEND_KEY = "SCT347411T9Z2D0Taq18lndnZQ0vGUjqgw"

def send_wechat(msg):
    url = f"https://sctapi.ftqq.com/{SEND_KEY}.send"
    requests.post(url, data={"title": "信号", "desp": msg})


SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

def get_klines(symbol):

    url = "https://www.okx.com/api/v5/market/candles"

    params = {

        "instId": symbol.replace("USDT", "-USDT"),

        "bar": "1D",

        "limit": "100"

    }

    try:

        r = requests.get(url, params=params, timeout=10)

        data = r.json()

        # OKX结构检查

        if data.get("code") != "0":

            print(symbol, "API错误:", data)

            return None

        candles = data.get("data", [])

        if len(candles) == 0:

            print(symbol, "无数据")

            return None

        df = pd.DataFrame(candles)

        # OKX字段：

        # [ts,o,h,l,c,vol,...]

        df["close"] = df[4].astype(float)

        time.sleep(0.3)

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
