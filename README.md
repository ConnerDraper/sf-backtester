# sf-backtester

SLURM-based parallel backtesting for quantitative finance. Distributes MVO optimization across compute nodes, processing one year per task.

## Installation

```bash
pip install sf-backtester
```

## Usage

### CLI

#### Static MVO Backtest

```bash
# Run static backtest with fixed gamma
sf-backtester run config.yml

# Preview sbatch script without submitting
sf-backtester run config.yml --dry-run

# Override gamma from config
sf-backtester run config.yml --gamma 50
```

#### Dynamic Backtest with Gamma Calibration

```bash
# Run dynamic backtest with automatic gamma calibration
sf-backtester dynamic config.dynamic.yml

# Preview sbatch script without submitting
sf-backtester dynamic config.dynamic.yml --dry-run

# Override parameters from config
sf-backtester dynamic config.dynamic.yml --initial-gamma 100 --target-active-risk 0.05
```

### Python API

#### Static Backtest

```python
from sf_backtester import BacktestRunner, BacktestConfig, SlurmConfig

slurm_config = SlurmConfig(
    n_cpus=8,
    mem="32G",
    time="03:00:00",
    mail_type="BEGIN,END,FAIL",
    max_concurrent_jobs=30,
)

config = BacktestConfig(
    signal_name="momentum",
    gamma=50,
    data_path="/path/to/alphas.parquet",
    project_root="/path/to/project",
    byu_email="you@byu.edu",
    constraints=["ZeroBeta", "ZeroInvestment"],
    slurm=slurm_config,
)

runner = BacktestRunner(config)

# Submit to SLURM
runner.submit()
```

#### Dynamic Backtest with Gamma Calibration

```python
from sf_backtester import DynamicBacktestRunner, DynamicBacktestConfig, SlurmConfig

slurm_config = SlurmConfig(
    n_cpus=8,
    mem="32G",
    time="03:00:00",
    mail_type="BEGIN,END,FAIL",
    max_concurrent_jobs=30,
)

config = DynamicBacktestConfig(
    signal_name="momentum",
    initial_gamma=100.0,
    target_active_risk=0.05,  # 5% annualized active risk
    data_path="/path/to/alphas.parquet",
    project_root="/path/to/project",
    byu_email="you@byu.edu",
    constraints=["ZeroBeta", "ZeroInvestment"],
    slurm=slurm_config,
)

runner = DynamicBacktestRunner(config)

# Submit to SLURM
runner.submit()
```

#### Load from YAML

```python
from sf_backtester import BacktestRunner, DynamicBacktestRunner
import polars as pl

# Static backtest
runner = BacktestRunner.from_yaml("config.yml")
runner.submit()

# Dynamic backtest
runner = DynamicBacktestRunner.from_yaml("config.dynamic.yml")
runner.submit()
```

#### Pass DataFrame directly

```python
from sf_backtester import BacktestRunner
import polars as pl

runner = BacktestRunner.from_yaml("config.yml")
data = pl.read_parquet("alphas.parquet")
runner.submit(data=data)
```

## Configuration

### YAML format

#### Static Backtest

```yaml
signal_name: momentum
gamma: 500
data_path: /path/to/alphas.parquet
project_root: /path/to/project
byu_email: you@byu.edu

constraints:
  - ZeroBeta
  - ZeroInvestment

slurm:
  n_cpus: 8
  mem: 32G
  time: "03:00:00"
  mail_type: BEGIN,END,FAIL
  max_concurrent_jobs: 31
```

#### Dynamic Backtest with Gamma Calibration

```yaml
signal_name: momentum
initial_gamma: 100.0
target_active_risk: 0.05  # 5% annualized active risk
data_path: /path/to/alphas.parquet
project_root: /path/to/project
byu_email: you@byu.edu

constraints:
  - ZeroBeta
  - ZeroInvestment

slurm:
  n_cpus: 8
  mem: 32G
  time: "03:00:00"
  mail_type: BEGIN,END,FAIL
  max_concurrent_jobs: 31
```

### What is Dynamic Gamma Calibration?

The dynamic backtest automatically calibrates the risk aversion parameter (gamma) to achieve a target level of active risk (tracking error) relative to a benchmark portfolio. Instead of specifying a fixed gamma value:

- **Static backtest**: Specify a fixed `gamma` parameter
- **Dynamic backtest**: Specify `initial_gamma` (starting point) and `target_active_risk` (desired annualized active risk in decimal, e.g., 0.05 = 5%)

The optimizer iteratively adjusts gamma to find the portfolio weights that produce the target active risk level. This is useful when you want to control portfolio risk relative to a benchmark rather than directly controlling the risk aversion parameter.

## Data format

Input parquet must have columns:
- `date`: Date column
- `barrid`: Asset identifier  
- `alpha`: Alpha signal values
- `predicted_beta`: Predicted beta values

Output is one parquet per year in `output_dir/{year}.parquet` containing portfolio weights.

## Publishing
1. Bump the version

```bash
uv version v*.*.*
```

2. Add changes (it can be just the version change)

```bash
git add .
git commit -m "Bumped version."
```

3. Tag the branch

```bash
git tag v*.*.*
```

4. Push to origin

```bash
git push --tags
```

