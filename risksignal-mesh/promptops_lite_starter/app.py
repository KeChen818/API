
import streamlit as st
import pandas as pd
from evaluation.runner import run_prompt
from evaluation.metrics import calculate_metrics

st.set_page_config(layout="wide")

st.sidebar.title("Prompt Registry")
selected_prompt = st.sidebar.selectbox(
    "Prompt",
    ["impact_inconsistency_controller.yaml","impact_inconsistency_controller_v2.yaml"]
)

mode = st.sidebar.radio(
    "Mode",
    ["Single Test","Batch Evaluation","Compare Versions"]
)

st.title("PromptOps Lite")

if mode == "Batch Evaluation":
    df = pd.read_csv("data/eval/impact_inconsistency_controller.csv")

    if st.button("Run Evaluation"):
        predictions = run_prompt(df)

        metrics = calculate_metrics(
            df["expected"],
            predictions
        )

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("Accuracy", f"{metrics['accuracy']:.2%}")
        c2.metric("Precision", f"{metrics['precision']:.2%}")
        c3.metric("Recall", f"{metrics['recall']:.2%}")
        c4.metric("F1", f"{metrics['f1']:.2%}")

        df["predicted"] = predictions
        errors = df[df["expected"] != df["predicted"]]

        st.subheader(f"Error Cases ({len(errors)})")
        st.dataframe(errors)
