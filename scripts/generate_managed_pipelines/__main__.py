"""Allow running as python -m scripts.generate_managed_pipelines."""

from scripts.generate_managed_pipelines.generate_managed_pipelines import main

if __name__ == "__main__":
    raise SystemExit(main())
