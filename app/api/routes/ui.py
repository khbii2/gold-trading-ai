from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GOLD AI — Professional Trading Terminal</title>
<script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/* ── RESET & ROOT ─────────────────────────────────────────────────────────── */
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg0:#02020a;
  --bg1:#06060f;
  --bg2:#0a0a18;
  --bg3:#0e0e22;
  --bg4:#12122a;
  --gold:#c9a84c;
  --gold2:#f0d060;
  --gold3:rgba(201,168,76,.12);
  --green:#00e5a0;
  --green2:rgba(0,229,160,.1);
  --red:#ff3355;
  --red2:rgba(255,51,85,.1);
  --blue:#4499ff;
  --blue2:rgba(68,153,255,.1);
  --text:#9aa0bc;
  --text2:#c8cfe8;
  --muted:#2e3550;
  --border:rgba(201,168,76,.07);
  --border2:rgba(255,255,255,.04);
  --r:8px;
  --r2:12px;
}
html,body{height:100%;background:var(--bg0);color:var(--text);
  font-family:'Inter',system-ui,sans-serif;font-size:13px;line-height:1.5;
  overflow-x:hidden}
.mono{font-family:'JetBrains Mono',monospace}

/* ── SCROLLBAR ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:var(--bg1)}
::-webkit-scrollbar-thumb{background:var(--muted);border-radius:2px}

/* ── LAYOUT ───────────────────────────────────────────────────────────────── */
.layout{display:flex;flex-direction:column;min-height:100vh}
.main-row{display:grid;grid-template-columns:1fr 300px;gap:1px;flex:1;background:var(--border)}
.left-col{background:var(--bg0);display:flex;flex-direction:column;min-width:0}
.right-col{background:var(--bg0);display:flex;flex-direction:column;gap:1px;background:var(--border)}
.right-panel{background:var(--bg0)}
@media(max-width:1100px){.main-row{grid-template-columns:1fr}}
@media(max-width:1100px){.right-col{display:grid;grid-template-columns:1fr 1fr}}

/* ── HEADER ───────────────────────────────────────────────────────────────── */
header{
  display:flex;align-items:center;gap:0;
  background:var(--bg1);
  border-bottom:1px solid var(--border);
  height:52px;position:sticky;top:0;z-index:200;
}
.hdr-brand{
  display:flex;align-items:center;gap:10px;
  padding:0 20px;border-right:1px solid var(--border);
  height:100%;min-width:160px;
}
.brand-icon{
  width:28px;height:28px;border-radius:6px;
  background:linear-gradient(135deg,var(--gold),#8a6a20);
  display:flex;align-items:center;justify-content:center;
  font-size:14px;flex-shrink:0;
}
.brand-name{font-size:.75rem;font-weight:700;letter-spacing:2px;color:var(--gold2)}
.brand-sub{font-size:.55rem;color:var(--text);letter-spacing:1px;text-transform:uppercase;margin-top:1px}

.hdr-price{
  display:flex;align-items:baseline;gap:8px;
  padding:0 24px;border-right:1px solid var(--border);
}
.price-val{
  font-family:'JetBrains Mono',monospace;
  font-size:1.55rem;font-weight:600;
  color:var(--gold2);letter-spacing:.5px;
  transition:color .25s;
}
.price-val.up{color:var(--green)}.price-val.down{color:var(--red)}
.price-chg{
  font-size:.72rem;font-weight:600;padding:2px 8px;border-radius:4px;
  font-family:'JetBrains Mono',monospace;
}
.price-chg.up{background:var(--green2);color:var(--green)}
.price-chg.down{background:var(--red2);color:var(--red)}

.hdr-stats{
  display:flex;gap:20px;padding:0 20px;border-right:1px solid var(--border);
}
.hdr-stat{display:flex;flex-direction:column;gap:1px}
.hdr-stat .lbl{font-size:.55rem;color:var(--muted);letter-spacing:1px;text-transform:uppercase}
.hdr-stat .val{font-size:.72rem;color:var(--text2);font-family:'JetBrains Mono',monospace;font-weight:500}

.hdr-right{display:flex;align-items:center;gap:12px;padding:0 16px;margin-left:auto}
.status-pill{
  display:flex;align-items:center;gap:6px;
  padding:4px 10px;border-radius:20px;
  background:var(--bg3);border:1px solid var(--border);
  font-size:.62rem;font-weight:600;letter-spacing:1px;
}
.status-dot{
  width:6px;height:6px;border-radius:50%;background:var(--muted);
  transition:.3s;flex-shrink:0;
}
.status-dot.live{
  background:var(--green);
  box-shadow:0 0 6px var(--green);
  animation:pulse 2s infinite;
}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.hdr-time{font-family:'JetBrains Mono',monospace;font-size:.62rem;color:var(--text)}

/* ── SIGNAL BAR ───────────────────────────────────────────────────────────── */
.signal-bar{
  display:flex;align-items:stretch;gap:1px;
  background:var(--border);
  border-bottom:1px solid var(--border);
  flex-shrink:0;
}
.sig-main{
  display:flex;align-items:center;gap:16px;
  padding:14px 20px;background:var(--bg1);flex:0 0 auto;
  min-width:220px;
}
.sig-action{
  font-size:1.3rem;font-weight:700;letter-spacing:3px;
  font-family:'JetBrains Mono',monospace;
}
.sig-action.buy{color:var(--green)}.sig-action.sell{color:var(--red)}.sig-action.wait{color:var(--gold)}
.sig-score-ring{
  width:52px;height:52px;border-radius:50%;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  border:2px solid var(--muted);flex-shrink:0;position:relative;
}
.sig-score-ring.buy{border-color:var(--green)}
.sig-score-ring.sell{border-color:var(--red)}
.sig-score-ring.wait{border-color:var(--gold)}
.sig-score-num{font-size:.9rem;font-weight:700;line-height:1;color:var(--text2);font-family:'JetBrains Mono',monospace}
.sig-score-lbl{font-size:.42rem;color:var(--muted);letter-spacing:1px;text-transform:uppercase}

.sig-levels{
  display:flex;gap:0;background:var(--bg1);flex:0 0 auto;
  border-right:1px solid var(--border);
}
.sig-lvl{
  display:flex;flex-direction:column;justify-content:center;
  padding:10px 18px;border-right:1px solid var(--border2);
}
.sig-lvl:last-child{border-right:none}
.sig-lvl .lbl{font-size:.55rem;color:var(--muted);letter-spacing:1px;text-transform:uppercase;margin-bottom:4px}
.sig-lvl .val{font-size:.82rem;font-weight:600;font-family:'JetBrains Mono',monospace;color:var(--text2)}
.sig-lvl .val.entry{color:var(--gold2)}
.sig-lvl .val.sl{color:var(--red)}
.sig-lvl .val.tp{color:var(--green)}
.sig-lvl .val.rr{color:var(--blue)}

.sig-conds{
  display:flex;flex-direction:column;justify-content:center;
  gap:4px;padding:10px 16px;background:var(--bg1);flex:1;min-width:0;
}
.cond-row{display:flex;align-items:center;gap:7px;font-size:.64rem}
.cond-icon{font-size:.6rem;flex-shrink:0}
.cond-row .met{color:var(--text2)}.cond-row .miss{color:var(--muted)}
.cond-pts{margin-left:auto;font-size:.6rem;font-family:'JetBrains Mono',monospace;flex-shrink:0}
.cond-pts.met{color:var(--green)}.cond-pts.miss{color:var(--muted)}

.sig-macro{
  display:flex;flex-direction:column;justify-content:center;
  padding:10px 16px;background:var(--bg1);flex:0 0 auto;border-left:1px solid var(--border);
  font-size:.62rem;color:var(--muted);text-align:center;min-width:80px;
}
.sig-macro span{font-size:.68rem;color:var(--text);font-weight:600;margin-top:3px}

/* ── TF TABLE ─────────────────────────────────────────────────────────────── */
.tf-bar{
  display:flex;align-items:stretch;background:var(--border);
  border-bottom:1px solid var(--border);flex-shrink:0;gap:1px;
}
.tf-cell{
  flex:1;display:flex;flex-direction:column;align-items:center;
  justify-content:center;padding:8px 6px;background:var(--bg1);
  gap:3px;min-width:0;cursor:pointer;transition:background .15s;
}
.tf-cell:hover{background:var(--bg3)}
.tf-cell .tf-lbl{font-size:.55rem;color:var(--muted);letter-spacing:1px;text-transform:uppercase}
.tf-cell .tf-trend{font-size:.7rem;font-weight:600;font-family:'JetBrains Mono',monospace}
.tf-cell .tf-rsi{font-size:.58rem;color:var(--muted);font-family:'JetBrains Mono',monospace}
.tf-cell .tf-pat{font-size:.5rem;color:var(--blue);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
.tf-trend.bullish{color:var(--green)}.tf-trend.bearish{color:var(--red)}
.tf-trend.neutral,.tf-trend.ranging,.tf-trend.uptrend{color:var(--gold)}
.tf-trend.downtrend{color:var(--red)}

/* ── CHART AREA ───────────────────────────────────────────────────────────── */
.chart-wrap{display:flex;flex-direction:column;flex:1;min-height:0;position:relative}
.chart-toolbar{
  display:flex;align-items:center;gap:0;
  background:var(--bg1);border-bottom:1px solid var(--border);
  height:40px;flex-shrink:0;
}
.tf-tabs{display:flex;height:100%}
.tf-tab{
  display:flex;align-items:center;justify-content:center;
  padding:0 16px;height:100%;
  font-size:.67rem;font-weight:600;letter-spacing:1px;
  color:var(--muted);border-right:1px solid var(--border);
  cursor:pointer;transition:.15s;font-family:'JetBrains Mono',monospace;
  border-bottom:2px solid transparent;
}
.tf-tab:hover{color:var(--text2);background:var(--bg3)}
.tf-tab.active{color:var(--gold2);border-bottom-color:var(--gold);background:var(--bg3)}

.chart-legend{
  display:flex;align-items:center;gap:14px;padding:0 14px;margin-left:auto;
  font-size:.6rem;
}
.leg-item{display:flex;align-items:center;gap:5px;color:var(--muted)}
.leg-line{width:16px;height:2px;border-radius:1px;flex-shrink:0}
.chart-info-badge{
  padding:3px 10px;border-radius:4px;background:var(--bg3);
  font-size:.6rem;color:var(--muted);font-family:'JetBrains Mono',monospace;
  border:1px solid var(--border);margin-right:10px;
}

#chart{flex:1;width:100%;min-height:400px}

/* ── RIGHT PANELS ─────────────────────────────────────────────────────────── */
.panel{padding:14px 16px;flex:1;overflow:hidden;min-height:0}
.panel-title{
  display:flex;align-items:center;gap:8px;
  font-size:.58rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;
  color:var(--gold);margin-bottom:12px;padding-bottom:9px;
  border-bottom:1px solid var(--border2);
}
.panel-title .pticon{font-size:.75rem}

/* FIB panel */
.fib-dir{
  display:inline-flex;align-items:center;gap:6px;
  padding:3px 10px;border-radius:4px;margin-bottom:10px;
  font-size:.62rem;font-weight:700;font-family:'JetBrains Mono',monospace;
  border:1px solid;
}
.fib-dir.up{background:var(--green2);border-color:rgba(0,229,160,.2);color:var(--green)}
.fib-dir.down{background:var(--red2);border-color:rgba(255,51,85,.2);color:var(--red)}
.fib-dir.none{background:var(--bg3);border-color:var(--border);color:var(--muted)}

.fib-sig{
  font-size:1rem;font-weight:700;letter-spacing:2px;
  font-family:'JetBrains Mono',monospace;margin-bottom:6px;
}
.fib-sig.buy{color:var(--green)}.fib-sig.sell{color:var(--red)}.fib-sig.wait{color:var(--gold)}

.fib-quality-bar{
  display:flex;align-items:center;gap:8px;margin-bottom:10px;
}
.fib-bar-bg{
  flex:1;height:4px;border-radius:2px;background:var(--bg4);overflow:hidden;
}
.fib-bar-fill{height:100%;border-radius:2px;transition:width .4s;background:linear-gradient(90deg,var(--gold),var(--gold2))}
.fib-bar-val{font-size:.62rem;color:var(--text2);font-family:'JetBrains Mono',monospace;min-width:28px;text-align:right}

.fib-levels-grid{
  display:grid;grid-template-columns:1fr 1fr;gap:3px;margin-bottom:10px;
}
.fib-lvl-row{
  display:flex;align-items:center;justify-content:space-between;
  padding:3px 7px;border-radius:4px;font-size:.6rem;
  font-family:'JetBrains Mono',monospace;border:1px solid transparent;
}
.fib-lvl-row.gz{background:rgba(201,168,76,.08);border-color:rgba(201,168,76,.2)}
.fib-lvl-row .l{color:var(--muted)}.fib-lvl-row .v{color:var(--text2);font-weight:500}
.fib-lvl-row.gz .l{color:var(--gold)}.fib-lvl-row.gz .v{color:var(--gold2)}

.fib-conds-list{display:flex;flex-direction:column;gap:4px}
.fib-cond-row{display:flex;align-items:center;gap:7px;font-size:.62rem;padding:3px 0;border-bottom:1px solid var(--border2)}
.fib-cond-row:last-child{border:none}
.fc-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.fc-dot.met{background:var(--green)}.fc-dot.miss{background:var(--muted)}
.fc-txt.met{color:var(--text)}.fc-txt.miss{color:var(--muted)}
.fc-pts{margin-left:auto;font-size:.6rem;font-family:'JetBrains Mono',monospace;flex-shrink:0}
.fc-pts.met{color:var(--green)}.fc-pts.miss{color:var(--muted)}

.ob-tags{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
.ob-tag{
  padding:2px 8px;border-radius:3px;font-size:.57rem;font-weight:600;
  font-family:'JetBrains Mono',monospace;
}
.ob-tag.bull{background:var(--green2);color:var(--green);border:1px solid rgba(0,229,160,.15)}
.ob-tag.bear{background:var(--red2);color:var(--red);border:1px solid rgba(255,51,85,.15)}

/* LIQ panel */
.liq-row{
  display:flex;align-items:center;justify-content:space-between;
  padding:5px 0;border-bottom:1px solid var(--border2);font-size:.65rem;
}
.liq-row:last-child{border:none}
.liq-type{color:var(--muted);font-size:.6rem}
.liq-badge{
  padding:1px 8px;border-radius:3px;font-size:.62rem;font-weight:600;
  font-family:'JetBrains Mono',monospace;
}
.liq-badge.buy{background:var(--green2);color:var(--green)}
.liq-badge.sell{background:var(--red2);color:var(--red)}
.liq-badge.eq{background:var(--blue2);color:var(--blue)}

.sweep-banner{
  margin-top:10px;padding:8px 12px;border-radius:6px;
  font-size:.65rem;display:flex;align-items:center;gap:8px;
}
.sweep-banner.bull{background:var(--green2);border:1px solid rgba(0,229,160,.15);color:var(--green)}
.sweep-banner.bear{background:var(--red2);border:1px solid rgba(255,51,85,.15);color:var(--red)}

/* MODEL panel */
.model-row{
  display:flex;align-items:center;justify-content:space-between;
  padding:5px 0;border-bottom:1px solid var(--border2);font-size:.65rem;
}
.model-row:last-child{border:none}
.model-key{color:var(--muted)}
.model-val{font-weight:600;font-family:'JetBrains Mono',monospace;color:var(--text2)}
.model-val.good{color:var(--green)}.model-val.warn{color:var(--gold)}.model-val.bad{color:var(--red)}

.btn-train{
  width:100%;margin-top:12px;padding:9px;border-radius:6px;cursor:pointer;
  background:transparent;border:1px solid var(--border);color:var(--gold);
  font-family:'JetBrains Mono',monospace;font-size:.67rem;font-weight:600;
  letter-spacing:1px;transition:.2s;text-transform:uppercase;
}
.btn-train:hover{background:var(--gold3);border-color:var(--gold)}
.btn-train:disabled{opacity:.3;cursor:not-allowed}
.train-msg{font-size:.58rem;color:var(--muted);text-align:center;margin-top:5px;min-height:12px}

/* ── LOADING ───────────────────────────────────────────────────────────────── */
.shimmer{
  height:2px;
  background:linear-gradient(90deg,transparent 0%,var(--gold) 50%,transparent 100%);
  background-size:200% 100%;
  animation:shimmer 1.4s linear infinite;
  border-radius:1px;
}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}

.spin{
  display:inline-block;width:10px;height:10px;
  border:2px solid rgba(201,168,76,.2);border-top-color:var(--gold);
  border-radius:50%;animation:sp .6s linear infinite;vertical-align:middle;
  margin-right:5px;
}
@keyframes sp{to{transform:rotate(360deg)}}

/* ── DIVIDERS ─────────────────────────────────────────────────────────────── */
.divider{height:1px;background:var(--border2);margin:8px 0}
</style>
</head>
<body>
<div class="layout">

<!-- ══ HEADER ══════════════════════════════════════════════════════════════ -->
<header>
  <div class="hdr-brand">
    <div class="brand-icon">⬡</div>
    <div>
      <div class="brand-name">GOLD AI</div>
      <div class="brand-sub">Trading Terminal</div>
    </div>
  </div>

  <div class="hdr-price">
    <div class="price-val mono" id="price">—</div>
    <div class="price-chg" id="pchg" style="display:none"></div>
  </div>

  <div class="hdr-stats">
    <div class="hdr-stat">
      <span class="lbl">High</span>
      <span class="val" id="p-h">—</span>
    </div>
    <div class="hdr-stat">
      <span class="lbl">Low</span>
      <span class="val" id="p-l">—</span>
    </div>
    <div class="hdr-stat">
      <span class="lbl">Symbol</span>
      <span class="val" style="color:var(--gold)">XAUUSD</span>
    </div>
  </div>

  <div class="hdr-right">
    <div class="status-pill">
      <span class="status-dot" id="wsdot"></span>
      <span id="wsts" style="color:var(--muted)">CONNECTING</span>
    </div>
    <div class="hdr-time mono" id="upd">—</div>
  </div>
</header>

<!-- ══ SIGNAL BAR ═══════════════════════════════════════════════════════════ -->
<div class="signal-bar" id="signal-bar">
  <!-- loading shimmer -->
  <div style="width:100%;padding:4px 0;background:var(--bg1)">
    <div class="shimmer" id="sig-loader" style="width:100%"></div>
  </div>
</div>

<!-- ══ TF ALIGNMENT ══════════════════════════════════════════════════════════ -->
<div class="tf-bar">
  <div class="tf-cell" id="tfc-monthly">
    <div class="tf-lbl">Monthly</div>
    <div class="tf-trend neutral" id="tf-monthly">—</div>
  </div>
  <div class="tf-cell" id="tfc-weekly">
    <div class="tf-lbl">Weekly</div>
    <div class="tf-trend neutral" id="tf-weekly">—</div>
  </div>
  <div class="tf-cell" id="tfc-daily">
    <div class="tf-lbl">Daily</div>
    <div class="tf-trend neutral" id="tf-daily">—</div>
  </div>
  <div class="tf-cell" id="tfc-h4">
    <div class="tf-lbl">H4</div>
    <div class="tf-trend neutral" id="tf-h4">—</div>
  </div>
  <div class="tf-cell" id="tfc-h1">
    <div class="tf-lbl">H1</div>
    <div class="tf-trend neutral" id="tf-h1">—</div>
  </div>
  <div class="tf-cell" id="tfc-m15">
    <div class="tf-lbl">15M</div>
    <div class="tf-trend neutral" id="tf-m15">—</div>
    <div class="tf-rsi" id="rsi-m15"></div>
  </div>
  <div class="tf-cell" id="tfc-m5">
    <div class="tf-lbl">5M</div>
    <div class="tf-trend neutral" id="tf-m5">—</div>
    <div class="tf-pat" id="pat-m5"></div>
  </div>
</div>

<!-- ══ MAIN ROW ══════════════════════════════════════════════════════════════ -->
<div class="main-row">

  <!-- LEFT: Chart -->
  <div class="left-col">
    <div class="chart-wrap">
      <div class="chart-toolbar">
        <div class="tf-tabs">
          <div class="tf-tab" onclick="switchTF('1m')">1M</div>
          <div class="tf-tab" onclick="switchTF('5m')">5M</div>
          <div class="tf-tab" onclick="switchTF('15m')">15M</div>
          <div class="tf-tab active" id="tab-1h" onclick="switchTF('1h')">1H</div>
          <div class="tf-tab" onclick="switchTF('4h')">4H</div>
          <div class="tf-tab" onclick="switchTF('1d')">D1</div>
          <div class="tf-tab" onclick="switchTF('1w')">W1</div>
        </div>
        <div class="chart-legend">
          <div class="leg-item"><div class="leg-line" style="background:#c9a84c"></div>EMA 9</div>
          <div class="leg-item"><div class="leg-line" style="background:#4499ff"></div>EMA 20</div>
          <div class="leg-item"><div class="leg-line" style="background:#ff9900"></div>EMA 50</div>
          <div class="leg-item"><div class="leg-line" style="background:#ff3355"></div>EMA 200</div>
          <div class="leg-item"><div class="leg-line" style="background:rgba(201,168,76,.6);border-top:1px dashed var(--gold)"></div>Fib GZ</div>
        </div>
        <div class="chart-info-badge" id="chart-info">loading…</div>
      </div>
      <div id="chart" style="flex:1;width:100%;min-height:460px"></div>
    </div>
  </div>

  <!-- RIGHT: Panels -->
  <div class="right-col">

    <!-- Fibonacci -->
    <div class="right-panel panel">
      <div class="panel-title"><span class="pticon">📐</span>Fibonacci · Golden Zone</div>
      <div id="fib-dir" class="fib-dir none">— Scanning</div>
      <div class="fib-sig wait" id="fib-signal">— WAIT</div>
      <div class="fib-quality-bar">
        <div class="fib-bar-bg"><div class="fib-bar-fill" id="fib-bar" style="width:0%"></div></div>
        <div class="fib-bar-val" id="fib-quality">0/100</div>
      </div>
      <div class="fib-levels-grid" id="fib-levels-grid">
        <div class="fib-lvl-row"><span class="l">—</span></div>
      </div>
      <div class="divider"></div>
      <div class="fib-conds-list" id="fib-conds"></div>
      <div class="ob-tags" id="fib-obs"></div>
    </div>

    <!-- Liquidity -->
    <div class="right-panel panel">
      <div class="panel-title"><span class="pticon">💧</span>Liquidity Pools</div>
      <div id="liq-content"><div style="color:var(--muted);font-size:.65rem">Loading…</div></div>
    </div>

    <!-- Model -->
    <div class="right-panel panel">
      <div class="panel-title"><span class="pticon">🤖</span>AI Model · OHLCV v0</div>
      <div class="model-row"><span class="model-key">Status</span><span class="model-val warn" id="m-st">—</span></div>
      <div class="model-row"><span class="model-key">Win Rate</span><span class="model-val" id="m-hit">—</span></div>
      <div class="model-row"><span class="model-key">Expectancy</span><span class="model-val" id="m-exp">—</span></div>
      <div class="model-row"><span class="model-key">Accuracy</span><span class="model-val" id="m-acc">—</span></div>
      <div class="model-row"><span class="model-key">Samples</span><span class="model-val" id="m-tr">—</span></div>
      <button class="btn-train" id="train-btn" onclick="trainModel()">⚡ Train Model</button>
      <div class="train-msg" id="tmsg"></div>
    </div>

  </div>
</div><!-- end main-row -->
</div><!-- end layout -->

<script>
const API = location.origin;
const WS  = (location.protocol==='https:'?'wss':'ws')+'://'+location.host+'/api/v1/ws/price';
let chart, candleSeries, lastPrice=0, ws, wsR=0;
let ema9S, ema20S, ema50S, ema200S;
let srLines=[], liqLines=[], fibLines=[], obLines=[];
let currentTF='1h';

const TF_LABELS={'1m':'1M','5m':'5M','15m':'15M','1h':'1H','4h':'4H','1d':'D1','1w':'W1'};
const TF_ICONS={bullish:'▲',bearish:'▼',neutral:'─',uptrend:'▲',downtrend:'▼',ranging:'↔'};

// ── FMT ──────────────────────────────────────────────────────────────────────
const fmt=n=>'$'+Number(n).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});

// ── CHART ─────────────────────────────────────────────────────────────────────
function initChart(){
  chart=LightweightCharts.createChart(document.getElementById('chart'),{
    layout:{background:{color:'#06060f'},textColor:'#3a4055'},
    grid:{vertLines:{color:'rgba(255,255,255,.025)'},horzLines:{color:'rgba(255,255,255,.025)'}},
    rightPriceScale:{borderColor:'rgba(201,168,76,.08)',scaleMargins:{top:.08,bottom:.08}},
    timeScale:{borderColor:'rgba(201,168,76,.08)',timeVisible:true,secondsVisible:false},
    crosshair:{mode:1,vertLine:{color:'rgba(201,168,76,.3)',width:1,style:2},
               horzLine:{color:'rgba(201,168,76,.3)',width:1,style:2}},
  });
  candleSeries=chart.addCandlestickSeries({
    upColor:'#00e5a0',downColor:'#ff3355',
    borderUpColor:'#00e5a0',borderDownColor:'#ff3355',
    wickUpColor:'rgba(0,229,160,.5)',wickDownColor:'rgba(255,51,85,.5)',
  });
  ema9S  =chart.addLineSeries({color:'#c9a84c',lineWidth:1,priceLineVisible:false,lastValueVisible:false});
  ema20S =chart.addLineSeries({color:'#4499ff',lineWidth:1,priceLineVisible:false,lastValueVisible:false});
  ema50S =chart.addLineSeries({color:'#ff9900',lineWidth:1,priceLineVisible:false,lastValueVisible:false});
  ema200S=chart.addLineSeries({color:'#ff3355',lineWidth:1,priceLineVisible:false,lastValueVisible:false});
  new ResizeObserver(()=>{
    const el=document.getElementById('chart');
    chart.applyOptions({width:el.clientWidth,height:el.clientHeight});
  }).observe(document.getElementById('chart'));
}

function clearOverlays(){
  [...srLines,...liqLines,...fibLines,...obLines].forEach(s=>{try{chart.removeSeries(s)}catch(e){}});
  srLines=[];liqLines=[];fibLines=[];obLines=[];
}

function addHLine(price,color,lw,style,title=''){
  const s=chart.addLineSeries({color,lineWidth:lw,lineStyle:style,
    priceLineVisible:false,lastValueVisible:!!title,
    title,crosshairMarkerVisible:false});
  return s;
}

// ── TF SWITCH ─────────────────────────────────────────────────────────────────
function switchTF(tf){
  currentTF=tf;
  document.querySelectorAll('.tf-tab').forEach(b=>b.classList.toggle('active',b.textContent===TF_LABELS[tf]));
  loadChart(tf);
}

// ── LOAD CHART ────────────────────────────────────────────────────────────────
async function loadChart(tf){
  tf=tf||currentTF;
  document.getElementById('chart-info').innerHTML='<span class="spin"></span>'+TF_LABELS[tf];
  clearOverlays();
  try{candleSeries.setData([])}catch(e){}
  try{ema9S.setData([]);ema20S.setData([]);ema50S.setData([]);ema200S.setData([])}catch(e){}
  try{
    const r=await fetch(API+'/api/v1/chart/data?tf='+tf+'&limit=300');
    if(!r.ok){document.getElementById('chart-info').textContent='Error '+r.status;return;}
    const d=await r.json();
    if(!d.candles||!d.candles.length){document.getElementById('chart-info').textContent='No data';return;}

    candleSeries.setData(d.candles);
    if(d.ema9  &&d.ema9.length)  ema9S.setData(d.ema9);
    if(d.ema20 &&d.ema20.length) ema20S.setData(d.ema20);
    if(d.ema50 &&d.ema50.length) ema50S.setData(d.ema50);
    if(d.ema200&&d.ema200.length)ema200S.setData(d.ema200);

    const t0=d.candles[0].time, t1=d.candles[d.candles.length-1].time;

    (d.resistances||[]).forEach(p=>{const s=addHLine(p,'rgba(255,255,255,.25)',1,2);s.setData([{time:t0,value:p},{time:t1,value:p}]);srLines.push(s)});
    (d.supports||[]).forEach(p=>{const s=addHLine(p,'rgba(255,255,255,.25)',1,2);s.setData([{time:t0,value:p},{time:t1,value:p}]);srLines.push(s)});
    (d.buy_side||[]).forEach(p=>{const s=addHLine(p,'rgba(0,229,160,.55)',1,2);s.setData([{time:t0,value:p},{time:t1,value:p}]);liqLines.push(s)});
    (d.sell_side||[]).forEach(p=>{const s=addHLine(p,'rgba(255,51,85,.55)',1,2);s.setData([{time:t0,value:p},{time:t1,value:p}]);liqLines.push(s)});
    (d.equal_highs||[]).forEach(p=>{const s=addHLine(p,'rgba(68,153,255,.4)',1,1);s.setData([{time:t0,value:p},{time:t1,value:p}]);liqLines.push(s)});
    (d.equal_lows||[]).forEach(p=>{const s=addHLine(p,'rgba(68,153,255,.4)',1,1);s.setData([{time:t0,value:p},{time:t1,value:p}]);liqLines.push(s)});

    // Fibonacci
    const fib=d.fib||{};
    if(fib.levels&&fib.swing_high){
      const fibCfg={
        '0.0':  {c:'rgba(160,160,200,.2)',lw:1,st:2,lbl:''},
        '0.236':{c:'rgba(160,160,200,.3)',lw:1,st:2,lbl:'0.236'},
        '0.382':{c:'rgba(100,180,255,.45)',lw:1,st:2,lbl:'0.382'},
        '0.5':  {c:'rgba(255,255,255,.3)',lw:1,st:0,lbl:'0.5'},
        '0.618':{c:'rgba(201,168,76,.85)',lw:2,st:0,lbl:'0.618 GZ'},
        '0.705':{c:'rgba(201,168,76,.4)',lw:1,st:2,lbl:''},
        '0.786':{c:'rgba(201,168,76,.85)',lw:2,st:0,lbl:'0.786 GZ'},
        '1.0':  {c:'rgba(160,160,200,.2)',lw:1,st:0,lbl:''},
        '1.272':{c:'rgba(68,153,255,.3)',lw:1,st:2,lbl:'1.272'},
        '1.618':{c:'rgba(68,153,255,.3)',lw:1,st:2,lbl:'1.618'},
      };
      Object.entries(fib.levels).forEach(([lvl,price])=>{
        const cfg=fibCfg[lvl]||{c:'rgba(200,200,200,.2)',lw:1,st:2,lbl:''};
        const s=chart.addLineSeries({color:cfg.c,lineWidth:cfg.lw,lineStyle:cfg.st,
          priceLineVisible:false,lastValueVisible:!!cfg.lbl,
          title:cfg.lbl,crosshairMarkerVisible:false});
        s.setData([{time:t0,value:price},{time:t1,value:price}]);
        fibLines.push(s);
      });
      // Swing markers
      const mk=[];
      const shI=d.candles.findIndex(c=>Math.abs(c.high-fib.swing_high)<3);
      const slI=d.candles.findIndex(c=>Math.abs(c.low -fib.swing_low )<3);
      if(shI>=0)mk.push({time:d.candles[shI].time,position:'aboveBar',color:'#c9a84c',shape:'circle',text:'SH'});
      if(slI>=0)mk.push({time:d.candles[slI].time,position:'belowBar',color:'#c9a84c',shape:'circle',text:'SL'});
      const allMk=[...(d.markers||[]),...mk].sort((a,b)=>a.time-b.time);
      candleSeries.setMarkers(allMk);

      // Order blocks
      (fib.order_blocks||[]).forEach(ob=>{
        const bull=ob.type==='bullish';
        const top=addHLine(ob.top,bull?'rgba(0,229,160,.6)':'rgba(255,51,85,.6)',1,0,bull?'OB↑':'OB↓');
        const bot=addHLine(ob.bottom,bull?'rgba(0,229,160,.3)':'rgba(255,51,85,.3)',1,2);
        top.setData([{time:t0,value:ob.top},   {time:t1,value:ob.top}]);
        bot.setData([{time:t0,value:ob.bottom},{time:t1,value:ob.bottom}]);
        obLines.push(top,bot);
      });
      updateFibCard(fib);
    } else {
      candleSeries.setMarkers(d.markers||[]);
    }

    chart.timeScale().fitContent();
    document.getElementById('chart-info').textContent=d.candles.length+' · '+TF_LABELS[tf];
  }catch(e){document.getElementById('chart-info').textContent='Error: '+e.message;}
}

// ── FIB CARD ──────────────────────────────────────────────────────────────────
function updateFibCard(fib){
  if(!fib||!fib.swing_high)return;
  const sig=fib.signal||'wait';
  // direction badge
  const dirEl=document.getElementById('fib-dir');
  if(fib.direction==='up'){dirEl.className='fib-dir up';dirEl.textContent='↑ BULLISH SETUP  SL '+fmt(fib.swing_low)+' → SH '+fmt(fib.swing_high);}
  else if(fib.direction==='down'){dirEl.className='fib-dir down';dirEl.textContent='↓ BEARISH SETUP  SH '+fmt(fib.swing_high)+' → SL '+fmt(fib.swing_low);}
  else{dirEl.className='fib-dir none';dirEl.textContent='— Scanning…';}
  // signal
  const sigEl=document.getElementById('fib-signal');
  sigEl.className='fib-sig '+sig;
  sigEl.textContent=sig==='buy'?'▲ BUY  GOLDEN ZONE':sig==='sell'?'▼ SELL  GOLDEN ZONE':'── WAIT';
  // quality bar
  const q=fib.quality||0;
  document.getElementById('fib-bar').style.width=q+'%';
  document.getElementById('fib-quality').textContent=q+'/100';
  // levels
  const gz=fib.golden_zone||{};
  const levHtml=Object.entries(fib.levels||{}).map(([lvl,price])=>{
    const isGZ=(['0.618','0.705','0.786'].includes(lvl));
    return`<div class="fib-lvl-row${isGZ?' gz':''}"><span class="l">${lvl}</span><span class="v">${fmt(price)}</span></div>`;
  }).join('');
  document.getElementById('fib-levels-grid').innerHTML=levHtml;
  // conditions
  document.getElementById('fib-conds').innerHTML=(fib.conditions||[]).map(c=>
    `<div class="fib-cond-row">
      <div class="fc-dot ${c.met?'met':'miss'}"></div>
      <span class="fc-txt ${c.met?'met':'miss'}">${c.detail}</span>
      <span class="fc-pts ${c.met?'met':'miss'}">${c.met?'+':''}${c.weight}</span>
    </div>`).join('');
  // OBs
  document.getElementById('fib-obs').innerHTML=(fib.order_blocks||[]).map(ob=>
    `<div class="ob-tag ${ob.type==='bullish'?'bull':'bear'}">${ob.type==='bullish'?'▲':'▼'} ${fmt(ob.bottom)}–${fmt(ob.top)}</div>`
  ).join('');
}

async function loadFib(){
  try{
    const r=await fetch(API+'/api/v1/fib/gold?tf=15m');
    const d=await r.json();
    updateFibCard({signal:d.entry_signal,quality:d.entry_quality,direction:d.direction,
      swing_high:d.swing_high,swing_low:d.swing_low,levels:d.fib_levels,
      golden_zone:d.golden_zone,order_blocks:d.order_blocks,conditions:d.conditions});
  }catch(e){}
}

// ── WEBSOCKET ─────────────────────────────────────────────────────────────────
function connectWS(){
  ws=new WebSocket(WS);
  ws.onopen=()=>{
    document.getElementById('wsdot').className='status-dot live';
    document.getElementById('wsts').textContent='LIVE';
    document.getElementById('wsts').style.color='var(--green)';
    wsR=0;
  };
  ws.onmessage=(e)=>{updatePrice(JSON.parse(e.data))};
  ws.onclose=()=>{
    document.getElementById('wsdot').className='status-dot';
    document.getElementById('wsts').textContent='RECONNECTING';
    document.getElementById('wsts').style.color='var(--gold)';
    wsR=Math.min(wsR+1,5);
    setTimeout(connectWS,wsR*2000);
  };
  ws.onerror=()=>ws.close();
}

function updatePrice(d){
  const p=d.price,pr=d.prev||lastPrice||p;
  const dir=p>=pr?'up':'down';
  const el=document.getElementById('price');
  el.textContent=fmt(p);el.className='price-val mono '+dir;
  setTimeout(()=>el.className='price-val mono',600);
  const chg=d.change_pct||0;
  const ce=document.getElementById('pchg');
  ce.textContent=(chg>0?'+':'')+chg.toFixed(2)+'%';
  ce.className='price-chg '+(chg>=0?'up':'down');
  ce.style.display='inline-flex';
  if(d.high)document.getElementById('p-h').textContent=fmt(d.high);
  if(d.low) document.getElementById('p-l').textContent=fmt(d.low);
  if(candleSeries&&lastPrice!==p){
    const now=Math.floor(Date.now()/1000),ht=Math.floor(now/3600)*3600;
    try{candleSeries.update({time:ht,open:pr,high:Math.max(pr,p),low:Math.min(pr,p),close:p})}catch(e){}
  }
  lastPrice=p;
  document.getElementById('upd').textContent=new Date().toLocaleTimeString();
}

// ── ANALYSIS ──────────────────────────────────────────────────────────────────
async function loadAnalysis(){
  try{
    const r=await fetch(API+'/api/v1/analysis/gold');
    const d=await r.json();

    // Build signal bar
    const es=d.entry_signal||{};
    const action=es.action||'wait';
    const conf=es.confidence||0;
    const price=d.price||0;

    const sigBarHtml=`
      <div class="sig-main" style="background:var(--bg1)">
        <div class="sig-score-ring ${action}">
          <div class="sig-score-num">${conf.toFixed(0)}</div>
          <div class="sig-score-lbl">SCORE</div>
        </div>
        <div>
          <div class="sig-action ${action}">${action==='buy'?'▲ BUY':action==='sell'?'▼ SELL':'— WAIT'}</div>
          <div style="font-size:.6rem;color:var(--muted);margin-top:2px">${es.macro_bias||'—'} bias · ${es.score||0}/${es.max_score||100}pts</div>
        </div>
      </div>
      <div class="sig-levels">
        <div class="sig-lvl"><div class="lbl">Entry</div><div class="val entry">${price?fmt(price):'—'}</div></div>
        <div class="sig-lvl"><div class="lbl">Stop Loss</div><div class="val sl">${es.suggested_sl?fmt(es.suggested_sl):'—'}</div></div>
        <div class="sig-lvl"><div class="lbl">Take Profit</div><div class="val tp">${es.suggested_tp?fmt(es.suggested_tp):'—'}</div></div>
        <div class="sig-lvl"><div class="lbl">R : R</div><div class="val rr">${es.rr?'1 : '+es.rr:'—'}</div></div>
      </div>
      <div class="sig-conds">
        ${[...(es.conditions_met||[]).map(c=>`<div class="cond-row"><span class="cond-icon" style="color:var(--green)">✓</span><span class="met">${c.detail}</span><span class="cond-pts met">+${c.weight}</span></div>`),
           ...(es.conditions_missing||[]).map(c=>`<div class="cond-row"><span class="cond-icon" style="color:var(--muted)">○</span><span class="miss">${c.detail}</span><span class="cond-pts miss">${c.weight}</span></div>`)
          ].slice(0,5).join('')}
      </div>`;
    document.getElementById('signal-bar').innerHTML=sigBarHtml;
    document.getElementById('signal-bar').style.background='var(--border)';

    // TF table
    const tfs=d.timeframes||{};
    ['monthly','weekly','daily','h4','h1','m15','m5'].forEach(k=>{
      const tf=tfs[k]||{};
      const trend=tf.trend||'neutral';
      const el=document.getElementById('tf-'+k);
      if(el){el.textContent=(TF_ICONS[trend]||'─')+' '+trend.toUpperCase();el.className='tf-trend '+trend;}
      const rsiEl=document.getElementById('rsi-'+k);
      if(rsiEl&&tf.rsi)rsiEl.textContent='RSI '+tf.rsi.toFixed(0);
      const patEl=document.getElementById('pat-'+k);
      if(patEl){const pats=tf.patterns||[];patEl.textContent=pats.length?pats[0].pattern:'';}
    });

    // Liquidity
    const liq=d.liquidity||{};
    let liqH='';
    (liq.buy_side||[]).slice(0,3).forEach(v=>liqH+=`<div class="liq-row"><span class="liq-type">Buy-Side Stop</span><span class="liq-badge buy">${fmt(v)}</span></div>`);
    (liq.sell_side||[]).slice(0,3).forEach(v=>liqH+=`<div class="liq-row"><span class="liq-type">Sell-Side Stop</span><span class="liq-badge sell">${fmt(v)}</span></div>`);
    (liq.equal_highs||[]).slice(0,2).forEach(v=>liqH+=`<div class="liq-row"><span class="liq-type">Equal Highs</span><span class="liq-badge eq">${fmt(v)}</span></div>`);
    (liq.equal_lows||[]).slice(0,2).forEach(v=>liqH+=`<div class="liq-row"><span class="liq-type">Equal Lows</span><span class="liq-badge eq">${fmt(v)}</span></div>`);
    if(liq.last_sweep){
      const sw=liq.last_sweep;
      liqH+=`<div class="sweep-banner ${sw.direction==='bullish'?'bull':'bear'}">⚡ ${sw.type} @ ${fmt(sw.level)}</div>`;
    }
    document.getElementById('liq-content').innerHTML=liqH||'<div style="color:var(--muted);font-size:.65rem">No liquidity data</div>';

  }catch(e){}
}

// ── HEALTH ────────────────────────────────────────────────────────────────────
async function loadHealth(){
  try{
    const r=await fetch(API+'/health');
    const d=await r.json();
    const m=(d.models||{}).ohlcv_v0||{};
    const mt=m.metrics||{};
    document.getElementById('m-st').textContent=m.trained?'✅ Trained':'⚠ Not Trained';
    document.getElementById('m-st').className='model-val '+(m.trained?'good':'warn');
    if(m.trained){
      const hit=((mt.hit_rate||0)*100).toFixed(1)+'%';
      document.getElementById('m-hit').textContent=hit;
      document.getElementById('m-hit').className='model-val good';
      const ex=mt.expectancy_per_R||0;
      document.getElementById('m-exp').textContent=(ex>0?'+':'')+ex.toFixed(3)+'R';
      document.getElementById('m-exp').className='model-val '+(ex>0?'good':'bad');
      document.getElementById('m-acc').textContent=((mt.accuracy||0)*100).toFixed(1)+'%';
      document.getElementById('m-tr').textContent=(mt.train_samples||0).toLocaleString();
      document.getElementById('train-btn').textContent='↺ Re-Train Model';
    }
  }catch(e){}
}

// ── TRAIN ─────────────────────────────────────────────────────────────────────
async function trainModel(){
  const btn=document.getElementById('train-btn'),msg=document.getElementById('tmsg');
  btn.disabled=true;btn.innerHTML='<span class="spin"></span>Training…';msg.textContent='Fetching 2y data…';
  try{
    await fetch(API+'/api/v1/model/train',{method:'POST'});
    let p=0;
    const iv=setInterval(async()=>{
      p++;
      const sd=await (await fetch(API+'/api/v1/model/status')).json();
      if(!sd.training_running||p>80){
        clearInterval(iv);
        if(sd.trained){btn.disabled=false;btn.textContent='↺ Re-Train Model';msg.textContent='✅ Done';loadHealth();}
        else{btn.disabled=false;btn.textContent='⚡ Train Model';msg.textContent='Error: '+(sd.last_result?.error||'?');}
      }else btn.innerHTML='<span class="spin"></span>Training ('+p*5+'s)…';
    },5000);
  }catch(e){btn.disabled=false;btn.textContent='⚡ Train Model';msg.textContent='Error: '+e.message;}
}

// ── INIT ──────────────────────────────────────────────────────────────────────
initChart();
connectWS();
loadChart('1h');
loadAnalysis();
loadHealth();
loadFib();

setInterval(loadAnalysis, 180000);
setInterval(()=>loadChart(currentTF), 300000);
setInterval(loadFib, 120000);
</script>
</body></html>"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    return HTML
