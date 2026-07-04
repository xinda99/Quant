# -*- coding: utf-8 -*-
"""
中际旭创(300308.SZ) 过去一年日线行情分析
==========================================
1. 通过 Tushare API 获取过去一年每个交易日的日线数据
2. 绘制每日收盘价曲线图
3. 保存为 CSV 文件

依赖安装：
    pip install tushare pandas matplotlib

使用方法：
    将下方 TUSHARE_TOKEN 替换为你自己的 token（https://tushare.pro 注册获取）
    然后在 Jupyter Notebook / IPython 中逐 cell 运行
"""

# ============================================================
# Cell 1: 导入依赖 & 配置
# ============================================================
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Tushare token（替换为你自己的）
TUSHARE_TOKEN = "1e0b5ec1778ca679e79a36b6ddc303b41340f5e357f7a12e8678d5e2"

# 股票代码
TS_CODE = "300308.SZ"  # 中际旭创

# 设置 matplotlib 中文显示
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

# 初始化 Tushare
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

print(f"股票代码: {TS_CODE}")
print(f"数据区间: 过去一年")


# ============================================================
# Cell 2: 获取过去一年日线行情数据
# ============================================================
# 计算起止日期
end_date = datetime.now().strftime("%Y%m%d")
start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

print(f"起止日期: {start_date} ~ {end_date}")

# 调用 daily 接口获取日线行情
df = pro.daily(ts_code=TS_CODE, start_date=start_date, end_date=end_date)

# trade_date 转为 datetime 类型并排序（Tushare 返回的是倒序）
df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
df = df.sort_values("trade_date").reset_index(drop=True)

print(f"\n共获取 {len(df)} 个交易日数据")
print(f"日期范围: {df['trade_date'].iloc[0].strftime('%Y-%m-%d')} ~ {df['trade_date'].iloc[-1].strftime('%Y-%m-%d')}")
print(f"\n前5行预览:")
print(df.head())


# ============================================================
# Cell 3: 绘制每日收盘价曲线图
# ============================================================
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(df["trade_date"], df["close"], color="#E24B4A", linewidth=1.5, label="收盘价")
ax.fill_between(df["trade_date"], df["close"], alpha=0.1, color="#E24B4A")

# 标注最高点
max_idx = df["close"].idxmax()
ax.annotate(
    f"最高: ¥{df['close'].iloc[max_idx]:.2f}",
    xy=(df["trade_date"].iloc[max_idx], df["close"].iloc[max_idx]),
    xytext=(10, 15), textcoords="offset points",
    fontsize=10, color="#A32D2D",
    arrowprops=dict(arrowstyle="->", color="#A32D2D"),
)

# 标注最低点
min_idx = df["close"].idxmin()
ax.annotate(
    f"最低: ¥{df['close'].iloc[min_idx]:.2f}",
    xy=(df["trade_date"].iloc[min_idx], df["close"].iloc[min_idx]),
    xytext=(10, -20), textcoords="offset points",
    fontsize=10, color="#27500A",
    arrowprops=dict(arrowstyle="->", color="#27500A"),
)

ax.set_title(f"中际旭创 {TS_CODE} · 过去一年每日收盘价 ({len(df)} 个交易日)", fontsize=14, fontweight="bold")
ax.set_xlabel("日期", fontsize=12)
ax.set_ylabel("收盘价 (元)", fontsize=12)

# X 轴格式
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.xticks(rotation=45)

ax.legend(loc="upper left", fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("中际旭创_收盘价曲线.png", dpi=150, bbox_inches="tight")
plt.show()

# 打印统计信息
print(f"\n===== 区间统计 =====")
print(f"期初收盘: ¥{df['close'].iloc[0]:.2f}")
print(f"期末收盘: ¥{df['close'].iloc[-1]:.2f}")
print(f"区间最高: ¥{df['high'].max():.2f}")
print(f"区间最低: ¥{df['low'].min():.2f}")
print(f"年度涨幅: {(df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100:.2f}%")


# ============================================================
# Cell 4: 保存为 CSV 文件
# ============================================================
csv_filename = "中际旭创_300308_日线数据.csv"

# 将 trade_date 转回字符串格式 YYYYMMDD 保存
df_save = df.copy()
df_save["trade_date"] = df_save["trade_date"].dt.strftime("%Y%m%d")
df_save.to_csv(csv_filename, index=False, encoding="utf-8-sig")

print(f"CSV 已保存: {csv_filename}")
print(f"文件包含 {len(df_save)} 行数据，字段: {list(df_save.columns)}")
print(f"\n字段说明:")
print(f"  ts_code     - 股票代码")
print(f"  trade_date  - 交易日期(YYYYMMDD)")
print(f"  open        - 开盘价")
print(f"  high        - 最高价")
print(f"  low         - 最低价")
print(f"  close       - 收盘价")
print(f"  pre_close   - 昨收价")
print(f"  change      - 涨跌额")
print(f"  pct_chg     - 涨跌幅(%)")
print(f"  vol         - 成交量(手)")
print(f"  amount      - 成交额(千元)")
