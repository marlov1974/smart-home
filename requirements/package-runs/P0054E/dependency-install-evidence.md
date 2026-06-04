# P0054E Dependency Install Evidence

Package: P0054E
Label: LABB

## Install Commands

```text
python3 -m pip install --user lightgbm xgboost
```

Result:

```text
Successfully installed lightgbm-4.6.0 xgboost-2.1.4
```

Initial import failed because both packages required OpenMP runtime `libomp.dylib`.

```text
lightgbm IMPORT_FAIL OSError ... Library not loaded: @rpath/libomp.dylib
xgboost IMPORT_FAIL XGBoostError ... OpenMP runtime is not installed ... libomp.dylib
```

Homebrew was available at `/opt/homebrew/bin/brew`, and `/opt/homebrew/opt/libomp` did not exist. The minimal Mac-local runtime dependency was installed:

```text
brew install libomp
```

Result:

```text
libomp 22.1.7
/opt/homebrew/Cellar/libomp/22.1.7: 11 files, 1.8MB
```

Homebrew reported `libomp` as keg-only and did not broadly symlink it into `/opt/homebrew`.

## Installed Python Package Locations

```text
lightgbm 4.6.0
Location: /Users/marcus.lovenstad/Library/Python/3.9/lib/python/site-packages

xgboost 2.1.4
Location: /Users/marcus.lovenstad/Library/Python/3.9/lib/python/site-packages
```

## Scope Statement

These installs are Mac-local LABB dependencies for P0054E only. They are not G2 runtime, Shelly, Home Assistant, deploy or production dependencies.
