import pandas as pd
from src.classifier import train
from src.triage import triage

model, meta = train()
print(f"Trained on {meta['n_train']} tickets; macro-F1 on {meta['n_test']} held-out tickets = {meta['macro_f1']}")
print(pd.DataFrame(meta["report"]).T.drop(columns="support").to_string())
example = "Urgent: Outlook crashes with error E512 on startup. Ticket INC204211, contact me at priya@example.com"
t = triage(example, model)
print(f"\nExample: {example}\n -> {t['category']} ({t['confidence']:.0%}) | {t['team']} | {t['priority']}")
print(" -> entities:", ", ".join(f"{e['label']}={e['text']}" for e in t["entities"]))
