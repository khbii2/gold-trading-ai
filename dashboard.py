"""
dashboard.py — Gold Trading AI Dashboard
Streamlit frontend يتصل بـ FastAPI backend

تشغيل:
  streamlit run dashboard.py
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
import httpx
from datetime import datetime

API = "http://localhost:8000"

st.set_page_config(
    page_title = "Gold Trading AI",
    page_icon  = "🥇",
    layout     = "wide",
    initial_sidebar_state = "collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
.stApp { background: #05050f; }
h1, h2, h3 { color: #d4af37 !important; font-family: 'JetBrains Mono' !important; }
[data-testid="stMetricValue"] { color: #d4af37 !important; font-size: 1.4rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<h1 style="text-align:center;font-size:2rem;margin-bottom:0">🥇 Gold Trading AI</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="text-align:center;color:#555;font-size:0.85rem;margin-top:4px">XAUUSD · OHLCV v0 · ML Bias</p>',
    unsafe_allow_html=True,
)

col_refresh, _ = st.columns([1, 9])
with col_refresh:
    if st.button("🔄"):
        st.cache_data.clear()
        st.rerun()

# ── Data fetchers ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def api_signal():
    try:
        r = httpx.get(f"{API}/api/v1/signals/gold", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

@st.cache_data(ttl=60)
def api_health():
    try:
        r = httpx.get(f"{API}/health", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

@st.cache_data(ttl=60)
def api_signal_history():
    try:
        r = httpx.get(f"{API}/api/v1/signals/gold/history?limit=50", timeout=10)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

@st.cache_data(ttl=30)
def chart_data():
    try:
        d = yf.download("GC=F", period="5d", interval="1h", progress=False)
        if isinstance(d, tuple): d = d[0]
        d.columns = [c[0].lower() if isinstance(c, tuple) else c.lower() for c in d.columns]
        return d.dropna()
    except Exception:
        return pd.DataFrame()

signal  = api_signal()
health  = api_health()
history = api_signal_history()
df      = chart_data()

# ── API status warning ────────────────────────────────────────────────────────
if signal is None:
    st.warning(
        "⚠️ الـ API غير متصل.\n\n"
        "**1.** `python train_model.py`\n\n"
        "**2.** `uvicorn app.main:app --reload --port 8000`",
        icon="🔌",
    )

st.divider()

# ── Metrics row ───────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

if signal:
    price = signal.get("price", 0)
    bias  = signal.get("bias", "neutral")
    conf  = signal.get("confidence", 0)
    feats = signal.get("key_features", {})
    rsi   = feats.get("rsi_14", 0)
    ret1h = feats.get("ret_1h", 0)

    bias_label = {"buy": "▲ BUY", "sell": "▼ SELL", "neutral": "── WAIT"}.get(bias, bias)

    c1.metric("السعر",   f"${price:,.2f}")
    c2.metric("الإشارة", bias_label)
    c3.metric("الثقة",   f"{conf*100:.1f}%")
    c4.metric("RSI",     f"{rsi:.1f}")
    c5.metric("Ret 1h",  f"{ret1h:+.3f}%")
elif not df.empty:
    price = float(df["close"].iloc[-1])
    c1.metric("السعر", f"${price:,.2f}")

# ── Chart ─────────────────────────────────────────────────────────────────────
if not df.empty:
    df_c = df.copy()
    df_c["ma20"] = df_c["close"].rolling(20).mean()
    df_c["ma50"] = df_c["close"].rolling(50).mean()

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df_c.index,
        open=df_c["open"], high=df_c["high"],
        low=df_c["low"],   close=df_c["close"],
        increasing=dict(line=dict(color="#00e5a0", width=1), fillcolor="rgba(0,229,160,0.75)"),
        decreasing=dict(line=dict(color="#ff4466", width=1), fillcolor="rgba(255,68,102,0.75)"),
        name="XAUUSD",
    ))
    fig.add_trace(go.Scatter(
        x=df_c.index, y=df_c["ma20"],
        line=dict(color="#d4af37", width=1.2), name="MA20", opacity=0.8,
    ))
    fig.add_trace(go.Scatter(
        x=df_c.index, y=df_c["ma50"],
        line=dict(color="#555", width=1), name="MA50", opacity=0.7,
    ))

    # AI signal annotation
    if signal and signal.get("bias") in ("buy", "sell"):
        b     = signal["bias"]
        col_  = "#00e5a0" if b == "buy" else "#ff4466"
        arrow = "▲" if b == "buy" else "▼"
        fig.add_annotation(
            x=df_c.index[-1], y=float(df_c["close"].iloc[-1]),
            text=f"{arrow} AI {b.upper()} ({signal['confidence']*100:.0f}%)",
            font=dict(color=col_, size=14, family="JetBrains Mono"),
            showarrow=True, arrowcolor=col_, arrowhead=2,
            ax=-100, ay=-50,
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#05050f",
        plot_bgcolor="#05050f",
        height=500,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        margin=dict(l=60, r=20, t=30, b=20),
        font=dict(family="JetBrains Mono", color="#777", size=11),
        yaxis=dict(gridcolor="rgba(212,175,55,0.04)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.03)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#444")),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Bottom row ────────────────────────────────────────────────────────────────
col_model, col_hist = st.columns([1, 2])

with col_model:
    st.markdown("#### 🤖 النموذج")
    if health:
        m = health.get("models", {}).get("ohlcv_v0", {})
        mt = m.get("metrics", {})
        if mt:
            st.metric("دقة",        f"{mt.get('accuracy', 0)*100:.1f}%")
            st.metric("Hit Rate",   f"{mt.get('hit_rate', 0)*100:.1f}%")
            st.metric("Expectancy", f"{mt.get('expectancy_per_R', 0):+.3f}R")
            st.caption(f"تدريب: {mt.get('train_samples', 0):,} شمعة")
            st.caption(f"تحقق: {mt.get('val_samples', 0):,} شمعة")
        else:
            st.info("النموذج غير مدرب — شغّل `python train_model.py`")
    if signal:
        with st.expander("features"):
            st.json(signal.get("key_features", {}))

with col_hist:
    st.markdown("#### 📋 سجل الإشارات")
    if history:
        rows = []
        for h_ in history[:20]:
            bias_ = h_["bias"]
            icon  = "▲" if bias_ == "buy" else ("▼" if bias_ == "sell" else "─")
            rows.append({
                "الوقت":    h_["ts"][:16].replace("T", " "),
                "الإشارة":  f"{icon} {bias_}",
                "الثقة":    f"{h_['confidence']*100:.1f}%",
                "Score":    f"{h_['score']:+.3f}",
            })
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("لا سجل بعد — الإشارات تُحفظ تلقائياً عند استدعاء /signals/gold")
