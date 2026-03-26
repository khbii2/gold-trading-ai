from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gold Trading AI</title>
<script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#05050f;--bg2:#0a0a1a;--bg3:#0f0f22;
  --gold:#d4af37;--gold2:#f0c040;--gold3:rgba(212,175,55,0.08);
  --green:#00e5a0;--red:#ff4466;--blue:#4488ff;
  --text:#c0c0d0;--muted:#555566;--border:rgba(212,175,55,0.12);
}
body{background:var(--bg);color:var(--text);font-family:'JetBrains Mono',monospace,sans-serif;min-height:100vh;overflow-x:hidden}

/* ── TOP BAR ── */
.topbar{
  display:flex;align-items:center;justify-content:space-between;
  padding:14px 28px;border-bottom:1px solid var(--border);
  background:rgba(10,10,26,0.95);backdrop-filter:blur(8px);
  position:sticky;top:0;z-index:100;
}
.logo{font-size:1.15rem;font-weight:700;color:var(--gold);letter-spacing:2px}
.logo span{color:#fff;font-weight:400}
.live-price{font-size:1.6rem;font-weight:700;color:var(--gold2);letter-spacing:1px}
.price-change{font-size:.8rem;padding:2px 8px;border-radius:4px;margin-left:8px}
.up{background:rgba(0,229,160,.15);color:var(--green)}
.down{background:rgba(255,68,102,.15);color:var(--red)}
.refresh-btn{
  background:transparent;border:1px solid var(--border);color:var(--muted);
  padding:6px 14px;border-radius:6px;cursor:pointer;font-size:.75rem;
  transition:.2s;font-family:inherit;
}
.refresh-btn:hover{border-color:var(--gold);color:var(--gold)}

/* ── SIGNAL CARDS ── */
.cards{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;padding:20px 28px}
.card{
  background:var(--bg2);border:1px solid var(--border);border-radius:12px;
  padding:18px 16px;transition:.2s;
}
.card:hover{border-color:rgba(212,175,55,.3)}
.card-label{font-size:.65rem;color:var(--muted);letter-spacing:2px;text-transform:uppercase;margin-bottom:8px}
.card-value{font-size:1.3rem;font-weight:700;color:#fff}
.card-value.buy{color:var(--green)}
.card-value.sell{color:var(--red)}
.card-value.neutral{color:var(--gold)}
.card-sub{font-size:.7rem;color:var(--muted);margin-top:4px}

/* ── SIGNAL BIG BOX ── */
.signal-box{
  margin:0 28px 16px;border-radius:14px;padding:20px 24px;
  display:flex;align-items:center;gap:20px;
  border:1px solid;transition:.4s;
}
.signal-box.buy{background:rgba(0,229,160,.05);border-color:rgba(0,229,160,.3)}
.signal-box.sell{background:rgba(255,68,102,.05);border-color:rgba(255,68,102,.3)}
.signal-box.neutral{background:rgba(212,175,55,.04);border-color:rgba(212,175,55,.2)}
.signal-icon{font-size:2.2rem;line-height:1}
.signal-text{flex:1}
.signal-bias{font-size:1.4rem;font-weight:700}
.signal-reasons{font-size:.7rem;color:var(--muted);margin-top:4px}
.confidence-bar{flex:0 0 160px}
.conf-label{font-size:.65rem;color:var(--muted);margin-bottom:4px}
.conf-track{background:rgba(255,255,255,.06);border-radius:99px;height:6px;overflow:hidden}
.conf-fill{height:100%;border-radius:99px;transition:.6s}

/* ── CHART ── */
.chart-wrap{margin:0 28px 20px;border-radius:14px;overflow:hidden;border:1px solid var(--border);background:var(--bg2)}
.chart-header{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;border-bottom:1px solid var(--border)}
.chart-title{font-size:.8rem;color:var(--gold);letter-spacing:1px}
.chart-tf{display:flex;gap:6px}
.tf-btn{
  background:transparent;border:1px solid var(--border);color:var(--muted);
  padding:3px 10px;border-radius:5px;cursor:pointer;font-size:.7rem;
  transition:.2s;font-family:inherit;
}
.tf-btn.active,.tf-btn:hover{border-color:var(--gold);color:var(--gold)}
#chart{height:420px;width:100%}

/* ── BOTTOM GRID ── */
.bottom{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:0 28px 28px}
.panel{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:18px}
.panel-title{font-size:.7rem;color:var(--gold);letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid var(--border)}

/* model metrics */
.metrics-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.metric{background:var(--bg3);border-radius:8px;padding:12px}
.metric-label{font-size:.62rem;color:var(--muted);letter-spacing:1px;text-transform:uppercase}
.metric-val{font-size:1.1rem;font-weight:700;color:#fff;margin-top:4px}
.metric-val.good{color:var(--green)}
.metric-val.warn{color:var(--gold)}

/* history table */
.hist-table{width:100%;border-collapse:collapse}
.hist-table th{font-size:.62rem;color:var(--muted);letter-spacing:1px;text-align:left;padding:6px 8px;border-bottom:1px solid var(--border)}
.hist-table td{font-size:.72rem;padding:7px 8px;border-bottom:1px solid rgba(255,255,255,.03)}
.hist-table tr:last-child td{border:none}
.tag{display:inline-block;padding:2px 8px;border-radius:4px;font-weight:700;font-size:.68rem}
.tag.buy{background:rgba(0,229,160,.12);color:var(--green)}
.tag.sell{background:rgba(255,68,102,.12);color:var(--red)}
.tag.neutral{background:rgba(212,175,55,.1);color:var(--gold)}

/* train button */
.train-btn{
  width:100%;margin-top:14px;padding:10px;border-radius:8px;cursor:pointer;
  background:rgba(212,175,55,.08);border:1px solid rgba(212,175,55,.3);
  color:var(--gold);font-family:inherit;font-size:.8rem;transition:.2s;
}
.train-btn:hover{background:rgba(212,175,55,.15)}
.train-btn:disabled{opacity:.4;cursor:not-allowed}

/* status dot */
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:6px}
.dot.ok{background:var(--green);box-shadow:0 0 8px var(--green)}
.dot.warn{background:var(--gold)}
.dot.err{background:var(--red)}

/* ── SPINNER ── */
.spinner{display:inline-block;width:14px;height:14px;border:2px solid rgba(212,175,55,.2);border-top-color:var(--gold);border-radius:50%;animation:spin .7s linear infinite;vertical-align:middle;margin-right:6px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.pulsing{animation:pulse 1.5s ease infinite}

@media(max-width:900px){
  .cards{grid-template-columns:repeat(2,1fr)}
  .bottom{grid-template-columns:1fr}
}
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <div class="logo">🥇 GOLD<span> TRADING AI</span></div>
  <div style="display:flex;align-items:center;gap:12px">
    <span class="live-price" id="price">—</span>
    <span class="price-change" id="price-change" style="display:none"></span>
  </div>
  <div style="display:flex;align-items:center;gap:12px">
    <span style="font-size:.72rem;color:var(--muted)" id="last-update">—</span>
    <button class="refresh-btn" onclick="loadAll()">⟳ Refresh</button>
  </div>
</div>

<!-- SIGNAL BOX -->
<div class="signal-box neutral" id="signal-box" style="margin-top:20px">
  <div class="signal-icon" id="sig-icon">⏳</div>
  <div class="signal-text">
    <div class="signal-bias neutral" id="sig-bias">Loading...</div>
    <div class="signal-reasons" id="sig-reasons">جارٍ جلب البيانات...</div>
  </div>
  <div class="confidence-bar">
    <div class="conf-label">CONFIDENCE</div>
    <div style="font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:6px" id="conf-pct">—</div>
    <div class="conf-track"><div class="conf-fill" id="conf-fill" style="width:0%;background:var(--gold)"></div></div>
  </div>
</div>

<!-- METRIC CARDS -->
<div class="cards">
  <div class="card">
    <div class="card-label">RSI 14</div>
    <div class="card-value" id="c-rsi">—</div>
    <div class="card-sub" id="c-rsi-s">—</div>
  </div>
  <div class="card">
    <div class="card-label">Return 1H</div>
    <div class="card-value" id="c-ret1h">—</div>
    <div class="card-sub">1h change</div>
  </div>
  <div class="card">
    <div class="card-label">Return 24H</div>
    <div class="card-value" id="c-ret24h">—</div>
    <div class="card-sub">24h change</div>
  </div>
  <div class="card">
    <div class="card-label">ATR Norm</div>
    <div class="card-value" id="c-atr">—</div>
    <div class="card-sub">volatility</div>
  </div>
  <div class="card">
    <div class="card-label">MA20 Ratio</div>
    <div class="card-value" id="c-ma">—</div>
    <div class="card-sub">price/ma20</div>
  </div>
</div>

<!-- CHART -->
<div class="chart-wrap">
  <div class="chart-header">
    <span class="chart-title">XAUUSD · 1H · Candlestick</span>
    <div style="display:flex;align-items:center;gap:8px">
      <span class="dot ok" id="chart-dot"></span>
      <span style="font-size:.68rem;color:var(--muted)" id="chart-info">—</span>
    </div>
  </div>
  <div id="chart"></div>
</div>

<!-- BOTTOM -->
<div class="bottom">
  <!-- Model Metrics -->
  <div class="panel">
    <div class="panel-title">🤖 Model — OHLCV v0</div>
    <div class="metrics-grid" id="metrics-grid">
      <div class="metric"><div class="metric-label">STATUS</div><div class="metric-val warn pulsing" id="m-status">Loading</div></div>
      <div class="metric"><div class="metric-label">Hit Rate</div><div class="metric-val" id="m-hit">—</div></div>
      <div class="metric"><div class="metric-label">Expectancy</div><div class="metric-val" id="m-exp">—</div></div>
      <div class="metric"><div class="metric-label">Train Samples</div><div class="metric-val" id="m-train">—</div></div>
    </div>
    <button class="train-btn" id="train-btn" onclick="trainModel()">
      ⚡ Train Model (first time only)
    </button>
    <div style="font-size:.65rem;color:var(--muted);margin-top:8px;text-align:center" id="train-msg"></div>
  </div>

  <!-- Signal History -->
  <div class="panel">
    <div class="panel-title">📋 Signal History</div>
    <table class="hist-table">
      <thead><tr><th>Time</th><th>Bias</th><th>Confidence</th><th>Score</th></tr></thead>
      <tbody id="hist-body"><tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px">Loading...</td></tr></tbody>
    </table>
  </div>
</div>

<script>
const API = '';
let chart, series, prevPrice = 0;

// ── CHART ─────────────────────────────────────────────────────────────────
function initChart() {
  chart = LightweightCharts.createChart(document.getElementById('chart'), {
    layout:{ background:{color:'#0a0a1a'}, textColor:'#666' },
    grid:{ vertLines:{color:'rgba(212,175,55,0.04)'}, horzLines:{color:'rgba(212,175,55,0.04)'} },
    rightPriceScale:{ borderColor:'rgba(212,175,55,0.1)' },
    timeScale:{ borderColor:'rgba(212,175,55,0.1)', timeVisible:true },
    crosshair:{ mode:1 },
    handleScroll:true, handleScale:true,
  });
  series = chart.addCandlestickSeries({
    upColor:'#00e5a0', downColor:'#ff4466',
    borderUpColor:'#00e5a0', borderDownColor:'#ff4466',
    wickUpColor:'rgba(0,229,160,0.6)', wickDownColor:'rgba(255,68,102,0.6)',
  });
  new ResizeObserver(()=>chart.applyOptions({width:document.getElementById('chart').clientWidth}))
    .observe(document.getElementById('chart'));
}

async function loadChart() {
  try {
    const r = await fetch(API+'/api/v1/chart/data?limit=300');
    const data = await r.json();
    if(Array.isArray(data) && data.length) {
      series.setData(data);
      chart.timeScale().fitContent();
      document.getElementById('chart-info').textContent = data.length+' candles';
    }
  } catch(e) { document.getElementById('chart-info').textContent = 'chart error: '+e.message; }
}

// ── SIGNAL ────────────────────────────────────────────────────────────────
async function loadSignal() {
  try {
    const r = await fetch(API+'/api/v1/signals/gold');
    const d = await r.json();

    // Price
    const price = d.price || 0;
    const el = document.getElementById('price');
    el.textContent = '$' + price.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
    const chg = document.getElementById('price-change');
    if(prevPrice && prevPrice !== price) {
      const diff = price - prevPrice;
      chg.textContent = (diff>0?'+':'')+diff.toFixed(2);
      chg.className = 'price-change '+(diff>0?'up':'down');
      chg.style.display='inline';
    }
    prevPrice = price;

    // Signal box
    const bias = d.bias || 'neutral';
    const conf = d.confidence || 0;
    const box = document.getElementById('signal-box');
    box.className = 'signal-box '+bias;
    document.getElementById('sig-icon').textContent = bias==='buy'?'▲':bias==='sell'?'▼':'─';
    const biasEl = document.getElementById('sig-bias');
    biasEl.textContent = bias==='buy'?'BUY — شراء':bias==='sell'?'SELL — بيع':'WAIT — انتظار';
    biasEl.className = 'signal-bias '+bias;
    document.getElementById('sig-reasons').textContent = (d.reasons||[]).join(' · ');
    document.getElementById('conf-pct').textContent = (conf*100).toFixed(1)+'%';
    const fill = document.getElementById('conf-fill');
    fill.style.width = (conf*100)+'%';
    fill.style.background = bias==='buy'?'var(--green)':bias==='sell'?'var(--red)':'var(--gold)';

    // Feature cards
    const f = d.key_features || {};
    const rsi = f.rsi_14 || 0;
    const rsiEl = document.getElementById('c-rsi');
    rsiEl.textContent = rsi.toFixed(1);
    rsiEl.className = 'card-value '+(rsi<30?'buy':rsi>70?'sell':'neutral');
    document.getElementById('c-rsi-s').textContent = rsi<30?'Oversold':rsi>70?'Overbought':'Neutral';
    const r1 = (f.ret_1h||0);
    document.getElementById('c-ret1h').textContent = (r1>0?'+':'')+r1.toFixed(3)+'%';
    document.getElementById('c-ret1h').className = 'card-value '+(r1>0?'buy':'sell');
    const r24 = (f.ret_24h||0);
    document.getElementById('c-ret24h').textContent = (r24>0?'+':'')+r24.toFixed(2)+'%';
    document.getElementById('c-ret24h').className = 'card-value '+(r24>0?'buy':'sell');
    document.getElementById('c-atr').textContent = (f.atr_norm||0).toFixed(3)+'%';
    document.getElementById('c-ma').textContent = (f.ma20_ratio||0).toFixed(4);

    document.getElementById('last-update').textContent = 'Updated '+new Date().toLocaleTimeString();
  } catch(e) {
    document.getElementById('sig-bias').textContent = 'API Error';
    document.getElementById('sig-reasons').textContent = e.message;
  }
}

// ── HEALTH / MODEL ────────────────────────────────────────────────────────
async function loadHealth() {
  try {
    const r = await fetch(API+'/health');
    const d = await r.json();
    const m = (d.models||{}).ohlcv_v0 || {};
    const mt = m.metrics || {};
    const trained = m.trained;
    document.getElementById('m-status').textContent = trained?'✅ Trained':'⚠️ Not Trained';
    document.getElementById('m-status').className = 'metric-val '+(trained?'good':'warn');
    if(trained) {
      document.getElementById('m-hit').textContent = ((mt.hit_rate||0)*100).toFixed(1)+'%';
      document.getElementById('m-hit').className = 'metric-val good';
      const exp = mt.expectancy_per_R || 0;
      document.getElementById('m-exp').textContent = (exp>0?'+':'')+exp.toFixed(3)+'R';
      document.getElementById('m-exp').className = 'metric-val '+(exp>0?'good':'warn');
      document.getElementById('m-train').textContent = (mt.train_samples||0).toLocaleString();
      document.getElementById('train-btn').style.display = 'none';
    }
  } catch(e){}
}

// ── HISTORY ───────────────────────────────────────────────────────────────
async function loadHistory() {
  try {
    const r = await fetch(API+'/api/v1/signals/gold/history?limit=20');
    const data = await r.json();
    const tbody = document.getElementById('hist-body');
    if(!data.length){ tbody.innerHTML='<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px">No signals yet</td></tr>'; return; }
    tbody.innerHTML = data.map(s=>{
      const t = s.ts.substring(11,16);
      const d = s.ts.substring(0,10);
      return `<tr>
        <td style="color:var(--muted)">${d} ${t}</td>
        <td><span class="tag ${s.bias}">${s.bias==='buy'?'▲ BUY':s.bias==='sell'?'▼ SELL':'─ WAIT'}</span></td>
        <td style="color:#fff">${(s.confidence*100).toFixed(1)}%</td>
        <td style="color:${s.score>0?'var(--green)':s.score<0?'var(--red)':'var(--muted)'}">${s.score>0?'+':''}${(s.score||0).toFixed(3)}</td>
      </tr>`;
    }).join('');
  } catch(e){}
}

// ── TRAIN ─────────────────────────────────────────────────────────────────
async function trainModel() {
  const btn = document.getElementById('train-btn');
  const msg = document.getElementById('train-msg');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Training... (~2 min)';
  msg.textContent = 'Downloading data & training RandomForest...';
  try {
    const r = await fetch(API+'/api/v1/model/train', {method:'POST'});
    const d = await r.json();
    msg.textContent = d.message || d.status;
    // Poll status
    let polls = 0;
    const poll = setInterval(async()=>{
      polls++;
      const sr = await fetch(API+'/api/v1/model/status');
      const sd = await sr.json();
      if(!sd.training_running || polls>60){
        clearInterval(poll);
        if(sd.trained){
          btn.innerHTML='✅ Trained!';
          msg.textContent='Model ready — refreshing...';
          setTimeout(()=>loadAll(), 1500);
        } else {
          btn.disabled=false;
          btn.innerHTML='⚡ Train Model';
          msg.textContent='Error: '+(sd.last_result?.error||'unknown');
        }
      } else {
        btn.innerHTML='<span class="spinner"></span>Training ('+polls*5+'s)';
      }
    }, 5000);
  } catch(e) {
    btn.disabled=false;
    btn.innerHTML='⚡ Train Model';
    msg.textContent='Error: '+e.message;
  }
}

// ── MAIN ──────────────────────────────────────────────────────────────────
async function loadAll() {
  await Promise.all([loadSignal(), loadChart(), loadHealth(), loadHistory()]);
}

initChart();
loadAll();
setInterval(loadAll, 30000);
</script>
</body></html>"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    return HTML
