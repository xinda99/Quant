"""
生成中际旭创技术指标交互式 HTML 网站
- 嵌入 JSON 数据
- Chart.js 可视化
- 参数可交互调整（RSI周期、MACD参数、布林带参数、Alpha窗口）
"""
import json

with open("analysis_output.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

js_data = {
    "dates": raw["price"]["dates"],
    "close": raw["price"]["close"],
    "open": raw["price"]["open"],
    "high": raw["price"]["high"],
    "low": raw["price"]["low"],
    "vol": raw["price"]["vol"],
    "pct_chg": raw["price"]["pct_chg"],
    "rsi": raw["indicators"]["rsi"]["values"],
    "macd_dif": raw["indicators"]["macd"]["dif"],
    "macd_dea": raw["indicators"]["macd"]["dea"],
    "macd_hist": raw["indicators"]["macd"]["hist"],
    "bb_upper": raw["indicators"]["bollinger"]["upper"],
    "bb_middle": raw["indicators"]["bollinger"]["middle"],
    "bb_lower": raw["indicators"]["bollinger"]["lower"],
    "alpha6": raw["indicators"]["alpha6"]["values"],
    "alpha101": raw["indicators"]["alpha101"]["values"],
    "stats": raw["stats"],
    "meta": raw["meta"],
}

json_str = json.dumps(js_data, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>中际旭创(300308.SZ) 技术指标交互分析</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
<style>
:root {
  --up: #e74c3c;
  --down: #27ae60;
  --bg: #f5f6fa;
  --card: #ffffff;
  --border: #e1e4e8;
  --text: #2c3e50;
  --text-light: #7f8c8d;
  --accent: #3498db;
  --shadow: 0 2px 8px rgba(0,0,0,0.08);
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: -apple-system, 'Segoe UI', 'Microsoft YaHei', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
.header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
  padding: 30px 40px;
}
.header h1 { font-size: 24px; margin-bottom: 8px; }
.header .subtitle { font-size: 14px; opacity: 0.8; }
.header .badge {
  display: inline-block;
  background: rgba(255,255,255,0.15);
  padding: 3px 12px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 8px;
}
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.section {
  background: var(--card);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
}
.section h2 {
  font-size: 18px;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--border);
  display: flex;
  align-items: center;
  gap: 8px;
}
.section h2 .icon { font-size: 22px; }
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}
.stat-card {
  background: var(--bg);
  border-radius: 8px;
  padding: 14px;
  text-align: center;
}
.stat-card .label { font-size: 12px; color: var(--text-light); margin-bottom: 4px; }
.stat-card .value { font-size: 20px; font-weight: 700; }
.stat-card .value.up { color: var(--up); }
.stat-card .value.down { color: var(--down); }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
table th, table td {
  padding: 8px 12px;
  text-align: right;
  border-bottom: 1px solid var(--border);
}
table th { background: var(--bg); font-weight: 600; color: var(--text-light); }
table td:first-child, table th:first-child { text-align: left; }
.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
  padding: 14px;
  background: var(--bg);
  border-radius: 8px;
}
.control-group { display: flex; align-items: center; gap: 8px; }
.control-group label { font-size: 13px; font-weight: 600; white-space: nowrap; }
.control-group input[type="range"] {
  width: 120px;
  accent-color: var(--accent);
}
.control-group .val {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent);
  min-width: 35px;
  text-align: center;
}
.chart-wrap { position: relative; height: 350px; }
.chart-wrap.tall { height: 420px; }
.nav {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.nav a {
  padding: 8px 18px;
  background: var(--card);
  border-radius: 8px;
  text-decoration: none;
  color: var(--text);
  font-size: 14px;
  font-weight: 600;
  border: 1px solid var(--border);
  transition: all 0.2s;
}
.nav a:hover, .nav a.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.indicator-card {
  border-left: 4px solid var(--accent);
  padding-left: 16px;
  margin-bottom: 16px;
}
.indicator-card h3 { font-size: 15px; margin-bottom: 6px; }
.indicator-card .formula {
  background: #1e1e2e;
  color: #a6e3a1;
  padding: 8px 14px;
  border-radius: 6px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
  margin: 8px 0;
}
.indicator-card .desc { font-size: 13px; color: var(--text-light); }
.missing-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}
.missing-badge.ok { background: #e8f5e9; color: #2e7d32; }
.footer {
  text-align: center;
  padding: 20px;
  color: var(--text-light);
  font-size: 13px;
}
</style>
</head>
<body>

<div class="header">
  <h1>中际旭创 (300308.SZ) 技术指标交互分析 <span class="badge">Tushare 数据</span></h1>
  <div class="subtitle" id="subtitle">数据范围加载中...</div>
</div>

<div class="container">
  <div class="nav">
    <a href="#diagnosis" class="active">数据诊断</a>
    <a href="#bollinger">布林带</a>
    <a href="#rsi">RSI</a>
    <a href="#macd">MACD</a>
    <a href="#alpha6">Alpha#6</a>
    <a href="#alpha101">Alpha#101</a>
  </div>

  <!-- 数据诊断 -->
  <div class="section" id="diagnosis">
    <h2><span class="icon">📊</span> 数据诊断分析</h2>
    <div id="overview-stats" class="stats-grid"></div>
    <h3 style="margin:20px 0 10px;font-size:15px">缺失值检查</h3>
    <div id="missing-table"></div>
    <h3 style="margin:20px 0 10px;font-size:15px">描述性统计</h3>
    <div id="desc-table"></div>
  </div>

  <!-- 布林带 -->
  <div class="section" id="bollinger">
    <h2><span class="icon">📈</span> 布林带 Bollinger Bands</h2>
    <div class="indicator-card">
      <h3>计算方法</h3>
      <div class="formula">中轨 = SMA(Close, N) &nbsp;&nbsp; 上轨 = 中轨 + K × σ &nbsp;&nbsp; 下轨 = 中轨 - K × σ</div>
      <div class="desc">布林带由 John Bollinger 提出，用移动平均±标准差构建价格通道。价格触及上轨可能超买，触及下轨可能超卖。带宽收缩常预示突破。</div>
    </div>
    <div class="controls">
      <div class="control-group">
        <label>周期 N</label>
        <input type="range" id="bb-period" min="5" max="40" value="20" step="1">
        <span class="val" id="bb-period-val">20</span>
      </div>
      <div class="control-group">
        <label>标准差倍数 K</label>
        <input type="range" id="bb-std" min="1" max="3" value="2" step="0.1">
        <span class="val" id="bb-std-val">2.0</span>
      </div>
    </div>
    <div class="chart-wrap tall"><canvas id="chart-bb"></canvas></div>
  </div>

  <!-- RSI -->
  <div class="section" id="rsi">
    <h2><span class="icon">⚡</span> RSI 相对强弱指标</h2>
    <div class="indicator-card">
      <h3>计算方法</h3>
      <div class="formula">RSI = 100 - 100 / (1 + RS) &nbsp;&nbsp; RS = N日平均涨幅 / N日平均跌幅 (Wilder平滑)</div>
      <div class="desc">RSI 由 Welles Wilder 提出，衡量价格内在强弱。RSI &gt; 70 为超买区（可能回调），RSI &lt; 30 为超卖区（可能反弹），50 为多空分界线。</div>
    </div>
    <div class="controls">
      <div class="control-group">
        <label>RSI 周期</label>
        <input type="range" id="rsi-period" min="5" max="30" value="14" step="1">
        <span class="val" id="rsi-period-val">14</span>
      </div>
      <div class="control-group">
        <label>超买线</label>
        <input type="range" id="rsi-ob" min="60" max="90" value="70" step="1">
        <span class="val" id="rsi-ob-val">70</span>
      </div>
      <div class="control-group">
        <label>超卖线</label>
        <input type="range" id="rsi-os" min="10" max="40" value="30" step="1">
        <span class="val" id="rsi-os-val">30</span>
      </div>
    </div>
    <div class="chart-wrap tall"><canvas id="chart-rsi"></canvas></div>
  </div>

  <!-- MACD -->
  <div class="section" id="macd">
    <h2><span class="icon">🔄</span> MACD 指数平滑异同移动平均线</h2>
    <div class="indicator-card">
      <h3>计算方法</h3>
      <div class="formula">DIF = EMA(Fast) - EMA(Slow) &nbsp;&nbsp; DEA = EMA(DIF, Signal) &nbsp;&nbsp; MACD柱 = 2×(DIF-DEA)</div>
      <div class="desc">MACD 由 Gerald Appel 提出，通过快慢均线差值判断趋势方向和动量。DIF 上穿 DEA 为金叉（买入信号），下穿为死叉（卖出信号）。</div>
    </div>
    <div class="controls">
      <div class="control-group">
        <label>快线周期</label>
        <input type="range" id="macd-fast" min="5" max="20" value="12" step="1">
        <span class="val" id="macd-fast-val">12</span>
      </div>
      <div class="control-group">
        <label>慢线周期</label>
        <input type="range" id="macd-slow" min="15" max="40" value="26" step="1">
        <span class="val" id="macd-slow-val">26</span>
      </div>
      <div class="control-group">
        <label>信号线</label>
        <input type="range" id="macd-signal" min="5" max="15" value="9" step="1">
        <span class="val" id="macd-signal-val">9</span>
      </div>
    </div>
    <div class="chart-wrap tall"><canvas id="chart-macd"></canvas></div>
  </div>

  <!-- Alpha#6 -->
  <div class="section" id="alpha6">
    <h2><span class="icon">🔬</span> WorldQuant Alpha#6</h2>
    <div class="indicator-card">
      <h3>公式 (WorldQuant 101 Alphas)</h3>
      <div class="formula">Alpha#6 = -1 × Correlation(Open, Volume, 10)</div>
      <div class="desc">计算10日窗口内开盘价与成交量的相关系数并取负。当价升量增（正相关），Alpha 为负，暗示后续可能反转；当价量背离时 Alpha 趋正，可能预示趋势延续。</div>
    </div>
    <div class="controls">
      <div class="control-group">
        <label>相关窗口</label>
        <input type="range" id="a6-window" min="5" max="30" value="10" step="1">
        <span class="val" id="a6-window-val">10</span>
      </div>
    </div>
    <div class="chart-wrap tall"><canvas id="chart-alpha6"></canvas></div>
  </div>

  <!-- Alpha#101 -->
  <div class="section" id="alpha101">
    <h2><span class="icon">🎯</span> WorldQuant Alpha#101</h2>
    <div class="indicator-card">
      <h3>公式 (WorldQuant 101 Alphas)</h3>
      <div class="formula">Alpha#101 = (Close - Open) / ((High - Low) + 0.001)</div>
      <div class="desc">衡量日内动量占日内振幅的比例，值域约 [-1, 1]。正值表示收盘高于开盘（多头动量），负值表示空头动量。分母加 0.001 防止除零。该因子捕捉当日价格在区间中的相对位置。</div>
    </div>
    <div class="chart-wrap tall"><canvas id="chart-alpha101"></canvas></div>
  </div>

  <div class="footer">
    数据来源: Tushare Pro &nbsp;|&nbsp; 股票: 中际旭创 300308.SZ &nbsp;|&nbsp; 生成时间: 2026-07-04
  </div>
</div>

<script>
const DATA = __JSON_PLACEHOLDER__;

// ============ 工具函数 ============
function ema(arr, period) {
  const result = new Array(arr.length).fill(null);
  if (arr.length < period) return result;
  let sum = 0;
  for (let i = 0; i < period; i++) sum += arr[i];
  result[period - 1] = sum / period;
  const mult = 2 / (period + 1);
  for (let i = period; i < arr.length; i++) {
    result[i] = arr[i] * mult + result[i - 1] * (1 - mult);
  }
  return result;
}

function sma(arr, period) {
  const result = new Array(arr.length).fill(null);
  for (let i = period - 1; i < arr.length; i++) {
    let sum = 0;
    for (let j = i - period + 1; j <= i; j++) sum += arr[j];
    result[i] = sum / period;
  }
  return result;
}

function rollingStd(arr, period) {
  const result = new Array(arr.length).fill(null);
  for (let i = period - 1; i < arr.length; i++) {
    let sum = 0;
    for (let j = i - period + 1; j <= i; j++) sum += arr[j];
    const mean = sum / period;
    let sqSum = 0;
    for (let j = i - period + 1; j <= i; j++) sqSum += (arr[j] - mean) ** 2;
    result[i] = Math.sqrt(sqSum / (period - 1));
  }
  return result;
}

function calcRSI(closes, period) {
  const rsi = new Array(closes.length).fill(null);
  const gains = [], losses = [];
  for (let i = 1; i < closes.length; i++) {
    const diff = closes[i] - closes[i - 1];
    gains.push(Math.max(diff, 0));
    losses.push(Math.max(-diff, 0));
  }
  if (gains.length < period) return rsi;
  let avgGain = 0, avgLoss = 0;
  for (let i = 0; i < period; i++) { avgGain += gains[i]; avgLoss += losses[i]; }
  avgGain /= period; avgLoss /= period;
  for (let i = period; i <= closes.length - 1; i++) {
    const idx = i - 1;
    avgGain = (avgGain * (period - 1) + gains[idx]) / period;
    avgLoss = (avgLoss * (period - 1) + losses[idx]) / period;
    if (avgLoss === 0) rsi[i] = 100;
    else rsi[i] = 100 - 100 / (1 + avgGain / avgLoss);
  }
  return rsi;
}

function calcMACD(closes, fast, slow, signal) {
  const emaFast = ema(closes, fast);
  const emaSlow = ema(closes, slow);
  const dif = closes.map((_, i) => (emaFast[i] !== null && emaSlow[i] !== null) ? emaFast[i] - emaSlow[i] : null);
  const difClean = dif.map(v => v === null ? 0 : v);
  const dea = ema(difClean, signal);
  const hist = dif.map((d, i) => (d !== null && dea[i] !== null) ? 2 * (d - dea[i]) : null);
  return { dif, dea, hist };
}

function calcBollinger(closes, period, numStd) {
  const mid = sma(closes, period);
  const std = rollingStd(closes, period);
  const upper = closes.map((_, i) => mid[i] !== null ? mid[i] + numStd * std[i] : null);
  const lower = closes.map((_, i) => mid[i] !== null ? mid[i] - numStd * std[i] : null);
  return { upper, mid, lower };
}

function rollingCorr(a, b, period) {
  const result = new Array(a.length).fill(null);
  for (let i = period - 1; i < a.length; i++) {
    let sa = 0, sb = 0;
    for (let j = i - period + 1; j <= i; j++) { sa += a[j]; sb += b[j]; }
    const ma = sa / period, mb = sb / period;
    let cov = 0, va = 0, vb = 0;
    for (let j = i - period + 1; j <= i; j++) {
      cov += (a[j] - ma) * (b[j] - mb);
      va += (a[j] - ma) ** 2;
      vb += (b[j] - mb) ** 2;
    }
    cov /= (period - 1);
    const denom = Math.sqrt((va / (period - 1)) * (vb / (period - 1)));
    result[i] = denom === 0 ? 0 : cov / denom;
  }
  return result;
}

function calcAlpha101(opens, highs, lows, closes) {
  return closes.map((c, i) => (c - opens[i]) / ((highs[i] - lows[i]) + 0.001));
}

// ============ Chart 默认配置 ============
Chart.defaults.font.family = "'Segoe UI', 'Microsoft YaHei', sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.color = '#7f8c8d';

const UP = '#e74c3c';
const DOWN = '#27ae60';
const dateLabels = DATA.dates.map(d => d);

function makeChart(canvasId, config) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  return new Chart(ctx, config);
}

// ============ 数据诊断 ============
function renderDiagnosis() {
  const meta = DATA.meta;
  const closes = DATA.close;
  const pct = DATA.pct_chg;
  document.getElementById('subtitle').textContent =
    `数据范围: ${meta.date_start} ~ ${meta.date_end} | 交易日: ${meta.total_days} 天 | 年度涨幅: +${(((closes[closes.length-1]/closes[0])-1)*100).toFixed(1)}%`;

  // Overview stats
  const lastClose = closes[closes.length - 1];
  const yearHigh = Math.max(...DATA.high);
  const yearLow = Math.min(...DATA.low);
  const avgVol = (DATA.vol.reduce((a,b)=>a+b,0) / DATA.vol.length / 10000).toFixed(0);
  const overview = [
    { label: '最新收盘价', value: '¥' + lastClose.toFixed(2) },
    { label: '年度涨幅', value: '+' + (((closes[closes.length-1]/closes[0])-1)*100).toFixed(1) + '%', cls: 'up' },
    { label: '区间最高', value: '¥' + yearHigh.toFixed(2) },
    { label: '区间最低', value: '¥' + yearLow.toFixed(2) },
    { label: '日均成交量', value: avgVol + '万手' },
    { label: '交易日数', value: meta.total_days + '天' },
  ];
  document.getElementById('overview-stats').innerHTML = overview.map(s =>
    `<div class="stat-card"><div class="label">${s.label}</div><div class="value ${s.cls||''}">${s.value}</div></div>`
  ).join('');

  // Missing values
  const missing = DATA.stats.missing_report;
  let html = '<table><thead><tr><th>字段</th><th>总数</th><th>缺失数</th><th>缺失率</th><th>状态</th></tr></thead><tbody>';
  for (const [field, info] of Object.entries(missing)) {
    html += `<tr><td>${field}</td><td>${info.total}</td><td>${info.missing}</td><td>${info.missing_pct}%</td><td><span class="missing-badge ok">✓ 完整</span></td></tr>`;
  }
  html += '</tbody></table>';
  document.getElementById('missing-table').innerHTML = html;

  // Descriptive stats
  const desc = DATA.stats.descriptive;
  html = '<table><thead><tr><th>字段</th><th>样本数</th><th>均值</th><th>标准差</th><th>最小值</th><th>P25</th><th>中位数</th><th>P75</th><th>最大值</th></tr></thead><tbody>';
  for (const [field, s] of Object.entries(desc)) {
    html += `<tr><td>${field}</td><td>${s.count}</td><td>${s.mean}</td><td>${s.std}</td><td>${s.min}</td><td>${s.p25 ?? '-'}</td><td>${s.median}</td><td>${s.p75 ?? '-'}</td><td>${s.max}</td></tr>`;
  }
  html += '</tbody></table>';
  document.getElementById('desc-table').innerHTML = html;
}

// ============ 布林带 Chart ============
let chartBB;
function renderBB() {
  const period = parseInt(document.getElementById('bb-period').value);
  const numStd = parseFloat(document.getElementById('bb-std').value);
  document.getElementById('bb-period-val').textContent = period;
  document.getElementById('bb-std-val').textContent = numStd.toFixed(1);

  const bb = calcBollinger(DATA.close, period, numStd);
  if (chartBB) chartBB.destroy();
  chartBB = makeChart('chart-bb', {
    type: 'line',
    data: {
      labels: dateLabels,
      datasets: [
        { label: '收盘价', data: DATA.close, borderColor: '#2c3e50', borderWidth: 1.5, pointRadius: 0, tension: 0.1, order: 1 },
        { label: '上轨 (+' + numStd + 'σ)', data: bb.upper, borderColor: UP, borderWidth: 1, pointRadius: 0, tension: 0.1, order: 2 },
        { label: '中轨 (SMA' + period + ')', data: bb.mid, borderColor: '#f39c12', borderWidth: 1, pointRadius: 0, borderDash: [5,3], tension: 0.1, order: 3 },
        { label: '下轨 (-' + numStd + 'σ)', data: bb.lower, borderColor: DOWN, borderWidth: 1, pointRadius: 0, tension: 0.1, order: 4 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top' },
        tooltip: { callbacks: { label: c => c.dataset.label + ': ¥' + c.parsed.y.toFixed(2) } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 12, maxRotation: 0 } },
        y: { grid: { color: '#f0f0f0' }, ticks: { callback: v => '¥' + v.toFixed(0) } }
      }
    }
  });
}

// ============ RSI Chart ============
let chartRSI;
function renderRSI() {
  const period = parseInt(document.getElementById('rsi-period').value);
  const ob = parseInt(document.getElementById('rsi-ob').value);
  const os = parseInt(document.getElementById('rsi-os').value);
  document.getElementById('rsi-period-val').textContent = period;
  document.getElementById('rsi-ob-val').textContent = ob;
  document.getElementById('rsi-os-val').textContent = os;

  const rsi = calcRSI(DATA.close, period);
  if (chartRSI) chartRSI.destroy();
  chartRSI = makeChart('chart-rsi', {
    type: 'line',
    data: {
      labels: dateLabels,
      datasets: [
        { label: 'RSI(' + period + ')', data: rsi, borderColor: '#8e44ad', borderWidth: 1.5, pointRadius: 0, tension: 0.2, fill: false },
        { label: '超买线(' + ob + ')', data: new Array(rsi.length).fill(ob), borderColor: DOWN, borderWidth: 1, borderDash: [6,3], pointRadius: 0 },
        { label: '超卖线(' + os + ')', data: new Array(rsi.length).fill(os), borderColor: UP, borderWidth: 1, borderDash: [6,3], pointRadius: 0 },
        { label: '中轴(50)', data: new Array(rsi.length).fill(50), borderColor: '#bdc3c7', borderWidth: 0.5, borderDash: [2,2], pointRadius: 0 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top' },
        tooltip: { callbacks: { label: c => c.dataset.label + ': ' + (c.parsed.y !== null ? c.parsed.y.toFixed(2) : 'N/A') } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 12, maxRotation: 0 } },
        y: { min: 0, max: 100, grid: { color: '#f0f0f0' } }
      }
    }
  });
}

// ============ MACD Chart ============
let chartMACD;
function renderMACD() {
  const fast = parseInt(document.getElementById('macd-fast').value);
  const slow = parseInt(document.getElementById('macd-slow').value);
  const signal = parseInt(document.getElementById('macd-signal').value);
  document.getElementById('macd-fast-val').textContent = fast;
  document.getElementById('macd-slow-val').textContent = slow;
  document.getElementById('macd-signal-val').textContent = signal;

  if (fast >= slow) { alert('快线周期必须小于慢线周期'); return; }

  const macd = calcMACD(DATA.close, fast, slow, signal);
  if (chartMACD) chartMACD.destroy();
  chartMACD = makeChart('chart-macd', {
    data: {
      labels: dateLabels,
      datasets: [
        { type: 'bar', label: 'MACD柱', data: macd.hist, backgroundColor: macd.hist.map(v => v === null ? 'transparent' : (v >= 0 ? UP : DOWN)), borderWidth: 0, order: 3 },
        { type: 'line', label: 'DIF', data: macd.dif, borderColor: '#e67e22', borderWidth: 1.5, pointRadius: 0, tension: 0.2, order: 1 },
        { type: 'line', label: 'DEA', data: macd.dea, borderColor: '#3498db', borderWidth: 1.5, pointRadius: 0, tension: 0.2, order: 2 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top' },
        tooltip: { callbacks: { label: c => c.dataset.label + ': ' + (c.parsed.y !== null ? c.parsed.y.toFixed(4) : 'N/A') } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 12, maxRotation: 0 } },
        y: { grid: { color: '#f0f0f0' } }
      }
    }
  });
}

// ============ Alpha#6 Chart ============
let chartA6;
function renderAlpha6() {
  const window = parseInt(document.getElementById('a6-window').value);
  document.getElementById('a6-window-val').textContent = window;

  const corr = rollingCorr(DATA.open, DATA.vol, window);
  const alpha6 = corr.map(v => v === null ? null : -1 * v);
  if (chartA6) chartA6.destroy();
  chartA6 = makeChart('chart-alpha6', {
    type: 'line',
    data: {
      labels: dateLabels,
      datasets: [
        { label: 'Alpha#6 (-Corr×Open,Vol,' + window + ')', data: alpha6, borderColor: '#9b59b6', borderWidth: 1.5, pointRadius: 0, tension: 0.2, fill: { target: 'origin', above: 'rgba(231,76,60,0.06)', below: 'rgba(39,174,96,0.06)' } },
        { label: '零线', data: new Array(alpha6.length).fill(0), borderColor: '#bdc3c7', borderWidth: 0.5, pointRadius: 0 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top' },
        tooltip: { callbacks: { label: c => c.dataset.label + ': ' + (c.parsed.y !== null ? c.parsed.y.toFixed(4) : 'N/A') } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 12, maxRotation: 0 } },
        y: { grid: { color: '#f0f0f0' }, ticks: { callback: v => v.toFixed(2) } }
      }
    }
  });
}

// ============ Alpha#101 Chart ============
let chartA101;
function renderAlpha101() {
  const alpha101 = calcAlpha101(DATA.open, DATA.high, DATA.low, DATA.close);
  if (chartA101) chartA101.destroy();
  chartA101 = makeChart('chart-alpha101', {
    data: {
      labels: dateLabels,
      datasets: [
        { type: 'bar', label: 'Alpha#101', data: alpha101, backgroundColor: alpha101.map(v => v >= 0 ? UP : DOWN), borderWidth: 0, order: 2 },
        { type: 'line', label: '零线', data: new Array(alpha101.length).fill(0), borderColor: '#bdc3c7', borderWidth: 0.5, pointRadius: 0, order: 1 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top' },
        tooltip: { callbacks: { label: c => c.dataset.label + ': ' + (c.parsed.y !== null ? c.parsed.y.toFixed(4) : 'N/A') } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 12, maxRotation: 0 } },
        y: { grid: { color: '#f0f0f0' } }
      }
    }
  });
}

// ============ 事件绑定 ============
document.getElementById('bb-period').addEventListener('input', renderBB);
document.getElementById('bb-std').addEventListener('input', renderBB);
document.getElementById('rsi-period').addEventListener('input', renderRSI);
document.getElementById('rsi-ob').addEventListener('input', renderRSI);
document.getElementById('rsi-os').addEventListener('input', renderRSI);
document.getElementById('macd-fast').addEventListener('input', renderMACD);
document.getElementById('macd-slow').addEventListener('input', renderMACD);
document.getElementById('macd-signal').addEventListener('input', renderMACD);
document.getElementById('a6-window').addEventListener('input', renderAlpha6);

// Nav smooth scroll
document.querySelectorAll('.nav a').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    document.querySelectorAll('.nav a').forEach(n => n.classList.remove('active'));
    a.classList.add('active');
    document.querySelector(a.getAttribute('href')).scrollIntoView({ behavior: 'smooth' });
  });
});

// ============ 初始化 ============
renderDiagnosis();
renderBB();
renderRSI();
renderMACD();
renderAlpha6();
renderAlpha101();
</script>
</body>
</html>
"""

html = html.replace("__JSON_PLACEHOLDER__", json_str)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"index.html 已生成，大小: {len(html)} 字符")
