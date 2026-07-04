# -*- coding: utf-8 -*-
"""
中际旭创(300308) 量化分析脚本
包含：数据诊断、RSI/MACD/布林带计算与可视化、WorldQuant101因子计算
"""

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. 数据加载与诊断分析
# ============================================================

def load_data(filepath):
    """加载股价数据"""
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    # 转换日期格式
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df = df.sort_values('trade_date').reset_index(drop=True)
    return df

def data_diagnostics(df):
    """数据诊断分析：缺失值检查与描述性统计"""
    print("=" * 60)
    print("【数据诊断分析报告】")
    print("=" * 60)

    print(f"\n数据时间范围: {df['trade_date'].min().strftime('%Y-%m-%d')} ~ {df['trade_date'].max().strftime('%Y-%m-%d')}")
    print(f"总交易日数: {len(df)}")
    print(f"数据列: {list(df.columns)}")

    # 缺失值检查
    print("\n--- 缺失值检查 ---")
    missing = df.isnull().sum()
    missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
    missing_report = pd.DataFrame({
        '缺失数量': missing,
        '缺失比例(%)': missing_pct
    })
    print(missing_report.to_string())
    total_missing = missing.sum()
    print(f"\n总缺失值数量: {total_missing}")
    if total_missing == 0:
        print("结论: 数据完整，无缺失值。")

    # 描述性统计
    print("\n--- 描述性统计量 ---")
    numeric_cols = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
    desc = df[numeric_cols].describe().round(4)
    print(desc.to_string())

    # 额外统计量
    print("\n--- 额外统计量 ---")
    for col in ['close', 'vol', 'pct_chg']:
        print(f"\n[{col}]")
        print(f"  偏度(Skewness): {df[col].skew():.4f}")
        print(f"  峰度(Kurtosis): {df[col].kurtosis():.4f}")
        print(f"  变异系数(CV): {(df[col].std() / df[col].mean() * 100):.2f}%")

    return desc

# ============================================================
# 2. 技术指标计算
# ============================================================

def calc_rsi(close, period=14):
    """
    RSI (相对强弱指数)
    计算方法：
      1. 计算每日价格变动 delta = close - pre_close
      2. 分离上涨(gain)和下跌(loss)
      3. 计算period内的平均上涨幅度(AvgGain)和平均下跌幅度(AvgLoss)
         使用Wilder平滑法: AvgGain = (前日AvgGain*(period-1) + 今日Gain) / period
      4. RS = AvgGain / AvgLoss
      5. RSI = 100 - 100/(1+RS)
    作用：衡量价格超买超卖程度，RSI>70超买，RSI<30超卖
    """
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calc_macd(close, fast=12, slow=26, signal=9):
    """
    MACD (指数平滑异同移动平均线)
    计算方法：
      1. DIF(快线) = EMA(close, fast) - EMA(close, slow)
      2. DEA(信号线) = EMA(DIF, signal)
      3. MACD柱 = 2 * (DIF - DEA)
    作用：判断趋势方向和动量，DIF上穿DEA为金叉(买入)，下穿为死叉(卖出)
    """
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd_hist = 2 * (dif - dea)
    return dif, dea, macd_hist

def calc_bollinger(close, window=20, num_std=2):
    """
    布林带 (Bollinger Bands)
    计算方法：
      1. 中轨(MID) = SMA(close, window)
      2. 标准差(STD) = close在window期内的标准差
      3. 上轨(UPPER) = MID + num_std * STD
      4. 下轨(LOWER) = MID - num_std * STD
    作用：衡量价格波动率和相对位置，触及上轨超买，触及下轨超卖
    """
    mid = close.rolling(window=window).mean()
    std = close.rolling(window=window).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    bandwidth = (upper - lower) / mid * 100  # 带宽
    pct_b = (close - lower) / (upper - lower) * 100  # %B指标
    return mid, upper, lower, bandwidth, pct_b

# ============================================================
# 3. WorldQuant 101 Alpha 因子
# ============================================================

def calc_alpha_12(df):
    """
    Alpha#12: sign(delta(volume, 1)) * (-1 * delta(close, 1))

    计算方法：
      1. delta(volume, 1) = 今日成交量 - 昨日成交量
      2. sign() 取符号 (+1, 0, -1)
      3. delta(close, 1) = 今日收盘价 - 昨日收盘价
      4. Alpha = sign(成交量变化) * (-1 * 收盘价变化)

    作用：量价背离因子。当放量上涨时alpha为负（看空），
         缩量下跌时alpha为正（看多），捕捉量价关系异常。
    """
    delta_vol = df['vol'].diff(1)
    delta_close = df['close'].diff(1)
    alpha = np.sign(delta_vol) * (-1 * delta_close)
    return alpha

def calc_alpha_101(df):
    """
    Alpha#101: ((close - open) / ((high - low) + .001))

    计算方法：
      1. close - open = 当日涨跌幅（绝对值）
      2. high - low = 当日振幅
      3. Alpha = 涨跌幅 / (振幅 + 0.001)

    作用：日内价格位置因子。衡量收盘价在当日价格区间中的相对位置。
         值接近1表示收盘接近最高点（强势），接近-1表示收盘接近最低点（弱势）。
         0.001用于避免除零。
    """
    alpha = (df['close'] - df['open']) / ((df['high'] - df['low']) + 0.001)
    return alpha

# ============================================================
# 4. 可视化
# ============================================================

def setup_chinese_font():
    """设置中文字体"""
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

def plot_price_with_bollinger(df, mid, upper, lower, savepath):
    """绘制股价与布林带"""
    setup_chinese_font()
    fig, axes = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [3, 1]})

    # 上图：股价 + 布林带
    ax1 = axes[0]
    ax1.plot(df['trade_date'], df['close'], color='#333333', linewidth=1.2, label='收盘价')
    ax1.plot(df['trade_date'], mid, color='#FF6600', linewidth=1, label='BOLL中轨', linestyle='--')
    ax1.plot(df['trade_date'], upper, color='#FF4444', linewidth=1, label='BOLL上轨', linestyle='--')
    ax1.plot(df['trade_date'], lower, color='#00AA00', linewidth=1, label='BOLL下轨', linestyle='--')
    ax1.fill_between(df['trade_date'], lower, upper, alpha=0.08, color='#4488CC')
    ax1.set_title('中际旭创(300308) 股价与布林带(Bollinger Bands)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('价格 (元)', fontsize=11)
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)

    # 下图：%B指标
    ax2 = axes[1]
    pct_b = (df['close'] - lower) / (upper - lower) * 100
    ax2.plot(df['trade_date'], pct_b, color='#4488CC', linewidth=1)
    ax2.axhline(y=100, color='#FF4444', linestyle='--', alpha=0.5, label='上轨(100)')
    ax2.axhline(y=50, color='#888888', linestyle='--', alpha=0.5, label='中轨(50)')
    ax2.axhline(y=0, color='#00AA00', linestyle='--', alpha=0.5, label='下轨(0)')
    ax2.fill_between(df['trade_date'], pct_b, 50, where=(pct_b > 50), alpha=0.2, color='#FF4444')
    ax2.fill_between(df['trade_date'], pct_b, 50, where=(pct_b < 50), alpha=0.2, color='#00AA00')
    ax2.set_ylabel('%B', fontsize=11)
    ax2.set_xlabel('日期', fontsize=11)
    ax2.legend(loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(savepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [已保存] {savepath}")

def plot_rsi(df, rsi, savepath):
    """绘制RSI"""
    setup_chinese_font()
    fig, ax = plt.subplots(figsize=(16, 5))
    ax.plot(df['trade_date'], rsi, color='#9933CC', linewidth=1.2, label='RSI(14)')
    ax.axhline(y=70, color='#FF4444', linestyle='--', alpha=0.6, label='超买线(70)')
    ax.axhline(y=50, color='#888888', linestyle=':', alpha=0.4, label='中线(50)')
    ax.axhline(y=30, color='#00AA00', linestyle='--', alpha=0.6, label='超卖线(30)')
    ax.fill_between(df['trade_date'], rsi, 70, where=(rsi > 70), alpha=0.2, color='#FF4444')
    ax.fill_between(df['trade_date'], rsi, 30, where=(rsi < 30), alpha=0.2, color='#00AA00')
    ax.set_title('中际旭创(300308) RSI 相对强弱指数', fontsize=14, fontweight='bold')
    ax.set_ylabel('RSI', fontsize=11)
    ax.set_xlabel('日期', fontsize=11)
    ax.set_ylim(0, 100)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(savepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [已保存] {savepath}")

def plot_macd(df, dif, dea, macd_hist, savepath):
    """绘制MACD"""
    setup_chinese_font()
    fig, ax = plt.subplots(figsize=(16, 6))
    # MACD柱状图（中国惯例：红涨绿跌）
    colors = ['#FF4444' if v >= 0 else '#00AA00' for v in macd_hist]
    ax.bar(df['trade_date'], macd_hist, color=colors, alpha=0.6, width=1.5, label='MACD柱')
    ax.plot(df['trade_date'], dif, color='#FF6600', linewidth=1.2, label='DIF(快线)')
    ax.plot(df['trade_date'], dea, color='#0066CC', linewidth=1.2, label='DEA(信号线)')
    ax.axhline(y=0, color='#333333', linewidth=0.5)
    ax.set_title('中际旭创(300308) MACD 指数平滑异同移动平均线', fontsize=14, fontweight='bold')
    ax.set_ylabel('MACD', fontsize=11)
    ax.set_xlabel('日期', fontsize=11)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(savepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [已保存] {savepath}")

def plot_wq101(df, alpha12, alpha101, savepath):
    """绘制WorldQuant 101 Alpha因子"""
    setup_chinese_font()
    fig, axes = plt.subplots(2, 1, figsize=(16, 9))

    # Alpha#12
    ax1 = axes[0]
    colors12 = ['#FF4444' if v >= 0 else '#00AA00' for v in alpha12]
    ax1.bar(df['trade_date'], alpha12, color=colors12, alpha=0.6, width=1.5)
    ax1.axhline(y=0, color='#333333', linewidth=0.5)
    ax1.set_title('WorldQuant Alpha#12: sign(delta(volume,1)) * (-1 * delta(close,1))', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Alpha值', fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Alpha#101
    ax2 = axes[1]
    ax2.plot(df['trade_date'], alpha101, color='#4488CC', linewidth=1.2, label='Alpha#101')
    ax2.fill_between(df['trade_date'], alpha101, 0, where=(alpha101 >= 0), alpha=0.2, color='#FF4444')
    ax2.fill_between(df['trade_date'], alpha101, 0, where=(alpha101 < 0), alpha=0.2, color='#00AA00')
    ax2.axhline(y=0, color='#333333', linewidth=0.5)
    ax2.set_title('WorldQuant Alpha#101: (close - open) / ((high - low) + 0.001)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Alpha值', fontsize=11)
    ax2.set_xlabel('日期', fontsize=11)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(savepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [已保存] {savepath}")

# ============================================================
# 5. 导出JSON数据（供交互式网站使用）
# ============================================================

def export_json(df, filepath):
    """导出原始数据为JSON，供交互式网站前端使用"""
    data = []
    for _, row in df.iterrows():
        data.append({
            'date': row['trade_date'].strftime('%Y-%m-%d'),
            'open': round(float(row['open']), 2),
            'high': round(float(row['high']), 2),
            'low': round(float(row['low']), 2),
            'close': round(float(row['close']), 2),
            'vol': round(float(row['vol']), 2),
            'amount': round(float(row['amount']), 2),
            'pct_chg': round(float(row['pct_chg']), 4),
        })
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [已保存] {filepath} ({len(data)}条记录)")

# ============================================================
# 主程序
# ============================================================

def main():
    filepath = '中际旭创_300308_日线数据.csv'
    output_dir = '.'

    print(">>> 加载数据...")
    df = load_data(filepath)
    print(f"  数据加载完成，共 {len(df)} 条记录\n")

    # 1. 数据诊断
    print(">>> [1/5] 数据诊断分析...")
    desc = data_diagnostics(df)

    # 2 & 3. 计算指标并可视化
    print("\n>>> [2/5] 计算技术指标...")
    rsi = calc_rsi(df['close'], 14)
    dif, dea, macd_hist = calc_macd(df['close'], 12, 26, 9)
    mid, upper, lower, bandwidth, pct_b = calc_bollinger(df['close'], 20, 2)
    print("  RSI/MACD/布林带 计算完成")

    print("\n>>> [3/5] 生成可视化图表...")
    plot_price_with_bollinger(df, mid, upper, lower, f'{output_dir}/chart_bollinger.png')
    plot_rsi(df, rsi, f'{output_dir}/chart_rsi.png')
    plot_macd(df, dif, dea, macd_hist, f'{output_dir}/chart_macd.png')

    # 4. WorldQuant 101 Alpha因子
    print("\n>>> [4/5] 计算 WorldQuant 101 Alpha 因子...")
    alpha12 = calc_alpha_12(df)
    alpha101 = calc_alpha_101(df)
    plot_wq101(df, alpha12, alpha101, f'{output_dir}/chart_wq101.png')

    # 打印因子统计
    print("\n  Alpha#12 统计:")
    print(f"    均值: {alpha12.mean():.4f}, 标准差: {alpha12.std():.4f}")
    print(f"    最小值: {alpha12.min():.4f}, 最大值: {alpha12.max():.4f}")
    print("\n  Alpha#101 统计:")
    print(f"    均值: {alpha101.mean():.4f}, 标准差: {alpha101.std():.4f}")
    print(f"    最小值: {alpha101.min():.4f}, 最大值: {alpha101.max():.4f}")

    # 5. 导出JSON
    print("\n>>> [5/5] 导出JSON数据...")
    export_json(df, f'{output_dir}/stock_data.json')

    print("\n" + "=" * 60)
    print("分析完成！所有文件已生成。")
    print("=" * 60)

if __name__ == '__main__':
    main()
