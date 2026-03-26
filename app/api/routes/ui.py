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
  --gold:#d4af37;--gold2:#f0c040;
  --green:#00e5a0;--red:#ff4466;
  --text:#c0c0d0;--muted:#445;--border:rgba(212,175,55,0.1);
}
body{background:var(--bg);color:var(--text);font-family:'JetBrains Mono',monospace,sans-serif;min-height:100vh}

/* TOP BAR */
.topbar{
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;
  padding:12px 24px;border-bottom:1px solid var(--border);
  background:rgba(5,5,15,0.97);backdrop-filter:blur(10px);
  position:sticky;top:0;z-index:100;
}
.logo{font-size:1rem;font-weight:700;color:var(--gold);letter-spacing:3px}
.logo span{color:#fff;font-weight:300}

.price-block{display:flex;align-items:baseline;gap:10px}
.live-price{
  font-size:2rem;font-weight:700;color:var(--gold2);
  letter-spacing:1px;transition:color .3s;font-variant-numeric:tabular-nums;
}
.live-price.up{color:var(--green)}
.live-price.down{color:var(--red)}
.price-chg{font-size:.85rem;padding:3px 10px;border-radius:5px;font-weight:600}
.price-chg.up{background:rgba(0,229,160,.12);color:var(--green)}
.price-chg.down{background:rgba(255,68,102,.12);color:var(--red)}

.hl-block{display:flex;gap:16px;font-size:.72rem}
.hl-item{color:var(--muted)}
.hl-item span{color:var(--text)}

.ws-dot{width:8px;height:8px;border-radius:50%;background:var(--muted);display:inline-block;transition:background .3s}
.ws-dot.live{background:var(--green);box-shadow:0 0 8px var(--green);animation:blink 2s ease infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.4}}

/* SIGNAL BOX */
.sig-bar{
  margin:16px 24px 0;border-radius:12px;padding:16px 22px;
  display:flex;align-items:center;gap:18px;border:1px solid;transition:.4s;
}
.sig-bar.buy{background:rgba(0,229,160,.05);border-color:rgba(0,229,160,.25)}
.sig-bar.sell{background:rgba(255,68,102,.05);border-color:rgba(255,68,102,.25)}
.sig-bar.neutral{background:rgba(212,175,55,.04);border-color:rgba(212,175,55,.15)}
.sig-icon{font-size:2rem;line-height:1;min-width:36px}
.sig-info{flex:1}
.sig-bias{font-size:1.25rem;font-weight:700}
.sig-bias.buy{color:var(--green)}.sig-bias.sell{color:var(--red)}.sig-bias.neutral{color:var(--gold)}
.sig-reason{font-size:.68rem;color:var(--muted);margin-top:3px}
.conf-wrap{min-width:150px}
.conf-label{font-size:.62rem;color:var(--muted);letter-spacing:2px;margin-bottom:4px}
.conf-num{font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:5px}
.conf-track{background:rgba(255,255,255,.05);border-radius:99px;height:5px;overflow:hidden}
.conf-fill{height:100%;border-radius:99px;transition:width .8s,background .4s}

/* CARDS */
.cards{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;padding:14px 24px}
@media(max-width:1000px){.cards{grid-template-columns:repeat(3,1fr)}}
@media(max-width:600px){.cards{grid-template-columns:repeat(2,1fr)}}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:14px 14px}
.card-lbl{font-size:.6rem;color:var(--muted);letter-spacing:2px;text-transform:uppercase;margin-bottom:6px}
.card-val{font-size:1.2rem;font-weight:700}
.card-val.up{color:var(--green)}.card-val.dn{color:var(--red)}.card-val.neu{color:var(--gold)}
.card-sub{font-size:.65rem;color:var(--muted);margin-top:3px}

/* CHART */
.chart-outer{margin:0 24px 16px;border-radius:12px;overflow:hidden;border:1px solid var(--border)}
.chart-hdr{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:var(--bg2);border-bottom:1px solid var(--border)}
.chart-hdr-l{font-size:.75rem;color:var(--gold);letter-spacing:1px}
.chart-hdr-r{font-size:.68rem;color:var(--muted)}
#chart{height:430px;width:100%}

/* BOTTOM */
.bottom{display:grid;grid-template-columns:280px 1fr;gap:14px;padding:0 24px 24px}
@media(max-width:800px){.bottom{grid-template-columns:1fr}}
.panel{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px}
.panel-ttl{font-size:.65rem;color:var(--gold);letter-spacing:2px;text-transform:uppercase;padding-bottom:10px;margin-bottom:12px;border-bottom:1px solid var(--border)}
.m-row{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.03)}
.m-row:last-child{border:none}
.m-key{font-size:.68rem;color:var(--muted)}
.m-val{font-size:.82rem;font-weight:700;color:#fff}
.m-val.good{color:var(--green)}.m-val.warn{color:var(--gold)}.m-val.bad{color:var(--red)}
.train-btn{
  width:100%;margin-top:12px;padding:9px;border-radius:7px;cursor:pointer;
  background:rgba(212,175,55,.07);border:1px solid rgba(212,175,55,.25);
  color:var(--gold);font-family:inherit;font-size:.75rem;transition:.2s;
}
.train-btn:hover{background:rgba(212,175,55,.14)}
.train-btn:disabled{opacity:.4;cursor:not-allowed}
.train-msg{font-size:.62rem;color:var(--muted);text-align:center;margin-top:6px;min-height:14px}

/* HISTORY */
.hist-tbl{width:100%;border-collapse:collapse}
.hist-tbl th{font-size:.6rem;color:var(--muted);letter-spacing:1px;text-align:left;padding:5px 8px;border-bottom:1px solid var(--border)}
.hist-tbl td{font-size:.7rem;padding:6px 8px;border-bottom:1px solid rgba(255,255,255,.02)}
.hist-tbl tr:last-child td{border:none}
.hist-tbl tr:hover td{background:rgba(255,255,255,.02)}
.tag{display:inline-block;padding:2px 7px;border-radius:4px;font-weight:700;font-size:.65rem}
.tag.buy{background:rgba(0,229,160,.1);color:var(--green)}
.tag.sell{background:rgba(255,68,102,.1);color:var(--red)}
.tag.neutral{background:rgba(212,175,55,.08);color:var(--gold)}

/* misc */
.spinner{display:inline-block;width:12px;height:12px;border:2px solid rgba(212,175,55,.2);border-top-color:var(--gold);border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:5px}
@keyframes spin{to{transform:rotate(360deg)}}
.flash-up{animation:fup .5s ease}
.flash-dn{animation:fdn .5s ease}
@keyframes fup{0%{background:rgba(0,229,160,.25)}100%{background:transparent}}
@keyframes fdn{0%{background:rgba(255,68,102,.25)}100%{background:transparent}}
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <div class="logo">🥇 GOLD<span> TRADING AI</span></div>

  <div class="price-block">
    <div class="live-price" id="price">—</div>
    <div class="price-chg" id="price-chg" style="display:none"></div>
  </div>

  <div class="hl-block">
    <div class="hl-item">H <span id="p-high">—</span></div>
    <div class="hl-item">L <span id="p-low">—</span></div>
    <div class="hl-item">XAUUSD · 1H</div>
  </div>

  <div style="display:flex;align-items:center;gap:10px;font-size:.68rem;color:var(--muted)">
    <span class="ws-dot" id="ws-dot"></span>
    <span id="ws-status">connecting...</span>
    <span id="last-upd"></span>
  </div>
</div>

<!-- SIGNAL BAR -->
<div class="sig-bar neutral" id="sig-bar" style="margin-top:16px">
  <div class="sig-icon" id="sig-icon">⏳</div>
  <div class="sig-info">
    <div class="sig-bias neutral" id="sig-bias">Loading signal...</div>
    <div class="sig-reason" id="sig-reason">جارٍ التحليل...</div>
  </div>
  <div class="conf-wrap">
    <div class="conf-label">CONFIDENCE</div>
    <div class="conf-num" id="conf-num">—</div>
    <div class="conf-track"><div class="conf-fill" id="conf-fill" style="width:0"></div></div>
  </div>
</div>

<!-- CARDS -->
<div class="cards">
  <div class="card"><div class="card-lbl">RSI 14</div><div class="card-val neu" id="c-rsi">—</div><div class="card-sub" id="c-rsi-s">—</div></div>
  <div class="card"><div class="card-lbl">Ret 1H</div><div class="card-val" id="c-r1h">—</div><div class="card-sub">1h change</div></div>
  <div class="card"><div class="card-lbl">Ret 24H</div><div class="card-val" id="c-r24h">—</div><div class="card-sub">24h change</div></div>
  <div class="card"><div class="card-lbl">Volatility</div><div class="card-val neu" id="c-atr">—</div><div class="card-sub">ATR norm</div></div>
  <div class="card"><div class="card-lbl">MA20 Ratio</div><div class="card-val neu" id="c-ma">—</div><div class="card-sub">price/ma20</div></div>
</div>

<!-- CHART -->
<div class="chart-outer">
  <div class="chart-hdr">
    <span class="chart-hdr-l">XAUUSD · CANDLESTICK · 1H</span>
    <span class="chart-hdr-r" id="chart-info">loading...</span>
  </div>
  <div id="chart"></div>
</div>

<!-- BOTTOM -->
<div class="bottom">
  <div class="panel">
    <div class="panel-ttl">🤖 Model — OHLCV v0</div>
    <div class="m-row"><span class="m-key">STATUS</span><span class="m-val warn" id="m-st">—</span></div>
    <div class="m-row"><span class="m-key">Hit Rate</span><span class="m-val" id="m-hit">—</span></div>
    <div class="m-row"><span class="m-key">Expectancy</span><span class="m-val" id="m-exp">—</span></div>
    <div class="m-row"><span class="m-key">Train Samples</span><span class="m-val" id="m-tr">—</span></div>
    <div class="m-row"><span class="m-key">Val Accuracy</span><span class="m-val" id="m-acc">—</span></div>
    <button class="train-btn" id="train-btn" onclick="trainModel()">⚡ Train Model</button>
    <div class="train-msg" id="train-msg"></div>
  </div>

  <div class="panel">
    <div class="panel-ttl">📋 Signal History</div>
    <table class="hist-tbl">
      <thead><tr><th>Date/Time</th><th>Bias</th><th>Confidence</th><th>Score</th></tr></thead>
      <tbody id="hist-body"><tr><td colspan="4" style="text-align:center;color:var(--muted);padding:18px">Loading...</td></tr></tbody>
    </table>
  </div>
</div>

<script>
const API = location.origin;
const WS  = (location.protocol==='https:'?'wss':'ws')+'://'+location.host+'/api/v1/ws/price';
let chart, series, lastPrice = 0, ws, wsRetry = 0;

// ── CHART ────────────────────────────────────────────────────────────────
function initChart(){
  chart = LightweightCharts.createChart(document.getElementById('chart'),{
    layout:{background:{color:'#0a0a1a'},textColor:'#556'},
    grid:{vertLines:{color:'rgba(212,175,55,0.03)'},horzLines:{color:'rgba(212,175,55,0.03)'}},
    rightPriceScale:{borderColor:'rgba(212,175,55,0.08)'},
    timeScale:{borderColor:'rgba(212,175,55,0.08)',timeVisible:true,secondsVisible:false},
    crosshair:{mode:LightweightCharts.CrosshairMode.Normal},
  });
  series = chart.addCandlestickSeries({
    upColor:'#00e5a0',downColor:'#ff4466',
    borderUpColor:'#00e5a0',borderDownColor:'#ff4466',
    wickUpColor:'rgba(0,229,160,.5)',wickDownColor:'rgba(255,68,102,.5)',
  });
  new ResizeObserver(()=>{
    chart.applyOptions({width:document.getElementById('chart').clientWidth});
  }).observe(document.getElementById('chart'));
}

async function loadChart(){
  try{
    const r = await fetch(API+'/api/v1/chart/data?limit=300');
    const d = await r.json();
    if(Array.isArray(d)&&d.length){
      series.setData(d);
      chart.timeScale().fitContent();
      document.getElementById('chart-info').textContent = d.length+' candles loaded';
      // Update last candle with live price
      const last = d[d.length-1];
      if(lastPrice) series.update({...last,close:lastPrice,high:Math.max(last.high,lastPrice),low:Math.min(last.low,lastPrice)});
    }
  }catch(e){document.getElementById('chart-info').textContent='chart error';}
}

// ── WEBSOCKET — LIVE PRICE ───────────────────────────────────────────────
function connectWS(){
  ws = new WebSocket(WS);
  ws.onopen = ()=>{
    document.getElementById('ws-dot').className='ws-dot live';
    document.getElementById('ws-status').textContent='LIVE';
    wsRetry = 0;
  };
  ws.onmessage = (e)=>{
    const d = JSON.parse(e.data);
    updateLivePrice(d);
  };
  ws.onclose = ()=>{
    document.getElementById('ws-dot').className='ws-dot';
    document.getElementById('ws-status').textContent='reconnecting...';
    wsRetry = Math.min(wsRetry+1,5);
    setTimeout(connectWS, wsRetry*2000);
  };
  ws.onerror = ()=>ws.close();
}

function updateLivePrice(d){
  const price  = d.price;
  const prev   = d.prev || lastPrice || price;
  const dir    = price >= prev ? 'up':'down';
  const el     = document.getElementById('price');
  const fmtP   = '$'+price.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});

  // Flash color
  el.className = 'live-price '+dir;
  el.textContent = fmtP;
  setTimeout(()=>el.className='live-price',600);

  // Change badge
  const chgEl = document.getElementById('price-chg');
  const chg   = d.change_pct||0;
  chgEl.textContent=(chg>0?'+':'')+chg.toFixed(2)+'%';
  chgEl.className='price-chg '+(chg>=0?'up':'down');
  chgEl.style.display='inline';

  // H/L
  if(d.high) document.getElementById('p-high').textContent='$'+d.high.toLocaleString('en-US',{minimumFractionDigits:2});
  if(d.low)  document.getElementById('p-low').textContent ='$'+d.low.toLocaleString('en-US',{minimumFractionDigits:2});

  // Update last chart candle
  if(series && lastPrice !== price){
    const now = Math.floor(Date.now()/1000);
    const hourTs = Math.floor(now/3600)*3600;
    try{series.update({time:hourTs,open:prev,high:Math.max(prev,price),low:Math.min(prev,price),close:price});}catch(e){}
  }

  lastPrice = price;
  document.getElementById('last-upd').textContent=new Date().toLocaleTimeString();
}

// ── SIGNAL ───────────────────────────────────────────────────────────────
async function loadSignal(){
  try{
    const r = await fetch(API+'/api/v1/signals/gold');
    const d = await r.json();
    const bias = d.bias||'neutral';
    const conf = d.confidence||0;
    const box  = document.getElementById('sig-bar');
    box.className = 'sig-bar '+bias;
    document.getElementById('sig-icon').textContent = bias==='buy'?'▲':bias==='sell'?'▼':'─';
    const b = document.getElementById('sig-bias');
    b.textContent = bias==='buy'?'BUY  —  شراء':bias==='sell'?'SELL  —  بيع':'WAIT  —  انتظار';
    b.className = 'sig-bias '+bias;
    document.getElementById('sig-reason').textContent=(d.reasons||[]).join(' · ');
    document.getElementById('conf-num').textContent=(conf*100).toFixed(1)+'%';
    const fill=document.getElementById('conf-fill');
    fill.style.width=(conf*100)+'%';
    fill.style.background=bias==='buy'?'var(--green)':bias==='sell'?'var(--red)':'var(--gold)';
    const f=d.key_features||{};
    const rsi=f.rsi_14||0;
    const rsiEl=document.getElementById('c-rsi');
    rsiEl.textContent=rsi.toFixed(1);
    rsiEl.className='card-val '+(rsi<30?'up':rsi>70?'dn':'neu');
    document.getElementById('c-rsi-s').textContent=rsi<30?'Oversold':rsi>70?'Overbought':'Neutral';
    const r1=f.ret_1h||0;
    document.getElementById('c-r1h').textContent=(r1>0?'+':'')+r1.toFixed(3)+'%';
    document.getElementById('c-r1h').className='card-val '+(r1>=0?'up':'dn');
    const r24=f.ret_24h||0;
    document.getElementById('c-r24h').textContent=(r24>0?'+':'')+r24.toFixed(2)+'%';
    document.getElementById('c-r24h').className='card-val '+(r24>=0?'up':'dn');
    document.getElementById('c-atr').textContent=(f.atr_norm||0).toFixed(3)+'%';
    document.getElementById('c-ma').textContent=(f.ma20_ratio||0).toFixed(4);
  }catch(e){}
}

// ── HEALTH ───────────────────────────────────────────────────────────────
async function loadHealth(){
  try{
    const r=await fetch(API+'/health');
    const d=await r.json();
    const m=(d.models||{}).ohlcv_v0||{};
    const mt=m.metrics||{};
    document.getElementById('m-st').textContent=m.trained?'✅ Trained':'⚠️ Not Trained';
    document.getElementById('m-st').className='m-val '+(m.trained?'good':'warn');
    if(m.trained){
      document.getElementById('m-hit').textContent=((mt.hit_rate||0)*100).toFixed(1)+'%';
      document.getElementById('m-hit').className='m-val good';
      const ex=mt.expectancy_per_R||0;
      document.getElementById('m-exp').textContent=(ex>0?'+':'')+ex.toFixed(3)+'R';
      document.getElementById('m-exp').className='m-val '+(ex>0?'good':'bad');
      document.getElementById('m-tr').textContent=(mt.train_samples||0).toLocaleString();
      document.getElementById('m-acc').textContent=((mt.accuracy||0)*100).toFixed(1)+'%';
      document.getElementById('train-btn').textContent='🔁 Re-Train';
    }
  }catch(e){}
}

// ── HISTORY ──────────────────────────────────────────────────────────────
async function loadHistory(){
  try{
    const r=await fetch(API+'/api/v1/signals/gold/history?limit=20');
    const d=await r.json();
    const tb=document.getElementById('hist-body');
    if(!d.length){tb.innerHTML='<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:16px">No signals yet</td></tr>';return;}
    tb.innerHTML=d.map(s=>{
      const dt=s.ts.substring(0,10);const tm=s.ts.substring(11,16);
      return`<tr>
        <td style="color:var(--muted)">${dt} <span style="color:var(--text)">${tm}</span></td>
        <td><span class="tag ${s.bias}">${s.bias==='buy'?'▲ BUY':s.bias==='sell'?'▼ SELL':'─ WAIT'}</span></td>
        <td style="color:#fff;font-weight:600">${(s.confidence*100).toFixed(1)}%</td>
        <td style="color:${s.score>0?'var(--green)':s.score<0?'var(--red)':'var(--muted)'}">${s.score>0?'+':''}${(s.score||0).toFixed(3)}</td>
      </tr>`;
    }).join('');
  }catch(e){}
}

// ── TRAIN ────────────────────────────────────────────────────────────────
async function trainModel(){
  const btn=document.getElementById('train-btn');
  const msg=document.getElementById('train-msg');
  btn.disabled=true;
  btn.innerHTML='<span class="spinner"></span>Starting...';
  msg.textContent='Downloading 2y of gold data...';
  try{
    await fetch(API+'/api/v1/model/train',{method:'POST'});
    let polls=0;
    const iv=setInterval(async()=>{
      polls++;
      const sr=await fetch(API+'/api/v1/model/status');
      const sd=await sr.json();
      if(!sd.training_running||polls>80){
        clearInterval(iv);
        if(sd.trained){
          btn.disabled=false;btn.textContent='🔁 Re-Train';
          msg.textContent='✅ Model trained!';
          loadHealth();loadSignal();
        }else{
          btn.disabled=false;btn.textContent='⚡ Train Model';
          msg.textContent='Error: '+(sd.last_result?.error||'unknown');
        }
      }else{
        btn.innerHTML='<span class="spinner"></span>Training ('+polls*5+'s)';
      }
    },5000);
  }catch(e){btn.disabled=false;btn.textContent='⚡ Train Model';msg.textContent='Error: '+e.message;}
}

// ── INIT ─────────────────────────────────────────────────────────────────
initChart();
connectWS();
loadChart();
loadSignal();
loadHealth();
loadHistory();

// Refresh signal + history every 60s
setInterval(()=>{ loadSignal(); loadHistory(); }, 60000);
// Reload chart every 5min
setInterval(loadChart, 300000);
</script>
</body></html>"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    return HTML
