:root {
    --ubs-red: #E60000;
    --ubs-dark: #1A1A1A;
    --ubs-navy: #001F3F;
    --ubs-gray: #F5F5F5;
    --ubs-border: #D9D9D9;
    --ubs-text: #1A1A1A;
    --ubs-muted: #6B7280;
}

/* Sidebar */

.stSidebar {
    background-color: var(--ubs-dark);
}

.stSidebar * {
    color: white !important;
}

/* Buttons */

.stButton > button {
    background-color: var(--ubs-red);
    color: white;
    border-radius: 8px;
    border: none;
}

.stButton > button:hover {
    background-color: #B80000;
}

/* KPI */

.stMetric {
    border-left: 4px solid var(--ubs-red);
    padding-left: 12px;
}

/* Alert */

[data-testid="stAlert"] {
    background-color: #F5F5F5 !important;
    border: 1px solid #D9D9D9 !important;
    border-left: 4px solid #E60000 !important;
}

[data-testid="stAlert"] * {
    color: #1A1A1A !important;
}

/* Executive Note */

.executive-note {
    background: #F5F5F5;
    border: 1px solid #D9D9D9;
    border-left: 4px solid #E60000;
    padding: 12px 16px;
    border-radius: 6px;
}

/* Plotly */

.js-plotly-plot {
    border-radius: 8px;
}