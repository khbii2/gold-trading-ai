from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gold Trading AI</title>
<script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#05050f;--bg2:#0a0a1a;--bg3:#0e0e20;
  --gold:#d4af37;--gold2:#f0c040;
  --green:#00e5a0;--red:#ff4466;--blue:#4af;
  --text:#b0b0c8;--muted:#445566;--border:rgba(212,175,55,0.1);
}
body{background:var(--bg);color:var(--text);font-family:'JetBrains Mono',monospace,sans-serif;min-height:100vh}

/* TOPBAR */
.topbar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;padding:10px 20px;border-bottom:1px solid var(--border);background:rgba(5,5,15,.97);backdrop-filter:blur(10px);position:sticky;top:0;z-index:100}
.logo{font-size:.95rem;font-weight:700;color:var(--gold);letter-spacing:3px}
.logo span{color:#fff;font-weight:300;font-size:.85rem}
.live-price{font-size:1.9rem;font-weight:700;color:var(--gold2);letter-spacing:1px;transition:color .3s;font-variant-numeric:tabular-nums}
.live-price.up{color:var(--green)}.live-price.down{color:var(--red)}
.pchg{font-size:.8rem;padding:2px 9px;border-radius:4px;font-weight:600}
.pchg.up{background:rgba(0,229,160,.1);color:var(--green)}.pchg.down{background:rgba(255,68,102,.1);color:var(--red)}
.hl{font-size:.7rem;color:var(--muted)}
.hl span{color:var(--text)}
.ws-dot{width:7px;height:7px;border-radius:50%;display:inline-block;background:var(--muted);transition:.3s}
.ws-dot.on{background:var(--green);box-shadow:0 0 7px var(--green);animation:bl 2s infinite}
@keyframes bl{0%,100%{opacity:1}50%{opacity:.3}}
.spin{display:inline-block;width:11px;height:11px;border:2px solid rgba(212,175,55,.2);border-top-color:var(--gold);border-radius:50%;animation:sp .6s linear infinite;vertical-align:middle;margin-right:4px}
@keyframes sp{to{transform:rotate(360deg)}}

/* ENTRY SIGNAL BIG CARD */
.entry-card{margin:14px 20px 0;border-radius:14px;padding:18px 22px;border:1px solid;display:flex;gap:20px;align-items:stretch;flex-wrap:wrap;transition:.4s}
.entry-card.buy{background:rgba(0,229,160,.05);border-color:rgba(0,229,160,.3)}
.entry-card.sell{background:rgba(255,68,102,.05);border-color:rgba(255,68,102,.3)}
.entry-card.wait{background:rgba(212,175,55,.04);border-color:rgba(212,175,55,.15)}
.ec-main{flex:0 0 200px}
.ec-action{font-size:1.8rem;font-weight:700;letter-spacing:2px}
.ec-action.buy{color:var(--green)}.ec-action.sell{color:var(--red)}.ec-action.wait{color:var(--gold)}
.ec-sub{font-size:.7rem;color:var(--muted);margin-top:3px}
.ec-levels{flex:0 0 160px;display:flex;flex-direction:column;gap:6px;justify-content:center}
.ec-row{display:flex;justify-content:space-between;font-size:.72rem}
.ec-row .lbl{color:var(--muted)}.ec-row .val{color:#fff;font-weight:600}
.ec-conds{flex:1;min-width:220px}
.cond{display:flex;align-items:center;gap:6px;font-size:.68rem;padding:3px 0;border-bottom:1px solid rgba(255,255,255,.03)}
.cond:last-child{border:none}
.cond-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.cond-dot.met{background:var(--green)}.cond-dot.miss{background:var(--muted)}
.conf-ring{flex:0 0 90px;display:flex;flex-direction:column;align-items:center;justify-content:center}
.conf-num{font-size:1.6rem;font-weight:700;color:#fff}
.conf-lbl{font-size:.6rem;color:var(--muted);letter-spacing:2px;text-transform:uppercase}

/* TF ALIGNMENT TABLE */
.tf-section{margin:14px 20px;background:var(--bg2);border:1px solid var(--border);border-radius:12px;overflow:hidden}
.tf-header{padding:10px 16px;border-bottom:1px solid var(--border);font-size:.65rem;color:var(--gold);letter-spacing:2px;text-transform:uppercase}
.tf-grid{display:grid;grid-template-columns:repeat(7,1fr)}
.tf-cell{padding:10px 8px;text-align:center;border-right:1px solid var(--border);border-bottom:1px solid var(--border)}
.tf-cell:last-child{border-right:none}
.tf-name{font-size:.65rem;color:var(--muted);letter-spacing:1px;margin-bottom:5px}
.tf-trend{font-size:.78rem;font-weight:700}
.tf-trend.bullish{color:var(--green)}.tf-trend.bearish{color:var(--red)}.tf-trend.neutral,.tf-trend.ranging{color:var(--gold)}
.tf-rsi{font-size:.65rem;color:var(--muted);margin-top:3px}
.tf-pat{font-size:.58rem;color:var(--blue);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* CHART */
.chart-outer{margin:0 20px 14px;border-radius:12px;overflow:hidden;border:1px solid var(--border)}
.chart-hdr{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;padding:10px 14px;background:var(--bg2);border-bottom:1px solid var(--border)}
.chart-ttl{font-size:.72rem;color:var(--gold);letter-spacing:1px}
#chart{height:420px;width:100%}

/* TF SWITCHER */
.tf-switcher{display:flex;gap:4px;align-items:center}
.tf-btn{padding:3px 10px;border-radius:5px;border:1px solid var(--muted);background:transparent;color:var(--muted);font-family:inherit;font-size:.65rem;cursor:pointer;transition:.15s;letter-spacing:.5px}
.tf-btn:hover{border-color:var(--gold);color:var(--gold)}
.tf-btn.active{background:rgba(212,175,55,.12);border-color:var(--gold);color:var(--gold2);font-weight:700}

/* EMA legend */
.ema-legend{display:flex;gap:10px;align-items:center;font-size:.6rem;flex-wrap:wrap}
.ema-dot{display:inline-block;width:14px;height:2px;border-radius:1px;margin-right:3px;vertical-align:middle}

/* FIB CARD */
.fib-card{margin:0 20px 14px;border-radius:12px;padding:14px 18px;background:var(--bg2);border:1px solid var(--border)}
.fib-top{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:10px}
.fib-title{font-size:.62rem;color:var(--gold);letter-spacing:2px;text-transform:uppercase}
.fib-signal{font-size:1rem;font-weight:700;letter-spacing:2px}
.fib-signal.buy{color:var(--green)}.fib-signal.sell{color:var(--red)}.fib-signal.wait{color:var(--gold)}
.fib-quality{font-size:.7rem;padding:2px 10px;border-radius:4px;background:rgba(212,175,55,.08);color:var(--gold2);border:1px solid rgba(212,175,55,.2)}
.fib-levels-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.fib-lvl{padding:2px 8px;border-radius:3px;font-size:.6rem;font-weight:700;border:1px solid}
.fib-gz{background:rgba(212,175,55,.12);border-color:rgba(212,175,55,.4);color:var(--gold2)}
.fib-normal{background:rgba(80,80,120,.1);border-color:var(--muted);color:var(--text)}
.fib-conds{display:flex;flex-direction:column;gap:3px}
.fib-cond{display:flex;align-items:center;gap:6px;font-size:.65rem}
.fib-cond-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.fib-cond-dot.met{background:var(--green)}.fib-cond-dot.miss{background:var(--muted)}
.fib-ob-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.ob-badge{padding:2px 9px;border-radius:3px;font-size:.6rem;font-weight:700}
.ob-bull{background:rgba(0,229,160,.08);color:var(--green);border:1px solid rgba(0,229,160,.2)}
.ob-bear{background:rgba(255,68,102,.08);color:var(--red);border:1px solid rgba(255,68,102,.2)}

/* BOTTOM GRID */
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:0 20px 20px}
@media(max-width:800px){.grid2{grid-template-columns:1fr}}
.panel{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:14px 16px}
.ptitle{font-size:.62rem;color:var(--gold);letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border)}

/* liquidity levels */
.liq-row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.03);font-size:.7rem}
.liq-row:last-child{border:none}
.liq-badge{display:inline-block;padding:1px 7px;border-radius:3px;font-size:.6rem;font-weight:700}
.liq-buy{background:rgba(0,229,160,.08);color:var(--green)}
.liq-sell{background:rgba(255,68,102,.08);color:var(--red)}
.liq-eq{background:rgba(68,170,255,.08);color:var(--blue)}
.sweep-box{margin-top:8px;padding:8px;border-radius:7px;font-size:.7rem}
.sweep-box.bull{background:rgba(0,229,160,.06);border:1px solid rgba(0,229,160,.2);color:var(--green)}
.sweep-box.bear{background:rgba(255,68,102,.06);border:1px solid rgba(255,68,102,.2);color:var(--red)}

/* model panel */
.mrow{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.03);font-size:.7rem}
.mrow:last-child{border:none}
.mkey{color:var(--muted)}.mval{color:#fff;font-weight:600}
.mval.good{color:var(--green)}.mval.warn{color:var(--gold)}.mval.bad{color:var(--red)}
.train-btn{width:100%;margin-top:10px;padding:8px;border-radius:7px;cursor:pointer;background:rgba(212,175,55,.06);border:1px solid rgba(212,175,55,.2);color:var(--gold);font-family:inherit;font-size:.72rem;transition:.2s}
.train-btn:hover{background:rgba(212,175,55,.12)}.train-btn:disabled{opacity:.35;cursor:not-allowed}
.tmsg{font-size:.6rem;color:var(--muted);text-align:center;margin-top:5px;min-height:12px}

/* analysis loading */
.loading-bar{height:2px;background:linear-gradient(90deg,transparent,var(--gold),transparent);background-size:200%;animation:lb 1.5s linear infinite;border-radius:2px}
@keyframes lb{0%{background-position:200%}100%{background-position:-200%}}
</style>
</head>
<body>

<!-- TOPBAR -->
<div class="topbar">
  <div class="logo">🥇 GOLD<span> TRADING AI</span></div>
  <div style="display:flex;align-items:baseline;gap:8px">
    <div class="live-price" id="price">—</div>
    <div class="pchg" id="pchg" style="display:none"></div>
  </div>
  <div style="display:flex;gap:14px">
    <span class="hl">H <span id="p-h">—</span></span>
    <span class="hl">L <span id="p-l">—</span></span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;font-size:.68rem">
    <span class="ws-dot" id="wsdot"></span>
    <span id="wsts" style="color:var(--muted)">connecting</span>
    <span id="upd" style="color:var(--muted);font-size:.62rem"></span>
  </div>
</div>

<!-- ENTRY SIGNAL -->
<div class="entry-card wait" id="ecard">
  <div class="ec-main">
    <div class="ec-action wait" id="ec-action">WAIT</div>
    <div class="ec-sub" id="ec-sub">جارٍ التحليل...</div>
    <div style="margin-top:10px">
      <div id="analysis-bar" class="loading-bar" style="width:100%"></div>
    </div>
  </div>
  <div class="ec-levels" id="ec-levels">
    <div class="ec-row"><span class="lbl">Entry</span><span class="val" id="ec-entry">—</span></div>
    <div class="ec-row"><span class="lbl">SL</span><span class="val" id="ec-sl" style="color:var(--red)">—</span></div>
    <div class="ec-row"><span class="lbl">TP</span><span class="val" id="ec-tp" style="color:var(--green)">—</span></div>
    <div class="ec-row"><span class="lbl">R:R</span><span class="val" id="ec-rr">—</span></div>
  </div>
  <div class="ec-conds" id="ec-conds">
    <div style="font-size:.62rem;color:var(--muted)">الشروط...</div>
  </div>
  <div class="conf-ring">
    <div class="conf-num" id="ec-conf">—</div>
    <div class="conf-lbl">SCORE</div>
  </div>
</div>

<!-- TF ALIGNMENT -->
<div class="tf-section">
  <div class="tf-header">📊 Timeframe Alignment — Monthly → Weekly → Daily → H4 → H1 → 15M → 5M</div>
  <div class="tf-grid" id="tf-grid">
    <div class="tf-cell"><div class="tf-name">MONTHLY</div><div class="tf-trend neutral" id="tf-monthly">—</div></div>
    <div class="tf-cell"><div class="tf-name">WEEKLY</div><div class="tf-trend neutral" id="tf-weekly">—</div></div>
    <div class="tf-cell"><div class="tf-name">DAILY</div><div class="tf-trend neutral" id="tf-daily">—</div></div>
    <div class="tf-cell"><div class="tf-name">H4</div><div class="tf-trend neutral" id="tf-h4">—</div></div>
    <div class="tf-cell"><div class="tf-name">H1</div><div class="tf-trend neutral" id="tf-h1">—</div></div>
    <div class="tf-cell"><div class="tf-name">15M</div><div class="tf-trend neutral" id="tf-m15"><div class="tf-rsi" id="rsi-m15">RSI —</div></div></div>
    <div class="tf-cell"><div class="tf-name">5M</div><div class="tf-trend neutral" id="tf-m5"><div class="tf-pat" id="pat-m5">—</div></div></div>
  </div>
</div>

<!-- FIBONACCI CARD -->
<div class="fib-card" id="fib-card">
  <div class="fib-top">
    <span class="fib-title">📐 Fibonacci — Golden Zone Entry (15M)</span>
    <div style="display:flex;align-items:center;gap:10px">
      <span class="fib-signal wait" id="fib-signal">— SCANNING</span>
      <span class="fib-quality" id="fib-quality">Quality: —</span>
    </div>
  </div>
  <div class="fib-levels-row" id="fib-levels-row">
    <span style="color:var(--muted);font-size:.65rem">loading fib levels...</span>
  </div>
  <div class="fib-conds" id="fib-conds"></div>
  <div class="fib-ob-row" id="fib-ob-row"></div>
</div>

<!-- CHART -->
<div class="chart-outer">
  <div class="chart-hdr">
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
      <span class="chart-ttl" id="chart-ttl">XAUUSD · 1H</span>
      <!-- TF Switcher -->
      <div class="tf-switcher" id="tf-switcher">
        <button class="tf-btn" onclick="switchTF('1m')">1M</button>
        <button class="tf-btn" onclick="switchTF('5m')">5M</button>
        <button class="tf-btn" onclick="switchTF('15m')">15M</button>
        <button class="tf-btn active" id="tfbtn-1h" onclick="switchTF('1h')">1H</button>
        <button class="tf-btn" onclick="switchTF('4h')">4H</button>
        <button class="tf-btn" onclick="switchTF('1d')">D1</button>
        <button class="tf-btn" onclick="switchTF('1w')">W1</button>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">
      <!-- EMA Legend -->
      <div class="ema-legend">
        <span><span class="ema-dot" style="background:#d4af37"></span>EMA9</span>
        <span><span class="ema-dot" style="background:#4af"></span>EMA20</span>
        <span><span class="ema-dot" style="background:#ff9900"></span>EMA50</span>
        <span><span class="ema-dot" style="background:#ff4466"></span>EMA200</span>
        <span><span class="ema-dot" style="background:rgba(212,175,55,.7);border:1px dashed #d4af37"></span>Fib GZ</span>
        <span><span class="ema-dot" style="background:rgba(0,229,160,.5)"></span>Bull OB</span>
        <span><span class="ema-dot" style="background:rgba(255,68,102,.5)"></span>Bear OB</span>
      </div>
      <span style="font-size:.65rem;color:var(--muted)" id="chart-info">loading...</span>
    </div>
  </div>
  <div id="chart"></div>
</div>

<!-- BOTTOM GRID -->
<div class="grid2">
  <!-- Liquidity -->
  <div class="panel">
    <div class="ptitle">💧 Liquidity Levels</div>
    <div id="liq-content"><div style="color:var(--muted);font-size:.72rem">loading...</div></div>
  </div>
  <!-- Model -->
  <div class="panel">
    <div class="ptitle">🤖 AI Model — OHLCV v0</div>
    <div class="mrow"><span class="mkey">Status</span><span class="mval warn" id="m-st">—</span></div>
    <div class="mrow"><span class="mkey">Hit Rate</span><span class="mval" id="m-hit">—</span></div>
    <div class="mrow"><span class="mkey">Expectancy</span><span class="mval" id="m-exp">—</span></div>
    <div class="mrow"><span class="mkey">Accuracy</span><span class="mval" id="m-acc">—</span></div>
    <div class="mrow"><span class="mkey">Samples</span><span class="mval" id="m-tr">—</span></div>
    <button class="train-btn" id="train-btn" onclick="trainModel()">⚡ Train OHLCV Model</button>
    <div class="tmsg" id="tmsg"></div>
  </div>
</div>

<script>
const API = location.origin;
const WS  = (location.protocol==='https:'?'wss':'ws')+'://'+location.host+'/api/v1/ws/price';
let chart, candleSeries, lastPrice=0, ws, wsR=0;
let ema9S, ema20S, ema50S, ema200S;
let srLines=[], liqLines=[], fibLines=[], obLines=[];
let currentTF='1h';

const TF_LABELS = {
  '1m':'1M','5m':'5M','15m':'15M',
  '1h':'1H','4h':'4H','1d':'D1','1w':'W1'
};

// ── CHART INIT ─────────────────────────────────────────────────────────────
function initChart(){
  chart = LightweightCharts.createChart(document.getElementById('chart'),{
    layout:{background:{color:'#0a0a1a'},textColor:'#556'},
    grid:{vertLines:{color:'rgba(212,175,55,.03)'},horzLines:{color:'rgba(212,175,55,.03)'}},
    rightPriceScale:{borderColor:'rgba(212,175,55,.08)'},
    timeScale:{borderColor:'rgba(212,175,55,.08)',timeVisible:true},
    crosshair:{mode:1},
  });
  candleSeries = chart.addCandlestickSeries({
    upColor:'#00e5a0',downColor:'#ff4466',
    borderUpColor:'#00e5a0',borderDownColor:'#ff4466',
    wickUpColor:'rgba(0,229,160,.45)',wickDownColor:'rgba(255,68,102,.45)',
  });
  // EMA series
  ema9S   = chart.addLineSeries({color:'#d4af37',lineWidth:1,priceLineVisible:false,lastValueVisible:false});
  ema20S  = chart.addLineSeries({color:'#44aaff',lineWidth:1,priceLineVisible:false,lastValueVisible:false});
  ema50S  = chart.addLineSeries({color:'#ff9900',lineWidth:1,priceLineVisible:false,lastValueVisible:false});
  ema200S = chart.addLineSeries({color:'#ff4466',lineWidth:1,priceLineVisible:false,lastValueVisible:false});

  new ResizeObserver(()=>chart.applyOptions({width:document.getElementById('chart').clientWidth}))
    .observe(document.getElementById('chart'));
}

// ── CLEAR OVERLAYS ─────────────────────────────────────────────────────────
function clearOverlays(){
  [...srLines,...liqLines,...fibLines,...obLines].forEach(l=>{
    try{chart.removeSeries(l)}catch(e){}
  });
  srLines=[];liqLines=[];fibLines=[];obLines=[];
}

// ── ADD PRICE LINE HELPER ──────────────────────────────────────────────────
function addHLine(price, color, style, lineWidth){
  // Use a LineSeries with 2 points spanning the full chart as a price line
  const s = chart.addLineSeries({
    color:color,lineWidth:lineWidth||1,
    lineStyle:style||2, // 2=dashed
    priceLineVisible:false,lastValueVisible:false,crosshairMarkerVisible:false,
  });
  // We'll set it with a constant value; the time range will be set later
  return s;
}

// ── TF SWITCHER ────────────────────────────────────────────────────────────
function switchTF(tf){
  currentTF = tf;
  // Update button states
  document.querySelectorAll('.tf-btn').forEach(b=>{
    b.classList.toggle('active', b.textContent===TF_LABELS[tf]);
  });
  document.getElementById('chart-ttl').textContent='XAUUSD · '+TF_LABELS[tf];
  loadChart(tf);
}

// ── LOAD CHART ─────────────────────────────────────────────────────────────
async function loadChart(tf){
  tf = tf || currentTF;
  document.getElementById('chart-info').textContent='loading...';
  clearOverlays();
  try{
    const r = await fetch(API+'/api/v1/chart/data?tf='+tf+'&limit=300');
    const d = await r.json();

    if(!d.candles||!d.candles.length){
      document.getElementById('chart-info').textContent='no data';
      return;
    }

    // Candles
    candleSeries.setData(d.candles);

    // EMAs
    if(d.ema9  && d.ema9.length)   ema9S.setData(d.ema9);
    if(d.ema20 && d.ema20.length)  ema20S.setData(d.ema20);
    if(d.ema50 && d.ema50.length)  ema50S.setData(d.ema50);
    if(d.ema200&& d.ema200.length) ema200S.setData(d.ema200);

    // Build time range from candles
    const times = d.candles.map(c=>c.time);
    const t0=times[0], t1=times[times.length-1];

    // S/R lines
    (d.resistances||[]).forEach(p=>{
      const s=addHLine(p,'rgba(255,255,255,0.45)',2,1);
      s.setData([{time:t0,value:p},{time:t1,value:p}]);
      srLines.push(s);
    });
    (d.supports||[]).forEach(p=>{
      const s=addHLine(p,'rgba(255,255,255,0.45)',2,1);
      s.setData([{time:t0,value:p},{time:t1,value:p}]);
      srLines.push(s);
    });

    // Liquidity lines
    (d.buy_side||[]).forEach(p=>{
      const s=addHLine(p,'rgba(0,229,160,0.6)',2,1);
      s.setData([{time:t0,value:p},{time:t1,value:p}]);
      liqLines.push(s);
    });
    (d.sell_side||[]).forEach(p=>{
      const s=addHLine(p,'rgba(255,68,102,0.6)',2,1);
      s.setData([{time:t0,value:p},{time:t1,value:p}]);
      liqLines.push(s);
    });
    (d.equal_highs||[]).forEach(p=>{
      const s=addHLine(p,'rgba(68,170,255,0.5)',1,1);
      s.setData([{time:t0,value:p},{time:t1,value:p}]);
      liqLines.push(s);
    });
    (d.equal_lows||[]).forEach(p=>{
      const s=addHLine(p,'rgba(68,170,255,0.5)',1,1);
      s.setData([{time:t0,value:p},{time:t1,value:p}]);
      liqLines.push(s);
    });

    // ── Fibonacci Levels ──
    const fib = d.fib || {};
    if(fib.levels && fib.swing_high){
      const fibColors = {
        '0.0':   {color:'rgba(180,180,220,0.35)', lw:1, style:0},
        '0.236': {color:'rgba(180,180,220,0.35)', lw:1, style:2},
        '0.382': {color:'rgba(100,200,255,0.5)',  lw:1, style:2},
        '0.5':   {color:'rgba(255,255,255,0.4)',  lw:1, style:0},
        '0.618': {color:'rgba(212,175,55,0.85)',  lw:2, style:0},   // Golden Zone top
        '0.705': {color:'rgba(212,175,55,0.5)',   lw:1, style:2},
        '0.786': {color:'rgba(212,175,55,0.85)',  lw:2, style:0},   // Golden Zone bottom
        '1.0':   {color:'rgba(180,180,220,0.35)', lw:1, style:0},
        '1.272': {color:'rgba(100,200,255,0.3)',  lw:1, style:2},
        '1.618': {color:'rgba(100,200,255,0.3)',  lw:1, style:2},
      };
      Object.entries(fib.levels).forEach(([lvl, price])=>{
        const cfg = fibColors[lvl] || {color:'rgba(200,200,200,0.3)',lw:1,style:2};
        const s = chart.addLineSeries({
          color:cfg.color, lineWidth:cfg.lw, lineStyle:cfg.style,
          priceLineVisible:false, lastValueVisible:true,
          title: lvl==='0.618'||lvl==='0.786' ? 'GZ '+lvl : lvl,
          crosshairMarkerVisible:false,
        });
        s.setData([{time:t0,value:price},{time:t1,value:price}]);
        fibLines.push(s);
      });

      // Swing High/Low markers
      const swingMarkers = [];
      // Find candle time for swing high (approximate using price)
      const shIdx = d.candles.findIndex(c=>Math.abs(c.high-fib.swing_high)<2);
      const slIdx = d.candles.findIndex(c=>Math.abs(c.low -fib.swing_low )<2);
      if(shIdx>=0) swingMarkers.push({time:d.candles[shIdx].time,position:'aboveBar',color:'#d4af37',shape:'circle',text:'SH'});
      if(slIdx>=0) swingMarkers.push({time:d.candles[slIdx].time,position:'belowBar',color:'#d4af37',shape:'circle',text:'SL'});

      // Combine with pattern markers
      const allMarkers = [...(d.markers||[]), ...swingMarkers]
        .sort((a,b)=>a.time-b.time);
      candleSeries.setMarkers(allMarkers);
    } else {
      // Pattern markers only
      candleSeries.setMarkers(d.markers||[]);
    }

    // ── Order Blocks ──
    if(fib.order_blocks && fib.order_blocks.length){
      fib.order_blocks.forEach(ob=>{
        const isBull = ob.type==='bullish';
        const topS = chart.addLineSeries({
          color: isBull?'rgba(0,229,160,0.7)':'rgba(255,68,102,0.7)',
          lineWidth:1, lineStyle:0,
          priceLineVisible:false, lastValueVisible:false,
          title: isBull?'OB↑':'OB↓',
          crosshairMarkerVisible:false,
        });
        const botS = chart.addLineSeries({
          color: isBull?'rgba(0,229,160,0.4)':'rgba(255,68,102,0.4)',
          lineWidth:1, lineStyle:2,
          priceLineVisible:false, lastValueVisible:false,
          crosshairMarkerVisible:false,
        });
        topS.setData([{time:t0,value:ob.top},   {time:t1,value:ob.top}]);
        botS.setData([{time:t0,value:ob.bottom},{time:t1,value:ob.bottom}]);
        obLines.push(topS,botS);
      });
    }

    chart.timeScale().fitContent();
    document.getElementById('chart-info').textContent=d.candles.length+' candles · '+TF_LABELS[tf];

    // ── Update Fib Card ──
    updateFibCard(fib);

  }catch(e){
    document.getElementById('chart-info').textContent='error: '+e.message;
  }
}

// ── WEBSOCKET ─────────────────────────────────────────────────────────────
function connectWS(){
  ws = new WebSocket(WS);
  ws.onopen=()=>{document.getElementById('wsdot').className='ws-dot on';document.getElementById('wsts').textContent='LIVE';wsR=0};
  ws.onmessage=(e)=>{const d=JSON.parse(e.data);updatePrice(d)};
  ws.onclose=()=>{document.getElementById('wsdot').className='ws-dot';document.getElementById('wsts').textContent='reconnecting...';wsR=Math.min(wsR+1,5);setTimeout(connectWS,wsR*2000)};
  ws.onerror=()=>ws.close();
}

function fmt(n){return '$'+n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2})}

function updatePrice(d){
  const p=d.price, pr=d.prev||lastPrice||p;
  const dir=p>=pr?'up':'down';
  const el=document.getElementById('price');
  el.textContent=fmt(p);el.className='live-price '+dir;
  setTimeout(()=>el.className='live-price',700);
  const chg=d.change_pct||0;
  const ce=document.getElementById('pchg');
  ce.textContent=(chg>0?'+':'')+chg.toFixed(2)+'%';
  ce.className='pchg '+(chg>=0?'up':'down');ce.style.display='inline';
  if(d.high) document.getElementById('p-h').textContent=fmt(d.high);
  if(d.low)  document.getElementById('p-l').textContent=fmt(d.low);
  if(candleSeries&&lastPrice!==p){
    const now=Math.floor(Date.now()/1000),ht=Math.floor(now/3600)*3600;
    try{candleSeries.update({time:ht,open:pr,high:Math.max(pr,p),low:Math.min(pr,p),close:p})}catch(e){}
  }
  lastPrice=p;
  document.getElementById('upd').textContent=new Date().toLocaleTimeString();
}

// ── FIB CARD UPDATE ───────────────────────────────────────────────────────
function updateFibCard(fib){
  if(!fib||!fib.swing_high) return;

  const sig = fib.signal || 'wait';
  const sigEl = document.getElementById('fib-signal');
  sigEl.textContent = sig==='buy'? '▲ BUY SETUP — شراء' :
                      sig==='sell'?'▼ SELL SETUP — بيع' :
                                   '── SCANNING — انتظار';
  sigEl.className = 'fib-signal ' + sig;
  document.getElementById('fib-quality').textContent = 'Quality: ' + (fib.quality||0) + '/100';

  // Levels row
  const gz = fib.golden_zone || {};
  const levelsHtml = Object.entries(fib.levels||{}).map(([lvl,price])=>{
    const isGZ = (lvl==='0.618'||lvl==='0.705'||lvl==='0.786');
    return `<span class="fib-lvl ${isGZ?'fib-gz':'fib-normal'}">${lvl} · $${price.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2})}</span>`;
  }).join('');
  document.getElementById('fib-levels-row').innerHTML =
    `<span class="fib-lvl" style="background:rgba(212,175,55,.06);border-color:rgba(212,175,55,.3);color:var(--gold);font-size:.58rem">
      ${fib.direction==='up'?'↑ BULLISH':'↓ BEARISH'} &nbsp;|&nbsp;
      SL $${fib.swing_low} → SH $${fib.swing_high}
    </span>` + levelsHtml;

  // Conditions
  document.getElementById('fib-conds').innerHTML =
    (fib.conditions||[]).map(c=>
      `<div class="fib-cond">
        <div class="fib-cond-dot ${c.met?'met':'miss'}"></div>
        <span style="color:${c.met?'#ccc':'var(--muted)'}">${c.detail}</span>
        <span style="color:${c.met?'var(--green)':'var(--muted)'};margin-left:auto">${c.met?'+':''}${c.weight}</span>
      </div>`
    ).join('');

  // Order Blocks
  document.getElementById('fib-ob-row').innerHTML =
    (fib.order_blocks||[]).map(ob=>
      `<span class="ob-badge ${ob.type==='bullish'?'ob-bull':'ob-bear'}">
        ${ob.type==='bullish'?'▲':'▼'} OB $${ob.bottom}–$${ob.top}
      </span>`
    ).join('');
}

// ── STANDALONE FIB LOAD (15M) ─────────────────────────────────────────────
async function loadFib(){
  try{
    const r = await fetch(API+'/api/v1/fib/gold?tf=15m');
    const d = await r.json();
    updateFibCard({
      signal:        d.entry_signal,
      quality:       d.entry_quality,
      direction:     d.direction,
      swing_high:    d.swing_high,
      swing_low:     d.swing_low,
      levels:        d.fib_levels,
      golden_zone:   d.golden_zone,
      order_blocks:  d.order_blocks,
      conditions:    d.conditions,
    });
  }catch(e){}
}

// ── MULTI-TF ANALYSIS ─────────────────────────────────────────────────────
const TF_ICONS = {bullish:'▲',bearish:'▼',neutral:'─',uptrend:'▲',downtrend:'▼',ranging:'↔'};

async function loadAnalysis(){
  document.getElementById('analysis-bar').style.display='block';
  try{
    const r=await fetch(API+'/api/v1/analysis/gold');
    const d=await r.json();

    document.getElementById('analysis-bar').style.display='none';

    // Entry signal
    const es=d.entry_signal||{};
    const action=es.action||'wait';
    const conf=es.confidence||0;
    const card=document.getElementById('ecard');
    card.className='entry-card '+action;
    const aEl=document.getElementById('ec-action');
    aEl.textContent=action==='buy'?'▲ BUY — شراء':action==='sell'?'▼ SELL — بيع':'── WAIT — انتظار';
    aEl.className='ec-action '+action;
    document.getElementById('ec-sub').textContent='Macro: '+es.macro_bias+' | Score: '+es.score+'/'+es.max_score;
    document.getElementById('ec-conf').textContent=conf.toFixed(0)+'%';
    if(d.price){
      document.getElementById('ec-entry').textContent=fmt(d.price);
      document.getElementById('ec-sl').textContent=es.suggested_sl?fmt(es.suggested_sl):'—';
      document.getElementById('ec-tp').textContent=es.suggested_tp?fmt(es.suggested_tp):'—';
      document.getElementById('ec-rr').textContent=es.rr?'1:'+es.rr:'—';
    }

    // Conditions
    const condsHtml=[
      ...(es.conditions_met||[]).map(c=>`<div class="cond"><div class="cond-dot met"></div><span style="color:#ccc">${c.detail}</span><span style="color:var(--green);margin-left:auto">+${c.weight}</span></div>`),
      ...(es.conditions_missing||[]).map(c=>`<div class="cond"><div class="cond-dot miss"></div><span style="color:var(--muted)">${c.detail}</span><span style="color:var(--muted);margin-left:auto">${c.weight}</span></div>`),
    ].join('');
    document.getElementById('ec-conds').innerHTML=condsHtml||'<div style="font-size:.65rem;color:var(--muted)">No conditions</div>';

    // TF table
    const tfs=d.timeframes||{};
    ['monthly','weekly','daily','h4','h1','m15','m5'].forEach(k=>{
      const tf=tfs[k]||{};
      const trend=tf.trend||'neutral';
      const el=document.getElementById('tf-'+k);
      if(el){
        el.textContent=(TF_ICONS[trend]||'─')+' '+(trend||'—').toUpperCase();
        el.className='tf-trend '+trend;
        const rsiEl=document.getElementById('rsi-'+k);
        if(rsiEl&&tf.rsi) rsiEl.textContent='RSI '+tf.rsi.toFixed(0);
        const patEl=document.getElementById('pat-'+k);
        if(patEl){
          const pats=tf.patterns||[];
          patEl.textContent=pats.length?pats[0].pattern:'—';
        }
      }
    });

    // Liquidity
    const liq=d.liquidity||{};
    let liqHtml='';
    (liq.buy_side||[]).slice(0,3).forEach(v=>liqHtml+=`<div class="liq-row"><span>Buy-Side Liquidity</span><span class="liq-badge liq-buy">${fmt(v)}</span></div>`);
    (liq.sell_side||[]).slice(0,3).forEach(v=>liqHtml+=`<div class="liq-row"><span>Sell-Side Liquidity</span><span class="liq-badge liq-sell">${fmt(v)}</span></div>`);
    (liq.equal_highs||[]).slice(0,2).forEach(v=>liqHtml+=`<div class="liq-row"><span>Equal Highs</span><span class="liq-badge liq-eq">${fmt(v)}</span></div>`);
    (liq.equal_lows||[]).slice(0,2).forEach(v=>liqHtml+=`<div class="liq-row"><span>Equal Lows</span><span class="liq-badge liq-eq">${fmt(v)}</span></div>`);
    if(liq.last_sweep){
      const sw=liq.last_sweep;
      liqHtml+=`<div class="sweep-box ${sw.direction==='bullish'?'bull':'bear'}">⚡ ${sw.type} @ ${fmt(sw.level)}</div>`;
    }
    document.getElementById('liq-content').innerHTML=liqHtml||'<div style="color:var(--muted);font-size:.7rem">No liquidity data</div>';

  }catch(e){
    document.getElementById('analysis-bar').style.display='none';
    document.getElementById('ec-sub').textContent='Analysis error: '+e.message;
  }
}

// ── HEALTH ────────────────────────────────────────────────────────────────
async function loadHealth(){
  try{
    const r=await fetch(API+'/health');
    const d=await r.json();
    const m=(d.models||{}).ohlcv_v0||{};
    const mt=m.metrics||{};
    document.getElementById('m-st').textContent=m.trained?'✅ Trained':'⚠️ Not Trained';
    document.getElementById('m-st').className='mval '+(m.trained?'good':'warn');
    if(m.trained){
      document.getElementById('m-hit').textContent=((mt.hit_rate||0)*100).toFixed(1)+'%';
      document.getElementById('m-hit').className='mval good';
      const ex=mt.expectancy_per_R||0;
      document.getElementById('m-exp').textContent=(ex>0?'+':'')+ex.toFixed(3)+'R';
      document.getElementById('m-exp').className='mval '+(ex>0?'good':'bad');
      document.getElementById('m-acc').textContent=((mt.accuracy||0)*100).toFixed(1)+'%';
      document.getElementById('m-tr').textContent=(mt.train_samples||0).toLocaleString();
      document.getElementById('train-btn').textContent='🔁 Re-Train';
    }
  }catch(e){}
}

// ── TRAIN ─────────────────────────────────────────────────────────────────
async function trainModel(){
  const btn=document.getElementById('train-btn');
  const msg=document.getElementById('tmsg');
  btn.disabled=true;btn.innerHTML='<span class="spin"></span>Training...';
  msg.textContent='Fetching 2y data...';
  try{
    await fetch(API+'/api/v1/model/train',{method:'POST'});
    let p=0;
    const iv=setInterval(async()=>{
      p++;
      const sr=await fetch(API+'/api/v1/model/status');
      const sd=await sr.json();
      if(!sd.training_running||p>80){
        clearInterval(iv);
        if(sd.trained){btn.disabled=false;btn.textContent='🔁 Re-Train';msg.textContent='✅ Done!';loadHealth();}
        else{btn.disabled=false;btn.textContent='⚡ Train';msg.textContent='Error: '+(sd.last_result?.error||'?');}
      }else btn.innerHTML='<span class="spin"></span>Training ('+p*5+'s)';
    },5000);
  }catch(e){btn.disabled=false;btn.textContent='⚡ Train';msg.textContent='Error: '+e.message;}
}

// ── INIT ──────────────────────────────────────────────────────────────────
initChart();
connectWS();
loadChart('1h');
loadAnalysis();
loadHealth();
loadFib();

setInterval(loadAnalysis, 180000);
setInterval(()=>loadChart(currentTF), 300000);
setInterval(loadFib, 120000);  // refresh fib every 2 min
</script>
</body></html>"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    return HTML
