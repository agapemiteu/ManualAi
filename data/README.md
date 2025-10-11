# Data Directory

This directory contains uploaded car manuals, evaluation datasets, and processed documents.

## Contents

### Evaluation Dataset
- **`evaluation_set.json`** - Curated 50-question evaluation set for 2023 Toyota 4Runner Manual
  - Each question has: `id`, `question`, `ground_truth_answer_summary`, `correct_page_number`
  - Categories: Safety & Critical, Troubleshooting, Maintenance, System Knowledge
  - Used for measuring retrieval accuracy and comparing RAG strategies

### Car Manuals
- **`2023-Toyota-4runner-Manual.pdf`** - Complete 2023 Toyota 4Runner Owner's Manual (608 pages, 12.4MB)
  - Pre-loaded in HuggingFace deployment for immediate testing
  - Available for download and local testing
  - Source for all evaluation experiments

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

## Downloading the Manual

The Toyota 4Runner manual is included in this repository. To download it:

```bash
# Clone the repository
git clone https://github.com/agapemiteu/ManualAi.git
cd ManualAi

# The manual is located at:
# data/2023-Toyota-4runner-Manual.pdf
```

Or download directly from GitHub:
- Navigate to `data/2023-Toyota-4runner-Manual.pdf`
- Click "Download" button

## Note

This manual is pre-loaded in the HuggingFace deployment, so users can immediately test the Q&A system without uploading their own files.
