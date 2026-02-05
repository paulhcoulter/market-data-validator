# Market Data Validator

A data pipeline that processes historical stock market data and flags significant price movements based on configurable thresholds.

## Setup

Requires Python 3.8+

```bash
pip install -r requirements.txt
```

## Usage

```bash
python pipeline.py
```

This loads configuration from `config.json`, reads all CSV files from `data/`, runs the configured checks, and outputs results to `results.csv`.

## Configuration

Edit `config.json` to customize the pipeline:

```json
{
  "checks": [
    {
      "name": "daily",
      "enabled": true,
      "period": 1,
      "default_threshold": 1.0,
      "custom_thresholds": {
        "SP500": 1.5
      }
    },
    {
      "name": "weekly",
      "enabled": true,
      "period": 5,
      "default_threshold": 5.0,
      "custom_thresholds": {}
    }
  ]
}
```

- `name` - Label for the check (appears in output)
- `enabled` - Set to `false` to skip this check
- `period` - Trading days to look back (1=daily, 5=weekly, 21=monthly)
- `default_threshold` - Percentage threshold for flagging
- `custom_thresholds` - Override thresholds for specific tickers

To add a new check (e.g., monthly), just add another entry to the `checks` array with `"period": 21`. No code changes needed.

## Output

The pipeline generates `results.csv` with: ticker, check_type, date, previous_value, current_value, change_percent, and threshold.

## Design Choices

- **JSON over YAML** - Built into Python, no extra dependencies, and I'm more familiar with it.
- **pandas** - Industry-standard for tabular data in Python.
- **Single reusable check function** - Instead of separate daily/weekly functions, one function takes a `period` parameter. Adding new checks is a config change, not a code change.
- **File-based config vs database** - JSON file is simple and portable. A database would make sense if multiple users needed to edit configs simultaneously or we needed audit trails.

## AI Disclosure

This solution was developed with assistance from Claude AI (Anthropic).
