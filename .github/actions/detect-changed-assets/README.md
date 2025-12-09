# Detect Changed Components and Pipelines

Custom GitHub Action to detect changed components, pipelines, and file types (Python, Markdown, YAML) across the repository.

## Quick Start

```yaml
name: Test Changed Components
on: pull_request

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required!
      
      - name: Detect changes
        id: changes
        uses: ./.github/actions/detect-changed-assets
      
      - name: Test components
        if: steps.changes.outputs.has-changes == 'true'
        run: |
          for component in ${{ steps.changes.outputs.changed-components }}; do
            pytest $component/tests/
          done
```

## Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `base-ref` | Base git reference to compare against | `origin/main` |
| `head-ref` | Head git reference | `HEAD` |
| `include-third-party` | Include third_party/ directory | `true` |
| `filter` | Grep pattern to filter changed files | _(empty)_ |

## Outputs

| Output | Description | Example |
|--------|-------------|---------|
| `has-changes` | Boolean - any changes? | `"true"` |
| `has-changed-components` | Boolean - components changed? | `"true"` |
| `has-changed-pipelines` | Boolean - pipelines changed? | `"false"` |
| `changed-components` | Space-separated list | `"components/training/trainer"` |
| `changed-components-json` | JSON array for matrix | `["components/training/trainer"]` |
| `changed-components-count` | Count | `"1"` |
| `changed-pipelines` | Space-separated list | `"pipelines/training/pipeline"` |
| `changed-pipelines-json` | JSON array for matrix | `["pipelines/training/pipeline"]` |
| `changed-pipelines-count` | Count | `"1"` |
| `changed-python-files` | Space-separated list of `.py` files | `"setup.py scripts/helper.py"` |
| `changed-python-files-json` | JSON array of Python files | `["setup.py", "scripts/helper.py"]` |
| `changed-python-files-count` | Count of Python files | `"2"` |
| `has-changed-python-files` | Boolean - Python files changed? | `"true"` |
| `changed-markdown-files` | Space-separated list of `.md` files | `"README.md docs/guide.md"` |
| `changed-markdown-files-json` | JSON array of Markdown files | `["README.md", "docs/guide.md"]` |
| `changed-markdown-files-count` | Count of Markdown files | `"2"` |
| `has-changed-markdown-files` | Boolean - Markdown files changed? | `"true"` |
| `changed-yaml-files` | Space-separated list of `.yaml`/`.yml` files | `".github/workflows/ci.yml"` |
| `changed-yaml-files-json` | JSON array of YAML files | `[".github/workflows/ci.yml"]` |
| `changed-yaml-files-count` | Count of YAML files | `"1"` |
| `has-changed-yaml-files` | Boolean - YAML files changed? | `"true"` |
| `all-changed-files` | All changed files | `"components/training/trainer/component.yaml pipelines/training/pipeline/pipeline.py"` |
| `filtered-changed-files` | Changed files matching any filter pattern | `"components/training/trainer/component.yaml"` |

## Common Patterns

### Matrix Strategy (Parallel Testing)

```yaml
jobs:
  detect:
    outputs:
      components: ${{ steps.changes.outputs.changed-components-json }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - id: changes
        uses: ./.github/actions/detect-changed-assets
  
  test:
    needs: detect
    strategy:
      matrix:
        component: ${{ fromJson(needs.detect.outputs.components) }}
    steps:
      - run: pytest ${{ matrix.component }}/tests/
```

### Conditional Execution

```yaml
- id: changes
  uses: ./.github/actions/detect-changed-assets

- name: Run if any changes
  if: steps.changes.outputs.has-changes == 'true'
  run: ./run-all-tests.sh

- name: Component-specific task
  if: steps.changes.outputs.has-changed-components == 'true'
  run: ./validate-components.sh

- name: Pipeline-specific task
  if: steps.changes.outputs.has-changed-pipelines == 'true'
  run: ./validate-pipelines.sh

- name: Run ruff format check (changed files)
  if: steps.changes.outputs.has-changed-python-files == 'true'
  run: |
    uv run ruff format --check ${{ steps.changes.outputs.changed-python-files }}

- name: Run ruff lint (changed files)
  if: steps.changes.outputs.has-changed-python-files == 'true'
  run: |
    uv run ruff check ${{ steps.changes.outputs.changed-python-files }}

- name: Run markdownlint (changed files)
  if: steps.changes.outputs.has-changed-markdown-files == 'true'
  run: |
    markdownlint -c .markdownlint.json -- ${{ steps.changes.outputs.changed-markdown-files }}
```

### Process Each Asset

```yaml
- id: changes
  uses: ./.github/actions/detect-changed-assets

- run: |
    for component in ${{ steps.changes.outputs.changed-components }}; do
      echo "Processing $component"
      pytest $component/tests/
    done
```

### Filter by File Pattern

Detect changes only in specific file types:

```yaml
- uses: ./.github/actions/detect-changed-assets
  with:
    filter: '\.py$'  # Only Python files

- uses: ./.github/actions/detect-changed-assets
  with:
    filter: '\.(py|yaml)$'  # Python or YAML files

- uses: ./.github/actions/detect-changed-assets
  with:
    filter: '^components/.*/tests/'  # Only test files in components
```

## Testing Locally

```bash
# Test the detection script directly
.github/scripts/detect-changed-assets/detect.sh origin/main HEAD true

# With pattern filter (4th argument)
.github/scripts/detect-changed-assets/detect.sh origin/main HEAD true '\.py$'

# Or run the full test suite
.github/actions/detect-changed-assets/test.sh
```

## How It Works

1. Fetches base branch if needed
2. Finds merge base between base and head refs
3. Gets changed files via `git diff`
4. Parses paths to identify components/pipelines:
   - `components/<category>/<name>/` → `components/<category>/<name>`
   - `pipelines/<category>/<name>/` → `pipelines/<category>/<name>`
   - Same for `third_party/` if enabled
5. Detects changed file types across the entire repository:
   - Python files (`.py`)
   - Markdown files (`.md`)
   - YAML files (`.yaml`, `.yml`)
6. Deduplicates (multiple files in same component = one entry)
7. Outputs in multiple formats (space-separated lists, JSON arrays, counts, booleans)
