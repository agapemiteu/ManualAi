# Data Directory

This directory contains uploaded car manuals, evaluation datasets, and processed documents.

## Contents

### Evaluation Dataset
- **`evaluation_set.json`** - Curated 50-question evaluation set for 2023 Toyota 4Runner Manual
  - Each question has: `id`, `question`, `ground_truth_answer_summary`, `correct_page_number`
  - Categories: Safety & Critical, Troubleshooting, Maintenance, System Knowledge
  - Used for measuring retrieval accuracy and comparing RAG strategies

### Car Manuals
- **`2023-Toyota-4runner-Manual.pdf`** - Source manual for evaluation (place your PDF here)

### Runtime Storage (created at runtime)
- `uploads/` - Original uploaded files from users
- `manual_store/` - Processed vector store data

## Evaluation Set Schema

```json
{
  "description": "Evaluation set for 2023-Toyota-4runner-Manual",
  "source_manual": "2023-Toyota-4runner-Manual.pdf",
  "questions": [
    {
      "id": "T4R-001",
      "question": "What should you do if the brake light appears?",
      "ground_truth_answer_summary": "Stop safely and contact dealer...",
      "correct_page_number": 490
    }
  ]
}
```

## Using the Evaluation Set

Run baseline evaluation from repository root:
```bash
python hf-space/evaluate.py
```

Or from `hf-space/` directory:
```bash
cd hf-space
python evaluate.py
```

## Note

Sample PDF files are not included in the repository to keep it lightweight. Users should upload their own car manuals through the application interface.
