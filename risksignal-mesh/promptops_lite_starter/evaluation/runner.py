
import random

def run_prompt(df):
    return [
        random.choice(["Consistent","Inconsistent"])
        for _ in range(len(df))
    ]
