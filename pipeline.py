# Note: This solution was developed with assistance from Claude AI (Anthropic)

import json
import pandas as pd
from pathlib import Path


def load_config(config_path="config.json"):
    """Read the JSON config file and return it as a dictionary."""
    with open(config_path, "r") as file:
        return json.load(file)


def load_data(data_folder="data"):
    """Load all CSV files from a folder and combine into one DataFrame."""
    all_data = []

    # Find all CSV files in the folder
    for csv_file in Path(data_folder).glob("*.csv"):
        df = pd.read_csv(csv_file)

        # Get the ticker name from the column header (e.g., "SP500")
        ticker = df.columns[1]

        # Standardize column names
        df.columns = ["date", "price"]
        df["ticker"] = ticker
        all_data.append(df)

    # Combine all dataframes into one
    combined = pd.concat(all_data, ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"])
    combined = combined.sort_values(["ticker", "date"]).reset_index(drop=True)

    return combined


def check_price_changes(data, check_config):
    """
    Check for price movements that exceed a threshold.

    Parameters:
        data: DataFrame with columns [date, price, ticker]
        check_config: Dict with keys: name, enabled, period, default_threshold, custom_thresholds

    Returns:
        List of violation dictionaries
    """
    if not check_config["enabled"]:
        return []

    results = []
    check_name = check_config["name"]
    period = check_config["period"]
    default_threshold = check_config["default_threshold"]
    custom_thresholds = check_config["custom_thresholds"]

    # Process each ticker separately
    for ticker in data["ticker"].unique():
        ticker_data = data[data["ticker"] == ticker].copy()

        # shift(period) moves data down by N rows, letting us compare to N days ago
        ticker_data["previous_price"] = ticker_data["price"].shift(period)

        # Calculate percentage change
        ticker_data["pct_change"] = (
            (ticker_data["price"] - ticker_data["previous_price"])
            / ticker_data["previous_price"]
            * 100
        )

        # Use custom threshold if defined, otherwise use default
        threshold = custom_thresholds.get(ticker, default_threshold)

        # Find rows where the change exceeds the threshold
        violations = ticker_data[abs(ticker_data["pct_change"]) > threshold]
        violations = violations[violations["pct_change"].notna()]

        for row in violations.to_dict("records"):
            results.append({
                "ticker": ticker,
                "check_type": check_name,
                "date": row["date"].strftime("%Y-%m-%d"),
                "previous_value": round(row["previous_price"], 2),
                "current_value": round(row["price"], 2),
                "change_percent": round(row["pct_change"], 2),
                "threshold": threshold
            })

    return results


def run_pipeline():
    """Main function that runs the full pipeline."""
    print("Loading configuration...")
    config = load_config()

    print("Loading market data...")
    data = load_data()
    print(f"  Loaded {len(data)} rows for {data['ticker'].nunique()} tickers")

    # Run each check defined in the config
    all_results = []
    for check_config in config["checks"]:
        check_name = check_config["name"]
        print(f"Running {check_name} check...")
        results = check_price_changes(data, check_config)
        print(f"  Found {len(results)} {check_name} violations")
        all_results.extend(results)

    # Save results to CSV
    if all_results:
        results_df = pd.DataFrame(all_results)
        results_df.to_csv("results.csv", index=False)
        print(f"\nResults saved to results.csv ({len(all_results)} total violations)")
    else:
        print("\nNo violations found.")

    return all_results


if __name__ == "__main__":
    run_pipeline()
