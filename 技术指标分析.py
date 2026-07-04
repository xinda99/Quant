# -*- coding: utf-8 -*-
"""
中际旭创(300308.SZ) 技术指标分析 — Jupyter Notebook 版
逐 Cell 运行即可复现全部结果

依赖: pip install pandas matplotlib tushare
"""

# ============================================================
# Cell 1: 导入依赖
# ============================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# A股配色: 红涨绿跌
COLOR_UP = '#e74c3c'
COLOR_DOWN = '#27ae60'

print("依赖加载完成")

# ============================================================
# Cell 2: 加载CSV数据 & 数据诊断
# ============================================================
df = pd.read_csv('中际旭创_300308_日线数据.csv', encoding='utf-8-sig')
df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
df = df.sort_values('trade_date').reset_index(drop=True)

print(f"数据形状: {df.shape}")
print(f"日期范围: {df['trade_date'].iloc[0].date()} ~ {df['trade_date'].iloc[-1].date()}")
print(f"\n=== 缺失值检查 ===")
print(df.isnull().sum())
print(f"\n=== 描述性统计 ===")
print(df[['open','high','low','close','vol','amount','pct_chg']].describe().round(2))

# ============================================================
# Cell 3: 计算 RSI (14日)
# ============================================================
def calc_rsi(close, period=14):
    """RSI 相对强弱指标
    公式: RSI = 100 - 100/(1+RS)
    RS = N日内平均涨幅 / N日内平均跌幅
    使用 Wilder 平滑法
    """
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Wilder 平滑
    for i in range(period, len(close)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period-1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period-1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - 100 / (1 + rs)
    return rsi

df['RSI'] = calc_rsi(df['close'], 14)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
ax1.plot(df['trade_date'], df['close'], color='#2c3e50', linewidth=1.2, label='收盘价')
ax1.set_title('中际旭创(300308.SZ) 收盘价', fontsize=14)
ax1.set_ylabel('价格(元)')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(df['trade_date'], df['RSI'], color='#8e44ad', linewidth=1, label='RSI(14)')
ax2.axhline(70, color=COLOR_DOWN, linestyle='--', alpha=0.5, label='超买线(70)')
ax2.axhline(30, color=COLOR_UP, linestyle='--', alpha=0.5, label='超卖线(30)')
ax2.axhline(50, color='gray', linestyle=':', alpha=0.3)
ax2.fill_between(df['trade_date'], 70, 100, alpha=0.08, color=COLOR_DOWN)
ax2.fill_between(df['trade_date'], 0, 30, alpha=0.08, color=COLOR_UP)
ax2.set_title('RSI(14) 相对强弱指标', fontsize=12)
ax2.set_ylabel('RSI')
ax2.set_ylim(0, 100)
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('rsi_chart.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# Cell 4: 计算 MACD (12, 26, 9)
# ============================================================
def calc_macd(close, fast=12, slow=26, signal=9):
    """MACD 指数平滑异同移动平均线
    DIF = EMA(fast) - EMA(slow)
    DEA = EMA(DIF, signal)
    MACD柱 = 2 * (DIF - DEA)
    """
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    hist = 2 * (dif - dea)
    return dif, dea, hist

df['DIF'], df['DEA'], df['MACD_hist'] = calc_macd(df['close'], 12, 26, 9)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
ax1.plot(df['trade_date'], df['close'], color='#2c3e50', linewidth=1.2, label='收盘价')
ax1.set_title('中际旭创(300308.SZ) 收盘价', fontsize=14)
ax1.set_ylabel('价格(元)')
ax1.legend()
ax1.grid(True, alpha=0.3)

colors_hist = [COLOR_UP if v >= 0 else COLOR_DOWN for v in df['MACD_hist']]
ax2.bar(df['trade_date'], df['MACD_hist'], color=colors_hist, width=1, alpha=0.6, label='MACD柱')
ax2.plot(df['trade_date'], df['DIF'], color='#e67e22', linewidth=1, label='DIF')
ax2.plot(df['trade_date'], df['DEA'], color='#3498db', linewidth=1, label='DEA')
ax2.axhline(0, color='gray', linewidth=0.5)
ax2.set_title('MACD(12,26,9) 指数平滑异同移动平均线', fontsize=12)
ax2.set_ylabel('MACD')
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('macd_chart.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# Cell 5: 计算布林带 (20, 2)
# ============================================================
def calc_bollinger(close, period=20, num_std=2):
    """布林带
    中轨 = SMA(close, period)
    上轨 = 中轨 + num_std * std
    下轨 = 中轨 - num_std * std
    """
    middle = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower

df['BB_upper'], df['BB_middle'], df['BB_lower'] = calc_bollinger(df['close'], 20, 2)

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df['trade_date'], df['close'], color='#2c3e50', linewidth=1.2, label='收盘价', zorder=3)
ax.plot(df['trade_date'], df['BB_upper'], color='#e74c3c', linewidth=1, label='上轨(2σ)', alpha=0.7)
ax.plot(df['trade_date'], df['BB_middle'], color='#f39c12', linewidth=1, label='中轨(SMA20)', alpha=0.7, linestyle='--')
ax.plot(df['trade_date'], df['BB_lower'], color='#27ae60', linewidth=1, label='下轨(2σ)', alpha=0.7)
ax.fill_between(df['trade_date'], df['BB_upper'], df['BB_lower'], alpha=0.08, color='#3498db')
ax.set_title('布林带 Bollinger Bands (20, 2) — 中际旭创(300308.SZ)', fontsize=14)
ax.set_ylabel('价格(元)')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('bollinger_chart.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# Cell 6: WorldQuant Alpha#6
# ============================================================
# Alpha#6: -1 * correlation(Open, Volume, 10)
# 含义: 衡量开盘价与成交量在10日窗口内的负相关性
# 若价升量增（正相关），alpha为负 → 可能预示反转
def calc_alpha6(open_, volume, period=10):
    """滚动窗口计算 open 与 volume 的相关系数取负"""
    corr = open_.rolling(window=period).corr(volume)
    return -1 * corr

df['Alpha6'] = calc_alpha6(df['open'], df['vol'], 10)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
ax1.plot(df['trade_date'], df['close'], color='#2c3e50', linewidth=1.2, label='收盘价')
ax1.set_title('中际旭创(300308.SZ) 收盘价', fontsize=14)
ax1.set_ylabel('价格(元)')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(df['trade_date'], df['Alpha6'], color='#9b59b6', linewidth=1, label='Alpha#6')
ax2.axhline(0, color='gray', linewidth=0.5)
ax2.set_title('WorldQuant Alpha#6: -1 * Correlation(Open, Volume, 10)', fontsize=12)
ax2.set_ylabel('Alpha值')
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('alpha6_chart.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# Cell 7: WorldQuant Alpha#101
# ============================================================
# Alpha#101: ((Close - Open) / ((High - Low) + 0.001))
# 含义: 日内动量占日内振幅的比例
# 值域 [-1, 1]，正值=收盘高于开盘（多头动量），负值=空头动量
def calc_alpha101(open_, high, low, close):
    hl_range = (high - low) + 0.001
    return (close - open_) / hl_range

df['Alpha101'] = calc_alpha101(df['open'], df['high'], df['low'], df['close'])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
ax1.plot(df['trade_date'], df['close'], color='#2c3e50', linewidth=1.2, label='收盘价')
ax1.set_title('中际旭创(300308.SZ) 收盘价', fontsize=14)
ax1.set_ylabel('价格(元)')
ax1.legend()
ax1.grid(True, alpha=0.3)

colors_a101 = [COLOR_UP if v >= 0 else COLOR_DOWN for v in df['Alpha101']]
ax2.bar(df['trade_date'], df['Alpha101'], color=colors_a101, width=1, alpha=0.6, label='Alpha#101')
ax2.axhline(0, color='gray', linewidth=0.5)
ax2.set_title('WorldQuant Alpha#101: (Close-Open)/((High-Low)+0.001)', fontsize=12)
ax2.set_ylabel('Alpha值')
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('alpha101_chart.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# Cell 8: 综合指标汇总表
# ============================================================
indicator_summary = pd.DataFrame({
    '指标': ['RSI(14)', 'MACD DIF', 'MACD DEA', 'MACD柱', 'BB上轨', 'BB中轨', 'BB下轨', 'Alpha#6', 'Alpha#101'],
    '最新值': [
        round(df['RSI'].iloc[-1], 2),
        round(df['DIF'].iloc[-1], 2),
        round(df['DEA'].iloc[-1], 2),
        round(df['MACD_hist'].iloc[-1], 2),
        round(df['BB_upper'].iloc[-1], 2),
        round(df['BB_middle'].iloc[-1], 2),
        round(df['BB_lower'].iloc[-1], 2),
        round(df['Alpha6'].iloc[-1], 4),
        round(df['Alpha101'].iloc[-1], 4),
    ],
    '含义': [
        '>70超买, <30超卖',
        '快慢线差值, >0多头',
        'DIF的信号线',
        '柱状图, 红正绿负',
        '压力位(2σ上方)',
        '20日均线中轨',
        '支撑位(2σ下方)',
        '负相关因子',
        '日内动量/振幅',
    ],
})
print("=== 指标最新值汇总 ===")
print(indicator_summary.to_string(index=False))

# 保存带指标的完整数据
df.to_csv('中际旭创_300308_含指标.csv', index=False, encoding='utf-8-sig')
print("\n已保存: 中际旭创_300308_含指标.csv")
