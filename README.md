# Send Campaign

This repository contains `send_campaign.py` which reads a CSV (`Name,Phone`) and submits a campaign to the Aisensy API.

## Setup
1. Add a GitHub repository and push this project.
2. Add a repository secret `AISENSY_API_KEY` with your API key (Settings → Secrets → Actions).

## GitHub Actions
A workflow at `.github/workflows/send_campaign.yml` provides a `workflow_dispatch` trigger with inputs:
- `csv_path` (default: `users.csv`)
- `dry_run` (default: `true`)
- `limit` (optional)
- `test_number` (optional)
- `run_live` (default: `false`) — set to `true` to run the live send job
- `output` (default: `results.csv`)

### How it works
- Use the *test* job to run the script in dry-run mode and upload `results.csv` as an artifact.
- If you set `run_live` to `true` when dispatching, the *send* job will run using `AISENSY_API_KEY` and upload the live results.

## Safety tips
- Always perform a dry-run first.
- Use `limit` or `test_number` to send only to a small test subset before sending to the full list.
- Keep your API key secret and rotate it if it appears in logs.

## Local usage
Install dependencies and run locally:

```bash
python -m pip install --upgrade pip
pip install requests
python send_campaign.py users.csv --dry-run
```

To run and write results:

```bash
AISENSY_API_KEY="<your key>" python send_campaign.py users.csv --output results.csv
```
