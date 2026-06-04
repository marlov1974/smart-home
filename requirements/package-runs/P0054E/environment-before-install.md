# P0054E Environment Before Install

Captured before installing P0054E LABB dependencies.

## Python

```text
executable= /Library/Developer/CommandLineTools/usr/bin/python3
version= 3.9.6 (default, Apr 17 2026, 18:15:52)  [Clang 21.0.0 (clang-2100.1.1.101)]
prefix= /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9
base_prefix= /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9
real_prefix=
venv= False
conda_prefix=
virtual_env=
platform= macOS-26.4.1-arm64-arm-64bit
machine= arm64
site_packages= ['/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/site-packages', '/Library/Python/3.9/site-packages', '/AppleInternal/Library/Python/3.9/site-packages', '/AppleInternal/Tests/Python/3.9/site-packages']
```

## Pip

```text
pip 21.2.4 from /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/site-packages/pip (python 3.9)
```

## Package Status Before Install

```text
numpy 2.0.2
pandas NOT_INSTALLED
scikit-learn 1.6.1
sklearn NOT_INSTALLED
lightgbm NOT_INSTALLED
xgboost NOT_INSTALLED
```

## Import Status Before Install

```text
numpy IMPORT_OK 2.0.2
pandas IMPORT_FAIL ModuleNotFoundError No module named 'pandas'
sklearn IMPORT_OK 1.6.1
lightgbm IMPORT_FAIL ModuleNotFoundError No module named 'lightgbm'
xgboost IMPORT_FAIL ModuleNotFoundError No module named 'xgboost'
```

## Dependency Convention Finding

No repository-local `pyproject.toml`, `requirements*.txt`, `Pipfile`, `poetry.lock`, `environment*.yml`, `setup.cfg`, `setup.py`, `.python-version` or `uv.lock` was found by the inspected patterns.
