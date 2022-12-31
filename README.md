Example Usage:

```bash
# Update all tickers
python3 update.py

# Updating an existing ticker, or add a new one:
python3 update.py --symbol TSLA

# Fetching Historical Data:
# Fetch last 5 months (max-months-to-fetch), not stopping even if we encounter data we already have (halt-mode)
python3 update.py --symbol TSLA --max-months-to-fetch 5 --halt-mode all
```