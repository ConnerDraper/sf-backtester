"""Command-line interface for sf-backtester."""

import click

from sf_backtester.runner import BacktestRunner, DynamicBacktestRunner


@click.group()
def cli() -> None:
    """SLURM-based parallel backtesting for quantitative finance."""
    pass


@cli.command()
@click.argument("config_path", type=click.Path(exists=True))
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print the SBATCH script without submitting.",
)
@click.option(
    "--data-path",
    type=click.Path(exists=True),
    help="Override the data path from config.",
)
@click.option(
    "--gamma",
    type=float,
    help="Override gamma from config.",
)
def run(
    config_path: str,
    dry_run: bool,
    data_path: str | None,
    gamma: float | None,
) -> None:
    """Run a static MVO backtest on SLURM from a YAML config file.

    CONFIG_PATH is the path to a YAML configuration file.

    Example:
        sf-backtester run config.yml
        sf-backtester run config.yml --dry-run
        sf-backtester run config.yml --gamma 0.5
    """
    runner = BacktestRunner.from_yaml(config_path)

    # Apply overrides
    if data_path is not None:
        runner.config.data_path = data_path
    if gamma is not None:
        runner.config.gamma = gamma
        # Update output paths that depend on gamma
        runner.config.output_dir = (
            f"{runner.config.project_root}/weights/{runner.config.signal_name}/{gamma}"
        )
        runner.config.logs_dir = f"logs/{runner.config.signal_name}/{gamma}"

    runner.submit(dry_run=dry_run)


@cli.command()
@click.argument("config_path", type=click.Path(exists=True))
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print the SBATCH script without submitting.",
)
@click.option(
    "--data-path",
    type=click.Path(exists=True),
    help="Override the data path from config.",
)
@click.option(
    "--initial-gamma",
    type=float,
    help="Override initial_gamma from config.",
)
@click.option(
    "--target-active-risk",
    type=float,
    help="Override target_active_risk from config.",
)
def dynamic(
    config_path: str,
    dry_run: bool,
    data_path: str | None,
    initial_gamma: float | None,
    target_active_risk: float | None,
) -> None:
    """Run a dynamic MVO backtest with gamma calibration on SLURM.

    CONFIG_PATH is the path to a YAML configuration file.

    Example:
        sf-backtester dynamic config.yml
        sf-backtester dynamic config.yml --dry-run
        sf-backtester dynamic config.yml --initial-gamma 100 --target-active-risk 0.05
    """
    runner = DynamicBacktestRunner.from_yaml(config_path)

    # Apply overrides
    if data_path is not None:
        runner.config.data_path = data_path
    if initial_gamma is not None:
        runner.config.initial_gamma = initial_gamma
        # Update output paths that depend on target_active_risk
        runner.config.output_dir = (
            f"{runner.config.project_root}/weights/{runner.config.signal_name}/dynamic_{runner.config.target_active_risk}"
        )
        runner.config.logs_dir = f"logs/{runner.config.signal_name}/dynamic_{runner.config.target_active_risk}"
    if target_active_risk is not None:
        runner.config.target_active_risk = target_active_risk
        # Update output paths that depend on target_active_risk
        runner.config.output_dir = (
            f"{runner.config.project_root}/weights/{runner.config.signal_name}/dynamic_{target_active_risk}"
        )
        runner.config.logs_dir = f"logs/{runner.config.signal_name}/dynamic_{target_active_risk}"

    runner.submit(dry_run=dry_run)


if __name__ == "__main__":
    cli()
