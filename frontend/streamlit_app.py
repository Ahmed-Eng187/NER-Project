"""
Resume NER — Streamlit Frontend
Connects to the FastAPI backend (app.py / main.py) running on localhost:8000
"""

import streamlit as st
import requests
import json
import os

API_KEY = os.getenv("API_KEY", "default-dev-key")
HEADERS = {"X-API-Key": API_KEY}

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume NER — Entity Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Cards */
.ner-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
    transition: transform 0.2s, box-shadow 0.2s;
}
.ner-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99,102,241,0.25);
}

/* Entity badge */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 2px 3px;
    letter-spacing: 0.02em;
}

/* Routing pill */
.pill-auto    { background:#10b981; color:#fff; padding:3px 12px; border-radius:999px; font-size:0.8rem; font-weight:600; }
.pill-flagged { background:#f59e0b; color:#fff; padding:3px 12px; border-radius:999px; font-size:0.8rem; font-weight:600; }
.pill-review  { background:#ef4444; color:#fff; padding:3px 12px; border-radius:999px; font-size:0.8rem; font-weight:600; }

/* Metric box */
.metric-box {
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    text-align: center;
}
.metric-box .val { font-size: 1.7rem; font-weight: 700; color: #818cf8; }
.metric-box .lbl { font-size: 0.78rem; color: #94a3b8; margin-top: 2px; }

/* Section headers */
.section-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.4rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.55rem 1.4rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(99,102,241,0.4);
}

/* Textarea / inputs */
.stTextArea textarea, .stTextInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* Slider */
.stSlider > div { color: #e2e8f0; }

/* Hide default header */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────
API_BASE = os.getenv("BACKEND_URL", "http://localhost:8000")

ENTITY_COLORS = {
    "name":             ("#6366f1", "#fff"),
    "designation":      ("#8b5cf6", "#fff"),
    "email_address":    ("#06b6d4", "#fff"),
    "location":         ("#10b981", "#fff"),
    "companies":        ("#f59e0b", "#1e1e1e"),
    "degree":           ("#ec4899", "#fff"),
    "college_name":     ("#14b8a6", "#fff"),
    "graduation_year":  ("#a78bfa", "#fff"),
    "years_experience": ("#fb923c", "#fff"),
    "skills":           ("#22d3ee", "#1e1e1e"),
    "links":            ("#84cc16", "#1e1e1e"),
}

ENTITY_ICONS = {
    "name":             "👤",
    "designation":      "💼",
    "email_address":    "📧",
    "location":         "📍",
    "companies":        "🏢",
    "degree":           "🎓",
    "college_name":     "🏛️",
    "graduation_year":  "📅",
    "years_experience": "⏱️",
    "skills":           "🛠️",
    "links":            "🔗",
}

ENTITY_LABELS = {
    "name":             "Name",
    "designation":      "Designation",
    "email_address":    "Email",
    "location":         "Location",
    "companies":        "Companies",
    "degree":           "Degree",
    "college_name":     "College",
    "graduation_year":  "Grad Year",
    "years_experience": "Experience",
    "skills":           "Skills",
    "links":            "Links",
}

# ── Helpers ────────────────────────────────────────────────────────
def check_api():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200, r.json() if r.status_code == 200 else {}
    except Exception:
        return False, {}

def parse_text(text, conf, tta):
    r = requests.post(
        f"{API_BASE}/parse/text",
        json={"text": text, "conf": conf, "tta": tta},
        headers=HEADERS,
        timeout=120,
    )
    r.raise_for_status()
    return r.json()

def parse_pdf(file_bytes, filename):
    r = requests.post(
        f"{API_BASE}/parse/pdf",
        files={"file": (filename, file_bytes, "application/pdf")},
        headers=HEADERS,
        timeout=120,
    )
    r.raise_for_status()
    return r.json()

def get_review_queue(status_filter=None):
    url = f"{API_BASE}/review/queue"
    if status_filter and status_filter != "all":
        url += f"?status={status_filter}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def decide_review(queue_id, action, reviewer, correction=None):
    payload = {"action": action, "reviewer": reviewer, "correction": correction}
    r = requests.post(f"{API_BASE}/review/queue/{queue_id}/decide", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def render_routing_pill(routing):
    cls = {"auto": "pill-auto", "flagged": "pill-flagged", "review": "pill-review"}.get(routing, "pill-auto")
    label = {"auto": "✅ Auto-Accepted", "flagged": "⚠️ Flagged", "review": "🔍 Needs Review"}.get(routing, routing)
    return f'<span class="{cls}">{label}</span>'

def render_entity_section(key, values):
    if not values:
        return
    color_bg, color_fg = ENTITY_COLORS.get(key, ("#6366f1", "#fff"))
    icon  = ENTITY_ICONS.get(key, "•")
    label = ENTITY_LABELS.get(key, key.replace("_", " ").title())

    badges = " ".join(
        f'<span class="badge" style="background:{color_bg};color:{color_fg};">{v}</span>'
        for v in values
    )
    st.markdown(f"""
    <div class="ner-card">
      <div class="section-title">{icon} {label}</div>
      <div style="margin-top:6px">{badges}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    conf = st.slider("Confidence Threshold", 0.0, 1.0, 0.50, 0.05,
                     help="Minimum confidence to accept an entity")
    tta  = st.slider("TTA Runs", 0, 5, 3, 1,
                     help="Test-Time Augmentation passes (higher = slower but more accurate)")

    st.markdown("---")
    st.markdown("### 🔌 API Status")
    ok, health = check_api()
    if ok:
        st.success("Backend online")
        st.caption(f"Device: `{health.get('device','?')}`  |  Labels: `{health.get('labels','?')}`")
        pending = health.get("queue_pending", 0)
        if pending:
            st.warning(f"⏳ {pending} item(s) pending review")
    else:
        st.error("Backend offline — start the FastAPI server first")
        st.code("uvicorn app:app --reload", language="bash")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption(
        "Resume NER v7 · BERT-base + LoRA (r=32, α=64)\n\n"
        "Test F1: **0.8368** · Val F1: **0.8324** · Skills F1: **0.7273**"
    )

# ── Main ───────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;">
  <h1 style="font-size:2.6rem;font-weight:700;
             background:linear-gradient(135deg,#818cf8,#c084fc,#22d3ee);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
    📄 Resume NER
  </h1>
  <p style="color:#94a3b8;font-size:1.05rem;margin-top:-0.5rem;">
    Extract structured entities from resumes using BERT&nbsp;+&nbsp;LoRA
  </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["✍️ Paste Text", "📎 Upload PDF", "🔍 Review Queue"])

# ── Tab 1: Text ────────────────────────────────────────────────────
with tab1:
    text_input = st.text_area(
        "Paste resume text here",
        height=280,
        placeholder="John Doe\nSoftware Engineer at Google\njohn@example.com\nSkills: Python, TensorFlow, Docker ...",
        label_visibility="collapsed",
    )
    col_btn, col_clr = st.columns([1, 5])
    with col_btn:
        run_text = st.button("🔍 Extract", key="extract_text", use_container_width=True)

    if run_text:
        if not text_input.strip():
            st.warning("Please paste some resume text.")
        elif not ok:
            st.error("API is offline. Start the FastAPI backend first.")
        else:
            with st.spinner("Analysing resume…"):
                try:
                    result = parse_text(text_input, conf, tta)
                    st.session_state["result"] = result
                except Exception as e:
                    st.error(f"API error: {e}")

# ── Tab 2: PDF ─────────────────────────────────────────────────────
with tab2:
    uploaded = st.file_uploader("Upload a PDF resume", type=["pdf"], label_visibility="collapsed")
    run_pdf  = st.button("🔍 Extract from PDF", key="extract_pdf", use_container_width=False)

    if run_pdf:
        if not uploaded:
            st.warning("Please upload a PDF file.")
        elif not ok:
            st.error("API is offline. Start the FastAPI backend first.")
        else:
            with st.spinner("Parsing PDF and analysing…"):
                try:
                    result = parse_pdf(uploaded.read(), uploaded.name)
                    st.session_state["result"] = result
                except Exception as e:
                    st.error(f"API error: {e}")

# ── Results ────────────────────────────────────────────────────────
if "result" in st.session_state:
    res   = st.session_state["result"]
    ents  = res.get("entities", {})
    conf_ = res.get("confidence", 0)
    lat   = res.get("latency_ms", 0)
    route = res.get("routing", "auto")
    rid   = res.get("request_id", "")

    st.markdown("---")
    st.markdown("## 📊 Results")

    # ── Metrics row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-box"><div class="val">{conf_:.0%}</div><div class="lbl">Confidence</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-box"><div class="val">{lat:.0f}ms</div><div class="lbl">Latency</div></div>', unsafe_allow_html=True)
    with m3:
        non_empty = sum(1 for k, v in ents.items() if k != "raw" and v)
        st.markdown(f'<div class="metric-box"><div class="val">{non_empty}</div><div class="lbl">Entity Types Found</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-box"><div class="val" style="font-size:1rem;padding-top:6px">{render_routing_pill(route)}</div><div class="lbl">Routing</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Entity cards
    col_left, col_right = st.columns(2)
    keys_left  = ["name", "designation", "email_address", "location", "companies"]
    keys_right = ["degree", "college_name", "graduation_year", "years_experience", "links"]

    with col_left:
        for k in keys_left:
            render_entity_section(k, ents.get(k, []))

    with col_right:
        for k in keys_right:
            render_entity_section(k, ents.get(k, []))

    # ── Skills full-width
    skills = ents.get("skills", [])
    if skills:
        color_bg, color_fg = ENTITY_COLORS["skills"]
        badges = " ".join(
            f'<span class="badge" style="background:{color_bg};color:{color_fg};">{s}</span>'
            for s in skills
        )
        st.markdown(f"""
        <div class="ner-card">
          <div class="section-title">🛠️ Skills ({len(skills)})</div>
          <div style="margin-top:8px;line-height:2.2">{badges}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Review queue notice
    if route == "review":
        qid = res.get("review_queue_id", "")
        st.info(f"🔍 This result was sent to the Review Queue (confidence too low).\n\n**Queue ID:** `{qid}`  ·  Go to the **🔍 Review Queue** tab to action it.")

    # ── Raw JSON expander
    with st.expander("🔧 Raw JSON response"):
        st.json(res)

    # ── Download
    st.download_button(
        "⬇️ Download JSON",
        data=json.dumps(res, indent=2),
        file_name="resume_ner_result.json",
        mime="application/json",
    )

# ── Tab 3: Review Queue ────────────────────────────────────────────
with tab3:
    st.markdown("### 🔍 Low-Confidence CV Review Queue")
    st.caption("CVs with confidence < 60% are routed here for human review. Approve or correct them below.")

    col_filter, col_refresh = st.columns([3, 1])
    with col_filter:
        status_filter = st.selectbox(
            "Filter by status",
            ["all", "pending", "approved", "corrected"],
            index=0,
            label_visibility="collapsed",
        )
    with col_refresh:
        refresh_btn = st.button("🔄 Refresh", key="refresh_queue", use_container_width=True)

    if not ok:
        st.error("API is offline — start the FastAPI backend first.")
    else:
        try:
            queue_items = get_review_queue(status_filter)
        except Exception as e:
            st.error(f"Could not fetch queue: {e}")
            queue_items = []

        if not queue_items:
            st.markdown("""
            <div style="text-align:center;padding:3rem 0;color:#64748b;">
              <div style="font-size:3rem;">📭</div>
              <div style="font-size:1.1rem;margin-top:0.5rem;">No items in the review queue</div>
              <div style="font-size:0.85rem;margin-top:0.3rem;">CVs with confidence &lt; 50% will appear here</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Summary counts
            total   = len(queue_items)
            pending = sum(1 for q in queue_items if q["status"] == "pending")
            approved = sum(1 for q in queue_items if q["status"] == "approved")
            corrected = sum(1 for q in queue_items if q["status"] == "corrected")

            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.markdown(f'<div class="metric-box"><div class="val">{total}</div><div class="lbl">Total</div></div>', unsafe_allow_html=True)
            sc2.markdown(f'<div class="metric-box"><div class="val" style="color:#ef4444">{pending}</div><div class="lbl">Pending</div></div>', unsafe_allow_html=True)
            sc3.markdown(f'<div class="metric-box"><div class="val" style="color:#10b981">{approved}</div><div class="lbl">Approved</div></div>', unsafe_allow_html=True)
            sc4.markdown(f'<div class="metric-box"><div class="val" style="color:#f59e0b">{corrected}</div><div class="lbl">Corrected</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            for item in queue_items:
                qid    = item["queue_id"]
                conf_v = item["confidence"]
                status = item["status"]
                queued = item["queued_at"][:19].replace("T", " ")
                ents_q = item.get("entities", {})

                # Status badge color
                status_color = {"pending": "#ef4444", "approved": "#10b981", "corrected": "#f59e0b"}.get(status, "#6366f1")
                status_icon  = {"pending": "⏳", "approved": "✅", "corrected": "✏️"}.get(status, "•")

                with st.expander(
                    f"{status_icon} [{status.upper()}]  Conf: {conf_v:.0%}  ·  {queued}  ·  ID: {qid[:8]}…",
                    expanded=(status == "pending"),
                ):
                    # Entity summary
                    left_e, right_e = st.columns(2)
                    entity_keys_left  = ["name", "designation", "email_address", "location", "companies"]
                    entity_keys_right = ["degree", "college_name", "graduation_year", "years_experience"]

                    with left_e:
                        for k in entity_keys_left:
                            vals = ents_q.get(k, [])
                            if vals:
                                bg, fg = ENTITY_COLORS.get(k, ("#6366f1", "#fff"))
                                icon = ENTITY_ICONS.get(k, "•")
                                lbl  = ENTITY_LABELS.get(k, k)
                                badges = " ".join(f'<span class="badge" style="background:{bg};color:{fg};">{v}</span>' for v in vals)
                                st.markdown(f'<div class="ner-card"><div class="section-title">{icon} {lbl}</div><div style="margin-top:4px">{badges}</div></div>', unsafe_allow_html=True)

                    with right_e:
                        for k in entity_keys_right:
                            vals = ents_q.get(k, [])
                            if vals:
                                bg, fg = ENTITY_COLORS.get(k, ("#6366f1", "#fff"))
                                icon = ENTITY_ICONS.get(k, "•")
                                lbl  = ENTITY_LABELS.get(k, k)
                                badges = " ".join(f'<span class="badge" style="background:{bg};color:{fg};">{v}</span>' for v in vals)
                                st.markdown(f'<div class="ner-card"><div class="section-title">{icon} {lbl}</div><div style="margin-top:4px">{badges}</div></div>', unsafe_allow_html=True)

                    # Skills
                    skills_q = ents_q.get("skills", [])
                    if skills_q:
                        bg, fg = ENTITY_COLORS["skills"]
                        badges = " ".join(f'<span class="badge" style="background:{bg};color:{fg};">{s}</span>' for s in skills_q)
                        st.markdown(f'<div class="ner-card"><div class="section-title">🛠️ Skills ({len(skills_q)})</div><div style="margin-top:6px;line-height:2.2">{badges}</div></div>', unsafe_allow_html=True)

                    # Reviewer info if already decided
                    if status != "pending":
                        reviewed_at = (item.get("reviewed_at") or "")[:19].replace("T", " ")
                        st.success(f"{status_icon} **{status.capitalize()}** by `{item.get('reviewer','?')}` at {reviewed_at}")
                        if item.get("correction"):
                            with st.expander("📝 Correction details"):
                                st.json(item["correction"])
                    else:
                        # ── Action panel ──
                        st.markdown("---")
                        st.markdown("**👤 Your name (reviewer)**")
                        reviewer_name = st.text_input(
                            "Reviewer", key=f"reviewer_{qid}",
                            placeholder="e.g. Ahmed Hassan",
                            label_visibility="collapsed",
                        )

                        act_col1, act_col2 = st.columns(2)
                        with act_col1:
                            if st.button("✅ Approve", key=f"approve_{qid}", use_container_width=True):
                                if not reviewer_name.strip():
                                    st.warning("Enter your name first.")
                                else:
                                    try:
                                        decide_review(qid, "approve", reviewer_name.strip())
                                        st.success("✅ Approved successfully! Refresh to update.")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {e}")

                        with act_col2:
                            show_correct = st.toggle("✏️ Correct entities", key=f"toggle_{qid}")

                        if show_correct:
                            st.markdown("**Edit the JSON below and submit correction:**")
                            correction_json = st.text_area(
                                "Correction JSON",
                                value=json.dumps(ents_q, indent=2, ensure_ascii=False),
                                height=200,
                                key=f"correction_{qid}",
                                label_visibility="collapsed",
                            )
                            if st.button("💾 Submit Correction", key=f"submit_{qid}", use_container_width=True):
                                if not reviewer_name.strip():
                                    st.warning("Enter your name first.")
                                else:
                                    try:
                                        correction_data = json.loads(correction_json)
                                        decide_review(qid, "correct", reviewer_name.strip(), correction_data)
                                        st.success("✏️ Correction saved! Refresh to update.")
                                        st.rerun()
                                    except json.JSONDecodeError:
                                        st.error("Invalid JSON — fix the format and try again.")
                                    except Exception as e:
                                        st.error(f"Error: {e}")
