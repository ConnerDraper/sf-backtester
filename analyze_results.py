"""Analyze results from completed backtests."""

import polars as pl
import matplotlib.pyplot as plt
from pathlib import Path
import glob

# Load original data for returns
print("Loading data...")
data = pl.read_parquet("momentum.parquet")
returns_data = data.select(["date", "barrid", "return"])

# Load static weights from all years
print("Loading static backtest results...")
static_output_dir = Path("./weights/momentum_test/60.0")
static_files = sorted(glob.glob(str(static_output_dir / "*.parquet")))
if not static_files:
    raise FileNotFoundError(f"No weight files found in {static_output_dir}")

static_portfolio = pl.concat([pl.read_parquet(f) for f in static_files])
print(f"Static: loaded {len(static_files)} year files, {len(static_portfolio)} total weights")

# Load dynamic weights from all years
print("Loading dynamic backtest results...")
dynamic_output_dir = Path("./weights/momentum_test/dynamic_0.05")
dynamic_files = sorted(glob.glob(str(dynamic_output_dir / "*.parquet")))
if not dynamic_files:
    raise FileNotFoundError(f"No weight files found in {dynamic_output_dir}")

dynamic_portfolio = pl.concat([pl.read_parquet(f) for f in dynamic_files])
print(f"Dynamic: loaded {len(dynamic_files)} year files, {len(dynamic_portfolio)} total weights")

# === PRINT AVERAGE ACTIVE RISK (DYNAMIC ONLY) ===
avg_active_risk = dynamic_portfolio["active_risk"].mean()
print(f"\n{'='*50}")
print(f"Dynamic avg active risk: {avg_active_risk*100:.2f}% (target: 5.00%)")
print(f"{'='*50}")

# === PLOT GAMMA OVER TIME (DYNAMIC ONLY) ===
print("\nPlotting gamma over time...")
gammas = (
    dynamic_portfolio.select(["date", "gamma"])
    .unique("date")
    .sort("date")
)

dates = gammas["date"].to_list()
gamma_vals = gammas["gamma"].to_list()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(dates, gamma_vals, linewidth=2)
ax.set_title("Dynamic Backtest: Calibrated Gamma Over Time", fontsize=14)
ax.set_xlabel("Date")
ax.set_ylabel("Gamma")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('gamma')

# === COMPUTE PORTFOLIO RETURNS FOR BOTH ===
print("\nComputing portfolio returns...")


def compute_portfolio_returns(portfolio, label):
    """Compute daily portfolio returns."""
    return (
        portfolio.select(["date", "barrid", "weight"])
        .join(returns_data, on=["date", "barrid"])
        .group_by("date")
        .agg((pl.col("weight") * pl.col("return")).sum().alias("return"))
        .sort("date")
        .with_columns(pl.lit(label).alias("portfolio"))
    )


static_ret = compute_portfolio_returns(static_portfolio, "Static")
dynamic_ret = compute_portfolio_returns(dynamic_portfolio, "Dynamic")

# === SUMMARY STATISTICS ===
def print_stats(ret_df, label):
    """Print summary statistics for a portfolio."""
    r = ret_df["return"]

    # Annualized metrics
    ann_ret = r.mean() * 252
    ann_vol = r.std() * (252 ** 0.5)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else float("nan")

    # Cumulative return
    cum = (1 + r).product() - 1

    # Max drawdown
    cum_df = ret_df.with_columns(
        (1 + pl.col("return")).cum_prod().alias("cum")
    ).with_columns(
        pl.col("cum").cum_max().alias("cum_max")
    )
    dd = (cum_df["cum"] / cum_df["cum_max"]) - 1
    max_dd = dd.min()

    print(f"\n{'='*50}")
    print(f"{label.upper()} BACKTEST SUMMARY")
    print(f"{'='*50}")
    print(f"  Annualized return : {ann_ret*100:7.2f}%")
    print(f"  Annualized vol    : {ann_vol*100:7.2f}%")
    print(f"  Sharpe ratio      : {sharpe:7.3f}")
    print(f"  Cumulative return : {cum*100:7.2f}%")
    print(f"  Max drawdown      : {max_dd*100:7.2f}%")
    print(f"{'='*50}")


print_stats(static_ret, "Static")
print_stats(dynamic_ret, "Dynamic")

print("\nDone!")
