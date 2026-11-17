import json, pandas as pd
from pathlib import Path
root=Path(__file__).resolve().parents[1]
df=pd.read_csv(root/'data/processed/clean_data.csv')
enc=json.loads((root/'data/encoded/encoded_reviews.json').read_text(encoding='utf-8'))
assert len(df)==len(enc)
assert df.review_id.is_unique
assert all(e['evidence'] in df.loc[df.review_id==e['review_id'],'review_text'].iloc[0] for e in enc)
print('PASS: rows, unique IDs, evidence traceability')
