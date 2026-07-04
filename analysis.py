"""
中际旭创(300308.SZ) 技术指标分析脚本
1. 数据诊断分析（缺失值、描述性统计）
2. RSI / MACD / Bollinger Bands 计算
3. WorldQuant 101 Alpha#6 & Alpha#101 计算
4. 输出 JSON 供 HTML 可视化使用
"""
import csv
import json
import math
import statistics as stats

# ============ 1. 加载数据 ============
rows = []
with open("中际旭创_300308_日线数据.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

# 转换数值
fields_num = ["open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol", "amount"]
for r in rows:
    for k in fields_num:
        r[k] = float(r[k])

n = len(rows)
print(f"总交易日数: {n}")
print(f"日期范围: {rows[0]['trade_date']} ~ {rows[-1]['trade_date']}")

# ============ 2. 缺失值检查 ============
missing_report = {}
all_fields = ["ts_code", "trade_date"] + fields_num
for field in all_fields:
    count = sum(1 for r in rows if r.get(field) is None or r.get(field) == "" or r.get(field) == "nan")
    missing_report[field] = {"missing": count, "total": n, "missing_pct": round(count / n * 100, 2)}

print("\n=== 缺失值检查 ===")
for k, v in missing_report.items():
    status = "OK" if v["missing"] == 0 else f"缺失 {v['missing']} ({v['missing_pct']}%)"
    print(f"  {k}: {status}")

# ============ 3. 描述性统计 ============
desc_stats = {}
for field in ["open", "high", "low", "close", "vol", "amount", "pct_chg"]:
    vals = [r[field] for r in rows]
    desc_stats[field] = {
        "count": len(vals),
        "mean": round(stats.mean(vals), 4),
        "std": round(stats.stdev(vals), 4),
        "min": round(min(vals), 4),
        "max": round(max(vals), 4),
        "median": round(stats.median(vals), 4),
        "p25": round(stats.quantiles(vals, n=4)[0], 4) if len(vals) >= 4 else None,
        "p75": round(stats.quantiles(vals, n=4)[2], 4) if len(vals) >= 4 else None,
    }

print("\n=== 描述性统计 ===")
for field, s in desc_stats.items():
    print(f"  {field}: mean={s['mean']}, std={s['std']}, min={s['min']}, max={s['max']}, median={s['median']}")

# ============ 4. RSI 计算 (14日) ============
def calc_rsi(closes, period=14):
    """RSI = 100 - 100/(1 + RS), RS = avg_gain / avg_loss"""
    rsi = [None] * len(closes)
    gains = []
    losses = []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))

    # 第一个 RSI 值用简单平均
    avg_gain = stats.mean(gains[:period])
    avg_loss = stats.mean(losses[:period])
    for i in range(period, len(closes)):
        # Wilder 平滑法
        idx = i - 1  # gains/losses index offset by 1
        avg_gain = (avg_gain * (period - 1) + gains[idx]) / period
        avg_loss = (avg_loss * (period - 1) + losses[idx]) / period
        if avg_loss == 0:
            rsi[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[i] = round(100 - 100 / (1 + rs), 2)
    return rsi

closes = [r["close"] for r in rows]
rsi_values = calc_rsi(closes, 14)

# ============ 5. MACD 计算 (12, 26, 9) ============
def calc_ema(data, period):
    """指数移动平均"""
    ema = [None] * len(data)
    if len(data) < period:
        return ema
    # 初始 EMA = 前 period 个值的 SMA
    ema[period - 1] = stats.mean(data[:period])
    multiplier = 2 / (period + 1)
    for i in range(period, len(data)):
        ema[i] = data[i] * multiplier + ema[i - 1] * (1 - multiplier)
    return ema

ema12 = calc_ema(closes, 12)
ema26 = calc_ema(closes, 26)

dif = [None] * len(closes)  # DIF = EMA12 - EMA26
for i in range(len(closes)):
    if ema12[i] is not None and ema26[i] is not None:
        dif[i] = round(ema12[i] - ema26[i], 4)

# DEA = EMA(DIF, 9)
dif_valid = [v if v is not None else 0 for v in dif]
dea_raw = calc_ema(dif_valid, 9)
dea = [round(v, 4) if v is not None else None for v in dea_raw]

macd_hist = [None] * len(closes)  # MACD柱 = 2*(DIF-DEA)
for i in range(len(closes)):
    if dif[i] is not None and dea[i] is not None:
        macd_hist[i] = round(2 * (dif[i] - dea[i]), 4)

# ============ 6. 布林带计算 (20, 2) ============
def calc_bollinger(closes, period=20, num_std=2):
    upper = [None] * len(closes)
    middle = [None] * len(closes)
    lower = [None] * len(closes)
    for i in range(period - 1, len(closes)):
        window = closes[i - period + 1: i + 1]
        mid = stats.mean(window)
        std = stats.stdev(window)
        middle[i] = round(mid, 4)
        upper[i] = round(mid + num_std * std, 4)
        lower[i] = round(mid - num_std * std, 4)
    return upper, middle, lower

bb_upper, bb_middle, bb_lower = calc_bollinger(closes, 20, 2)

# ============ 7. WorldQuant Alpha#6 ============
# Alpha#6: -1 * correlation(Open, Volume, 10)
def calc_alpha6(opens, volumes, period=10):
    """滚动窗口内 open 与 volume 的相关系数取负"""
    alpha = [None] * len(opens)
    for i in range(period - 1, len(opens)):
        o = opens[i - period + 1: i + 1]
        v = volumes[i - period + 1: i + 1]
        n = period
        mean_o = sum(o) / n
        mean_v = sum(v) / n
        cov = sum((o[j] - mean_o) * (v[j] - mean_v) for j in range(n)) / (n - 1)
        std_o = math.sqrt(sum((x - mean_o) ** 2 for x in o) / (n - 1))
        std_v = math.sqrt(sum((x - mean_v) ** 2 for x in v) / (n - 1))
        if std_o == 0 or std_v == 0:
            alpha[i] = 0.0
        else:
            corr = cov / (std_o * std_v)
            alpha[i] = round(-1 * corr, 6)
    return alpha

opens = [r["open"] for r in rows]
volumes = [r["vol"] for r in rows]
alpha6 = calc_alpha6(opens, volumes, 10)

# ============ 8. WorldQuant Alpha#101 ============
# Alpha#101: ((Close - Open) / ((High - Low) + 0.001))
def calc_alpha101(opens, highs, lows, closes):
    alpha = [None] * len(closes)
    for i in range(len(closes)):
        hl_range = highs[i] - lows[i] + 0.001
        alpha[i] = round((closes[i] - opens[i]) / hl_range, 6)
    return alpha

highs = [r["high"] for r in rows]
lows = [r["low"] for r in rows]
alpha101 = calc_alpha101(opens, highs, lows, closes)

# ============ 9. 输出 JSON ============
dates = []
for r in rows:
    d = r["trade_date"]
    dates.append(f"{d[:4]}-{d[4:6]}-{d[6:]}")

output = {
    "meta": {
        "ts_code": "300308.SZ",
        "name": "中际旭创",
        "total_days": n,
        "date_start": dates[0],
        "date_end": dates[-1],
    },
    "stats": {
        "missing_report": missing_report,
        "descriptive": desc_stats,
    },
    "price": {
        "dates": dates,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "vol": volumes,
        "amount": [r["amount"] for r in rows],
        "pct_chg": [r["pct_chg"] for r in rows],
    },
    "indicators": {
        "rsi": {
            "period": 14,
            "values": rsi_values,
            "description": "RSI(14) 相对强弱指标",
        },
        "macd": {
            "params": {"fast": 12, "slow": 26, "signal": 9},
            "dif": dif,
            "dea": dea,
            "hist": macd_hist,
        },
        "bollinger": {
            "params": {"period": 20, "std": 2},
            "upper": bb_upper,
            "middle": bb_middle,
            "lower": bb_lower,
        },
        "alpha6": {
            "formula": "-1 * correlation(Open, Volume, 10)",
            "values": alpha6,
            "description": "WorldQuant Alpha#6: 开盘价与成交量的10日相关系数取负",
        },
        "alpha101": {
            "formula": "((Close - Open) / ((High - Low) + 0.001))",
            "values": alpha101,
            "description": "WorldQuant Alpha#101: 日内动量占日内振幅比例",
        },
    },
}

with open("analysis_output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False)

print("\n=== 输出文件 ===")
print("analysis_output.json 已生成")
print(f"RSI 有效值: {sum(1 for v in rsi_values if v is not None)}")
print(f"MACD DIF 有效值: {sum(1 for v in dif if v is not None)}")
print(f"布林带 有效值: {sum(1 for v in bb_upper if v is not None)}")
print(f"Alpha#6 有效值: {sum(1 for v in alpha6 if v is not None)}")
print(f"Alpha#101 有效值: {sum(1 for v in alpha101 if v is not None)}")
