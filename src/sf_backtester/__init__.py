"""sf-backtester: SLURM-based parallel backtesting for quantitative finance."""

from sf_backtester.config import BacktestConfig, DynamicBacktestConfig, SlurmConfig
from sf_backtester.runner import BacktestRunner, DynamicBacktestRunner

__version__ = "0.1.0"
__all__ = ["BacktestConfig", "BacktestRunner", "DynamicBacktestConfig", "DynamicBacktestRunner", "SlurmConfig"]
