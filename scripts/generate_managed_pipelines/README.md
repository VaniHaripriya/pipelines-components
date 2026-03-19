# Generate managed-pipelines.json

Generates `managed-pipelines.json` at the repository root by scanning all pipeline directories under
`pipelines/` and including only those whose `metadata.yaml` has `managed: true`.

## Usage

From the project root:

```bash
# Generate managed-pipelines.json at repo root
uv run python -m scripts.generate_managed_pipelines

# Write to a custom path
uv run python -m scripts.generate_managed_pipelines -o path/to/managed-pipelines.json
```

## Output format

The JSON is an array of objects with:

| Field         | Source                | Description |
|---------------|-----------------------|-------------|
| `name`        | `metadata.yaml` name  | Pipeline name |
| `description` | `metadata.yaml` description (optional) | Short description for the catalog |
| `path`        | Derived               | Relative path to `pipeline.py` (e.g. `pipelines/training/automl/my_pipeline/pipeline.py`) |
| `stability`   | `metadata.yaml` stability | One of: experimental, alpha, beta, stable |

## Including a pipeline

In the pipeline’s `metadata.yaml`:

1. Set `managed: true`.
2. Optionally set `description` to a short summary used in the catalog.

Only directories that contain both `metadata.yaml` and `pipeline.py` are considered.
