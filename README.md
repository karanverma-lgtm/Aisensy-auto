# Send Campaign

This repository contains `send_campaign.py` which reads a CSV (`Name,Phone`) and submits a campaign to the Aisensy API.

## Setup
1. Add a GitHub repository and push this project.
2. Add a repository secret `AISENSY_API_KEY` with your API key (Settings → Secrets → Actions).
3. (Optional) For local testing, create a `.env` file in the repository root with:

```env
AISENSY_API_KEY=your_api_key_here
```

The script uses `python-dotenv` to load `.env` automatically; `.env` is included in `.gitignore` and must not be committed.

## GitHub Actions
A workflow at `.github/workflows/send_campaign.yml` provides a `workflow_dispatch` trigger with inputs:
- `csv_path` (default: `users.csv`)
- `limit` (optional)
- `test_number` (optional)
- `output` (default: `results.csv`)

### How it works
- The *send* job runs using `AISENSY_API_KEY` and uploads results as an artifact.

## Safety tips
- Use `limit` or `test_number` to send only to a small test subset before sending to the full list.
- Keep your API key secret and rotate it if it appears in logs.

## Local usage
Install dependencies and run locally:

```bash
python -m pip install --upgrade pip
pip install requests python-dotenv
python send_campaign.py users.csv --output results.csv
```

To run and write results:

```bash
AISENSY_API_KEY="<your key>" python send_campaign.py users.csv --output results.csv
```
