# Detect Changed Assets Script

Core detection logic for the `detect-changed-assets` composite action.

## Usage

### Via Composite Action (Normal Use)

```yaml
- uses: ./.github/actions/detect-changed-assets
```

### Standalone (Testing/Debugging)

```bash
# Basic usage
.github/scripts/detect-changed-assets/detect.sh origin/main HEAD true

# Arguments:
# 1. BASE_REF (default: origin/main)
# 2. HEAD_REF (default: HEAD)
# 3. INCLUDE_THIRD_PARTY (default: true)
# 4. FILTER (default: empty - no filtering)

# Examples:
.github/scripts/detect-changed-assets/detect.sh origin/develop HEAD false
.github/scripts/detect-changed-assets/detect.sh origin/main HEAD true '\.py$'
.github/scripts/detect-changed-assets/detect.sh origin/main HEAD true '\.(py|yaml)$'
```

## What It Does

1. Fetches base branch if needed
2. Finds merge base for accurate diff
3. Lists all changed files via `git diff`
4. Parses paths with regex to find components/pipelines
5. Detects changed file types (Python, Markdown, YAML) across the entire repository
6. Deduplicates results
7. Writes outputs to `$GITHUB_OUTPUT` and `$GITHUB_STEP_SUMMARY`
8. Displays results (when run standalone)

## Detection Patterns

### Components and Pipelines

```bash
# Matches these patterns:
components/<category>/<name>/
pipelines/<category>/<name>/
third_party/components/<category>/<name>/
third_party/pipelines/<category>/<name>/

# Example:
# Changed file: components/training/my_trainer/component.py
# Output: components/training/my_trainer
```

### File Types (Repository-wide)

The script also detects changed file types across the entire repository:
- **Python files**: Any file ending with `.py`
- **Markdown files**: Any file ending with `.md`
- **YAML files**: Any file ending with `.yaml` or `.yml`

Examples:
- `setup.py` → detected as Python file
- `docs/README.md` → detected as Markdown file
- `.github/workflows/ci.yml` → detected as YAML file

## Outputs

When run in GitHub Actions, writes to `$GITHUB_OUTPUT`:

### Components and Pipelines
- `changed-components`: Space-separated list
- `changed-pipelines`: Space-separated list
- `changed-components-json`: JSON array (compact)
- `changed-pipelines-json`: JSON array (compact)
- `changed-components-count`: Integer
- `changed-pipelines-count`: Integer
- `has-changed-components`: Boolean (true if components changed)
- `has-changed-pipelines`: Boolean (true if pipelines changed)

### File Types (Repository-wide)
- `changed-python-files`: Space-separated list of `.py` files
- `changed-python-files-json`: JSON array of `.py` files
- `changed-python-files-count`: Integer count of Python files
- `has-changed-python-files`: Boolean (true if Python files changed)
- `changed-markdown-files`: Space-separated list of `.md` files
- `changed-markdown-files-json`: JSON array of `.md` files
- `changed-markdown-files-count`: Integer count of Markdown files
- `has-changed-markdown-files`: Boolean (true if Markdown files changed)
- `changed-yaml-files`: Space-separated list of `.yaml`/`.yml` files
- `changed-yaml-files-json`: JSON array of `.yaml`/`.yml` files
- `changed-yaml-files-count`: Integer count of YAML files
- `has-changed-yaml-files`: Boolean (true if YAML files changed)

### General
- `has-changes`: Boolean (true if any changes detected)
- `all-changed-files`: Space-separated file list
- `filtered-changed-files`: Space-separated file list (if filter applied)

Also writes to `$GITHUB_STEP_SUMMARY` for job summary markdown.

When run standalone, outputs are written to temp files and displayed in terminal.

## Testing

```bash
# Create test change
git checkout -b test
echo "test" >> components/dev/demo/component.py
git add . && git commit -m "test"

# Run script
.github/scripts/detect-changed-assets/detect.sh

# Should output: ✓ Component: components/dev/demo

# Cleanup
git checkout - && git branch -D test
```

See also: [Action README](../../actions/detect-changed-assets/README.md)
