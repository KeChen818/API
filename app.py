import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="RiskSignal Mesh Accent Pattern Gallery",
    layout="wide",
)


# -----------------------------
# CSS
# -----------------------------

def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --brand-red: #E60100;
            --brand-red-dark: #B00000;
            --brand-black: #000000;
            --brand-charcoal: #1A1A1A;
            --brand-bg: #FFFFFF;
            --brand-panel: #F7F7F7;
            --brand-border: #D9D9D9;
            --brand-muted: #666666;
            --brand-table-header: #F1F1F1;
            --brand-amber: #F59E0B;
            --brand-green: #15803D;
            --shadow-soft: 0 1px 3px rgba(0, 0, 0, 0.08);
        }

        .stApp {
            background-color: var(--brand-bg);
            color: var(--brand-charcoal);
        }

        /* Global top accent bar */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--brand-red);
            z-index: 9999;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }

        /* Sidebar brand rail */
        [data-testid="stSidebar"] {
            background-color: var(--brand-black);
            border-right: 4px solid var(--brand-red);
        }

        [data-testid="stSidebar"] * {
            color: #FFFFFF;
        }

        [data-testid="stSidebar"] label {
            color: #E5E5E5 !important;
            font-weight: 700;
        }

        /* Title accent bar */
        .main-title {
            border-left: 6px solid var(--brand-red);
            padding-left: 14px;
            margin-bottom: 0.4rem;
            color: var(--brand-black);
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: -0.045em;
        }

        .subtitle {
            color: var(--brand-muted);
            font-size: 0.98rem;
            line-height: 1.5;
            margin-bottom: 1.2rem;
        }

        .phase-badge {
            display: inline-block;
            background: #FFF1F1;
            color: var(--brand-red-dark);
            border: 1px solid #F5B5B5;
            padding: 8px 14px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 13px;
            margin-top: 0.2rem;
        }

        /* Section title underline */
        .section-title {
            display: inline-block;
            border-bottom: 2px solid var(--brand-red);
            padding-bottom: 8px;
            margin: 0.5rem 0 1rem 0;
            font-size: 1.35rem;
            font-weight: 750;
            color: var(--brand-black);
            letter-spacing: -0.02em;
        }

        .pattern-name {
            font-size: 12px;
            color: var(--brand-muted);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }

        /* Card base */
        .custom-card {
            background: #FFFFFF;
            border: 1px solid var(--brand-border);
            border-radius: 4px;
            padding: 18px 20px;
            box-shadow: var(--shadow-soft);
            height: 100%;
        }

        /* KPI card top accent */
        .metric-card {
            background: #FFFFFF;
            border: 1px solid var(--brand-border);
            border-top: 4px solid var(--brand-red);
            border-radius: 4px;
            padding: 18px 20px;
            box-shadow: var(--shadow-soft);
            min-height: 130px;
        }

        .metric-label {
            color: var(--brand-muted);
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 10px;
        }

        .metric-value {
            color: var(--brand-black);
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.1;
        }

        .metric-note {
            color: var(--brand-muted);
            font-size: 12px;
            margin-top: 8px;
            line-height: 1.4;
        }

        /* Divider accent */
        .section-divider {
            height: 3px;
            background: var(--brand-red);
            margin: 20px 0 18px;
            width: 90px;
        }

        /* Narrative left rail */
        .risk-summary-card {
            background: #FFFFFF;
            border: 1px solid var(--brand-border);
            border-left: 5px solid var(--brand-red);
            padding: 18px 20px;
            border-radius: 4px;
            line-height: 1.55;
            min-height: 150px;
        }

        .risk-summary-card h3,
        .alert-caveat h3,
        .executive-card h3 {
            margin: 0 0 10px;
            color: var(--brand-black);
            font-size: 1.1rem;
        }

        .risk-summary-card p,
        .alert-caveat p,
        .executive-card p {
            margin: 0;
            color: var(--brand-muted);
            line-height: 1.55;
            font-size: 14px;
        }

        /* Alert rail */
        .alert-caveat {
            background: #FFF7F7;
            border: 1px solid #F0CACA;
            border-left: 5px solid var(--brand-red);
            padding: 18px 20px;
            border-radius: 4px;
            min-height: 150px;
        }

        /* Severity strip */
        .status-strip {
            border: 1px solid var(--brand-border);
            background: #FFFFFF;
            padding: 16px 18px;
            border-radius: 4px;
            min-height: 125px;
        }

        .status-strip.high {
            border-left: 6px solid var(--brand-red-dark);
        }

        .status-strip.medium {
            border-left: 6px solid var(--brand-amber);
        }

        .status-strip.low {
            border-left: 6px solid var(--brand-green);
        }

        .status-title {
            font-weight: 800;
            margin-bottom: 8px;
            color: var(--brand-black);
        }

        .status-copy {
            color: var(--brand-muted);
            font-size: 13px;
            line-height: 1.45;
        }

        .pill {
            display: inline-block;
            padding: 4px 9px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
        }

        .pill-high {
            background: #FEE2E2;
            color: var(--brand-red-dark);
        }

        .pill-medium {
            background: #FEF3C7;
            color: #92400E;
        }

        .pill-low {
            background: #E8F5E9;
            color: var(--brand-green);
        }

        /* Active tab accent */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            border-bottom: 1px solid var(--brand-border);
        }

        .stTabs [data-baseweb="tab"] {
            background-color: var(--brand-table-header);
            border-radius: 0;
            padding: 10px 18px;
            color: var(--brand-charcoal);
            border: 1px solid var(--brand-border);
            border-bottom: none;
        }

        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF;
            color: var(--brand-black);
            font-weight: 750;
            border-top: 4px solid var(--brand-red);
        }

        /* Streamlit dataframe container */
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--brand-border);
            border-radius: 4px;
            overflow: hidden;
        }

        /* Corner accent card */
        .executive-card {
            position: relative;
            background: #FFFFFF;
            border: 1px solid var(--brand-border);
            padding: 20px;
            border-radius: 4px;
            min-height: 150px;
        }

        .executive-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 46px;
            height: 4px;
            background: var(--brand-red);
        }

        .code-label {
            margin-top: 12px;
            font-size: 12px;
            color: var(--brand-muted);
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            background: #F8F8F8;
            border: 1px solid var(--brand-border);
            border-radius: 4px;
            padding: 8px 10px;
        }

        .pattern-list {
            margin: 0;
            padding-left: 18px;
            color: var(--brand-muted);
            font-size: 14px;
            line-height: 1.65;
        }

        .small-muted {
            color: var(--brand-muted);
            font-size: 13px;
            line-height: 1.5;
        }

        /* Button */
        .stButton > button {
            background-color: var(--brand-black);
            color: #FFFFFF;
            border: 1px solid var(--brand-black);
            border-radius: 4px;
            font-weight: 700;
        }

        .stButton > button:hover {
            background-color: var(--brand-red);
            color: #FFFFFF;
            border-color: var(--brand-red);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:
    st.markdown("## RiskSignal Mesh")
    st.caption("Accent pattern gallery for a Streamlit enterprise dashboard.")

    st.markdown("---")

    st.markdown("### Pattern Set")
    selected_page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "FRED Macro Signals",
            "Polymarket Events",
            "Risk Theme Mapping",
            "Risk Profile Summary",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.markdown("### Recommended Core")
    st.markdown(
        """
        - Sidebar brand rail
        - Title accent bar
        - Metric top accent
        - Active tab accent
        - Summary left rail
        """
    )


# -----------------------------
# Header
# -----------------------------

left, right = st.columns([0.78, 0.22])

with left:
    st.markdown(
        """
        <div class="main-title">Accent Pattern Gallery</div>
        <div class="subtitle">
            A visual reference for UBS-inspired / banking-style dashboard accent patterns.
            Use these as reusable design motifs in your Streamlit CSS.
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="phase-badge">Single App · CSS Included</div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# KPI Cards
# -----------------------------

st.markdown('<div class="pattern-name">Pattern 2 · Card Accent Stripe</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">KPI Cards</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">FRED Signals</div>
            <div class="metric-value">8</div>
            <div class="metric-note">Macro, rates, credit, stress</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Event Markets</div>
            <div class="metric-value">25</div>
            <div class="metric-note">Polymarket keyword: recession</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Mapped Themes</div>
            <div class="metric-value">6</div>
            <div class="metric-note">Risk taxonomy alignment</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Highest Severity</div>
            <div class="metric-value">Medium</div>
            <div class="metric-note">Credit Spread Risk</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Tabs
# -----------------------------

st.markdown("")

st.markdown('<div class="pattern-name">Pattern 9 · Active Tab Accent</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Executive Overview",
        "FRED Macro",
        "Polymarket",
        "Risk Profile",
    ]
)

with tab1:
    st.write("Active tab uses a red top rail to show navigation state.")

with tab2:
    st.write("This tab can later hold FRED macro charts.")

with tab3:
    st.write("This tab can later hold Polymarket event signals.")

with tab4:
    st.write("This tab can later hold risk profile summaries.")


# -----------------------------
# Narrative cards
# -----------------------------

st.markdown("")
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="pattern-name">Pattern 6 · Narrative Left Rail</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="risk-summary-card">
            <h3>Current Risk Profile</h3>
            <p>
                Credit spread conditions appear moderately elevated. The left rail draws attention to an
                important narrative block without overusing red across the full page.
            </p>
        </div>
        <div class="code-label">Class: .risk-summary-card · Accent: border-left</div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown('<div class="pattern-name">Pattern 12 · Alert Accent Rail</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="alert-caveat">
            <h3>Data Caveat</h3>
            <p>
                Prediction market probabilities are market-implied signals and should not be treated as official forecasts.
            </p>
        </div>
        <div class="code-label">Class: .alert-caveat · Use for caveats / warnings</div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Severity strips
# -----------------------------

st.markdown("")
st.markdown('<div class="pattern-name">Pattern 7 · Severity Status Strip</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Risk Theme Status</div>', unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)

with s1:
    st.markdown(
        """
        <div class="status-strip high">
            <div class="status-title">Credit Spread Risk <span class="pill pill-high">High</span></div>
            <div class="status-copy">Useful when a theme requires immediate management attention.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s2:
    st.markdown(
        """
        <div class="status-strip medium">
            <div class="status-title">Interest Rate Risk <span class="pill pill-medium">Medium</span></div>
            <div class="status-copy">Useful when a theme is elevated but not yet critical.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s3:
    st.markdown(
        """
        <div class="status-strip low">
            <div class="status-title">Liquidity Risk <span class="pill pill-low">Low</span></div>
            <div class="status-copy">Useful when a theme is monitored but currently contained.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Data table
# -----------------------------

st.markdown("")
st.markdown('<div class="pattern-name">Pattern 8 · Table Header Accent</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Unified Signal Table</div>', unsafe_allow_html=True)

df = pd.DataFrame(
    [
        {
            "Source": "FRED",
            "Signal": "HY Credit Spread",
            "Risk Theme": "Credit Spread Risk",
            "Direction": "Widening",
            "Severity": "Medium",
        },
        {
            "Source": "FRED",
            "Signal": "Fed Funds Rate",
            "Risk Theme": "Interest Rate Risk",
            "Direction": "Tightening",
            "Severity": "Medium",
        },
        {
            "Source": "Polymarket",
            "Signal": "Recession Event Market",
            "Risk Theme": "Credit / Macro Risk",
            "Direction": "Elevated",
            "Severity": "Medium",
        },
        {
            "Source": "Polymarket",
            "Signal": "Oil / Geopolitical Market",
            "Risk Theme": "Geopolitical Risk",
            "Direction": "Contained",
            "Severity": "Low",
        },
    ]
)

st.dataframe(df, use_container_width=True, hide_index=True)


# -----------------------------
# Corner card and section divider
# -----------------------------

st.markdown("")
cc1, cc2 = st.columns(2)

with cc1:
    st.markdown('<div class="pattern-name">Pattern 11 · Corner Accent Card</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="executive-card">
            <h3>Executive Commentary</h3>
            <p>
                The corner accent is subtle and works well for boardroom-style commentary cards.
            </p>
        </div>
        <div class="code-label">Class: .executive-card::before · Small corner stripe</div>
        """,
        unsafe_allow_html=True,
    )

with cc2:
    st.markdown('<div class="pattern-name">Pattern 4 + 5 · Divider and Underline</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="custom-card">
            <h3 class="section-title">Section Heading</h3>
            <p class="small-muted">
                Use a short red divider or underline to break long pages into executive-friendly sections.
            </p>
            <div class="section-divider"></div>
            <p class="small-muted">
                This is less visually heavy than a full-width red band.
            </p>
        </div>
        <div class="code-label">Classes: .section-title · .section-divider</div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Pattern catalog
# -----------------------------

st.markdown("")
st.markdown('<div class="pattern-name">Pattern Catalog</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Names to Use in Your Spec</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="custom-card">
        <ul class="pattern-list">
            <li><strong>Title accent bar</strong> — left border beside page title.</li>
            <li><strong>Card accent stripe</strong> — top border on KPI / metric cards.</li>
            <li><strong>Sidebar brand rail</strong> — vertical red rail beside navigation.</li>
            <li><strong>Section accent divider</strong> — short red line between content blocks.</li>
            <li><strong>Accent underline</strong> — red underline for section headers.</li>
            <li><strong>Narrative left rail</strong> — red left border for risk profile summaries.</li>
            <li><strong>Severity rail</strong> — red / amber / green left strip for risk status cards.</li>
            <li><strong>Table accent header</strong> — red top line above data table headers.</li>
            <li><strong>Active tab accent</strong> — red top rail on selected tab.</li>
            <li><strong>Global top accent bar</strong> — thin red app-wide top stripe.</li>
            <li><strong>Corner accent</strong> — small red stripe in card corner.</li>
            <li><strong>Alert rail</strong> — red left border for warnings and caveats.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)