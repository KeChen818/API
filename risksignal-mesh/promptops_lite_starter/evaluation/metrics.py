
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def calculate_metrics(expected, predicted):
    return {
        "accuracy": accuracy_score(expected, predicted),
        "precision": precision_score(expected, predicted, pos_label="Inconsistent", zero_division=0),
        "recall": recall_score(expected, predicted, pos_label="Inconsistent", zero_division=0),
        "f1": f1_score(expected, predicted, pos_label="Inconsistent", zero_division=0),
    }
