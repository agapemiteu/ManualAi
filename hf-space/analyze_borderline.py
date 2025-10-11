import json

with open('hf-space/rag_results_ultimate.json') as f:
    results = json.load(f)

borderline = [p for p in results['predictions'] if 3 <= p['diff'] <= 5]

print(f"\nBorderline cases (off by 3-5 pages): {len(borderline)}\n")
print("="*80)

for p in borderline:
    print(f"{p['id']}: GT={p['ground_truth']}, Pred={p['predicted']}, Diff={p['diff']}")
    print(f"  Q: {p['question']}")
    print()
