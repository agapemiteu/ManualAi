# Utility Scripts

This folder contains utility scripts for testing, evaluation, and maintenance of the ManualAi system.

## Testing Scripts

### `test_full_upload.py`
Test uploading the full Toyota 4Runner manual (608 pages) to production.

```bash
python scripts/test_full_upload.py
```

**What it does:**
- Uploads the complete manual to the API
- Monitors processing status
- Tests query functionality
- Validates source page retrieval

### `test_small_upload.py`
Test uploading a smaller sample manual for quick validation.

```bash
python scripts/test_small_upload.py
```

### `test_source_pages.py`
Quick test to verify the API returns source page numbers.

```bash
python scripts/test_source_pages.py
```

### `test_api_response.py`
Basic API connectivity and response format testing.

```bash
python scripts/test_api_response.py
```

---

## Evaluation Scripts

### `evaluate_production.py`
**Main evaluation script** - Tests production system against 50 ground truth questions.

```bash
python scripts/evaluate_production.py
```

**Output:**
- `production_evaluation_results.json` - Detailed results
- Console output with accuracy metrics

**Metrics calculated:**
- Exact page match accuracy
- Within ±2, ±5, ±10 pages tolerance
- Category-wise performance
- Question-by-question breakdown

### `evaluate_production_batch.py`
Batch evaluation variant for testing multiple configurations.

---

## Utility Scripts

### `extract_sample.py`
Extract a smaller section from a large PDF for testing.

```bash
python scripts/extract_sample.py
```

**Use case:** Create test files from large manuals for development and debugging.

**Output:** 
- Extracts first 30 pages by default
- Creates a ~1-2MB PDF suitable for quick uploads

---

## Requirements

Install dependencies before running scripts:

```bash
pip install requests PyMuPDF
```

---

## Environment Setup

Some scripts require environment variables:

```bash
# API endpoint (defaults to production)
export API_URL="https://agapemiteu-manualai.hf.space"

# For local testing
export API_URL="http://localhost:8000"
```

---

## Usage Tips

### Running Production Evaluation
```bash
# Full evaluation with all 50 questions
python scripts/evaluate_production.py

# Check results
cat production_evaluation_results.json
```

### Testing New Features
```bash
# 1. Upload test manual
python scripts/test_full_upload.py

# 2. Test specific feature
python scripts/test_source_pages.py

# 3. Run evaluation
python scripts/evaluate_production.py
```

### Development Workflow
```bash
# Quick test cycle
python scripts/test_small_upload.py   # Fast upload
python scripts/test_api_response.py    # Verify API
python scripts/test_source_pages.py    # Check feature
```

---

## Script Dependencies

| Script | Dependencies | Runtime |
|--------|--------------|---------|
| `test_*.py` | requests | < 1 min |
| `evaluate_production.py` | requests | 3-5 min |
| `extract_sample.py` | PyMuPDF | < 10 sec |

---

## Integration with CI/CD

These scripts can be integrated into automated testing:

```yaml
# .github/workflows/test.yml
- name: Test Production API
  run: python scripts/test_api_response.py

- name: Run Evaluation
  run: python scripts/evaluate_production.py
```

---

## Troubleshooting

**"Connection refused"**
- Check API_URL is correct
- Verify API is running
- Check network connectivity

**"Manual not found"**
- Upload manual first with `test_full_upload.py`
- Verify manual ID in response

**"Timeout errors"**
- Large manuals take 3-5 minutes to process
- Wait for processing to complete
- Check manual status endpoint

---

For more information, see the main [README](../README.md) and [PRODUCTION_CASE_STUDY](../PRODUCTION_CASE_STUDY.md).
