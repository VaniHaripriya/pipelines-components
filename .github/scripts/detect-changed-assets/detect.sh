#!/bin/bash
# Detect changed components, pipelines, Python files, Markdown files, and YAML files
# Usage: detect.sh <base-ref> <head-ref> <include-third-party> <filter>

set -euo pipefail

# Arguments
BASE_REF="${1:-origin/main}"
HEAD_REF="${2:-HEAD}"
INCLUDE_THIRD_PARTY="${3:-true}"
FILTER="${4:-}"

# Output files
GITHUB_OUTPUT="${GITHUB_OUTPUT:-/tmp/github-output-$$.txt}"
GITHUB_STEP_SUMMARY="${GITHUB_STEP_SUMMARY:-/tmp/github-summary-$$.txt}"
touch "$GITHUB_OUTPUT" "$GITHUB_STEP_SUMMARY"

# Fetch base branch if needed
if [[ "$BASE_REF" == origin/* ]]; then
  BASE_BRANCH="${BASE_REF#origin/}"
  git fetch origin "${BASE_BRANCH}:refs/remotes/origin/${BASE_BRANCH}" 2>/dev/null || \
    git fetch --depth=100 origin "${BASE_BRANCH}" 2>/dev/null || true
fi

# Get changed files
MERGE_BASE=$(git merge-base "${BASE_REF}" "${HEAD_REF}" 2>/dev/null || echo "")
if [ -z "$MERGE_BASE" ]; then
  CHANGED_FILES=$(git diff --name-only "${BASE_REF}...${HEAD_REF}" 2>/dev/null || \
                  git diff --name-only "${BASE_REF}" "${HEAD_REF}" 2>/dev/null || echo "")
else
  CHANGED_FILES=$(git diff --name-only "${MERGE_BASE}" "${HEAD_REF}")
fi

# Apply pattern filter if specified
FILTERED_CHANGED_FILES="$CHANGED_FILES"
if [ -n "$FILTER" ]; then
  FILTERED_CHANGED_FILES=$(echo "$CHANGED_FILES" | grep -E "$FILTER" || echo "")
fi

# Parse changed files
COMPONENTS=()
PIPELINES=()
PYTHON_FILES=()
MARKDOWN_FILES=()
YAML_FILES=()

while IFS= read -r file; do
  [ -z "$file" ] && continue
  
  # Core components
  if [[ "$file" =~ ^components/([^/]+)/([^/]+)/ ]]; then
    COMPONENT_PATH="components/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    [[ ! " ${COMPONENTS[@]} " =~ " ${COMPONENT_PATH} " ]] && COMPONENTS+=("${COMPONENT_PATH}")
  fi
  
  # Core pipelines
  if [[ "$file" =~ ^pipelines/([^/]+)/([^/]+)/ ]]; then
    PIPELINE_PATH="pipelines/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    [[ ! " ${PIPELINES[@]} " =~ " ${PIPELINE_PATH} " ]] && PIPELINES+=("${PIPELINE_PATH}")
  fi
  
  # Third-party (if enabled)
  if [[ "$INCLUDE_THIRD_PARTY" == "true" ]]; then
    if [[ "$file" =~ ^third_party/components/([^/]+)/([^/]+)/ ]]; then
      COMPONENT_PATH="third_party/components/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
      [[ ! " ${COMPONENTS[@]} " =~ " ${COMPONENT_PATH} " ]] && COMPONENTS+=("${COMPONENT_PATH}")
    fi
    
    if [[ "$file" =~ ^third_party/pipelines/([^/]+)/([^/]+)/ ]]; then
      PIPELINE_PATH="third_party/pipelines/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
      [[ ! " ${PIPELINES[@]} " =~ " ${PIPELINE_PATH} " ]] && PIPELINES+=("${PIPELINE_PATH}")
    fi
  fi
  
  # Detect Python files anywhere in repository
  if [[ "$file" =~ \.py$ ]]; then
    [[ ! " ${PYTHON_FILES[@]} " =~ " ${file} " ]] && PYTHON_FILES+=("${file}")
  fi
  
  # Detect Markdown files anywhere in repository
  if [[ "$file" =~ \.md$ ]]; then
    [[ ! " ${MARKDOWN_FILES[@]} " =~ " ${file} " ]] && MARKDOWN_FILES+=("${file}")
  fi
  
  # Detect YAML files anywhere in repository (.yaml or .yml)
  if [[ "$file" =~ \.(yaml|yml)$ ]]; then
    [[ ! " ${YAML_FILES[@]} " =~ " ${file} " ]] && YAML_FILES+=("${file}")
  fi
done <<< "$FILTERED_CHANGED_FILES"

# Generate outputs
COMPONENT_COUNT="${#COMPONENTS[@]}"
PIPELINE_COUNT="${#PIPELINES[@]}"
PYTHON_FILES_COUNT="${#PYTHON_FILES[@]}"
MARKDOWN_FILES_COUNT="${#MARKDOWN_FILES[@]}"
YAML_FILES_COUNT="${#YAML_FILES[@]}"
COMPONENTS_LIST="${COMPONENTS[*]}"
PIPELINES_LIST="${PIPELINES[*]}"
PYTHON_FILES_LIST="${PYTHON_FILES[*]}"
MARKDOWN_FILES_LIST="${MARKDOWN_FILES[*]}"
YAML_FILES_LIST="${YAML_FILES[*]}"

# JSON arrays (compact)
if [ ${COMPONENT_COUNT} -eq 0 ]; then
  COMPONENTS_JSON="[]"
else
  COMPONENTS_JSON=$(printf '%s\n' "${COMPONENTS[@]}" | jq -R . | jq -sc .)
fi

if [ ${PIPELINE_COUNT} -eq 0 ]; then
  PIPELINES_JSON="[]"
else
  PIPELINES_JSON=$(printf '%s\n' "${PIPELINES[@]}" | jq -R . | jq -sc .)
fi

if [ ${PYTHON_FILES_COUNT} -eq 0 ]; then
  PYTHON_FILES_JSON="[]"
else
  PYTHON_FILES_JSON=$(printf '%s\n' "${PYTHON_FILES[@]}" | jq -R . | jq -sc .)
fi

if [ ${MARKDOWN_FILES_COUNT} -eq 0 ]; then
  MARKDOWN_FILES_JSON="[]"
else
  MARKDOWN_FILES_JSON=$(printf '%s\n' "${MARKDOWN_FILES[@]}" | jq -R . | jq -sc .)
fi

if [ ${YAML_FILES_COUNT} -eq 0 ]; then
  YAML_FILES_JSON="[]"
else
  YAML_FILES_JSON=$(printf '%s\n' "${YAML_FILES[@]}" | jq -R . | jq -sc .)
fi

# Booleans
HAS_CHANGED_COMPONENTS=$([ ${COMPONENT_COUNT} -gt 0 ] && echo "true" || echo "false")
HAS_CHANGED_PIPELINES=$([ ${PIPELINE_COUNT} -gt 0 ] && echo "true" || echo "false")
HAS_CHANGED_PYTHON_FILES=$([ ${PYTHON_FILES_COUNT} -gt 0 ] && echo "true" || echo "false")
HAS_CHANGED_MARKDOWN_FILES=$([ ${MARKDOWN_FILES_COUNT} -gt 0 ] && echo "true" || echo "false")
HAS_CHANGED_YAML_FILES=$([ ${YAML_FILES_COUNT} -gt 0 ] && echo "true" || echo "false")
HAS_CHANGES=$(([ ${COMPONENT_COUNT} -gt 0 ] || [ ${PIPELINE_COUNT} -gt 0 ] || [ ${PYTHON_FILES_COUNT} -gt 0 ] || [ ${MARKDOWN_FILES_COUNT} -gt 0 ] || [ ${YAML_FILES_COUNT} -gt 0 ]) && echo "true" || echo "false")

# Write outputs
{
  echo "changed-components=${COMPONENTS_LIST}"
  echo "changed-pipelines=${PIPELINES_LIST}"
  echo "changed-components-json=${COMPONENTS_JSON}"
  echo "changed-pipelines-json=${PIPELINES_JSON}"
  echo "changed-components-count=${COMPONENT_COUNT}"
  echo "changed-pipelines-count=${PIPELINE_COUNT}"
  echo "has-changes=${HAS_CHANGES}"
  echo "has-changed-components=${HAS_CHANGED_COMPONENTS}"
  echo "has-changed-pipelines=${HAS_CHANGED_PIPELINES}"
  echo "changed-python-files=${PYTHON_FILES_LIST}"
  echo "changed-python-files-json=${PYTHON_FILES_JSON}"
  echo "changed-python-files-count=${PYTHON_FILES_COUNT}"
  echo "has-changed-python-files=${HAS_CHANGED_PYTHON_FILES}"
  echo "changed-markdown-files=${MARKDOWN_FILES_LIST}"
  echo "changed-markdown-files-json=${MARKDOWN_FILES_JSON}"
  echo "changed-markdown-files-count=${MARKDOWN_FILES_COUNT}"
  echo "has-changed-markdown-files=${HAS_CHANGED_MARKDOWN_FILES}"
  echo "changed-yaml-files=${YAML_FILES_LIST}"
  echo "changed-yaml-files-json=${YAML_FILES_JSON}"
  echo "changed-yaml-files-count=${YAML_FILES_COUNT}"
  echo "has-changed-yaml-files=${HAS_CHANGED_YAML_FILES}"
  echo "all-changed-files=$(echo "$CHANGED_FILES" | tr '\n' ' ')"
  echo "filtered-changed-files=$(echo "$FILTERED_CHANGED_FILES" | tr '\n' ' ')"
} >> "$GITHUB_OUTPUT"

# Write summary
{
  echo "## Changed Assets"
  echo ""
  echo "**Components:** ${COMPONENT_COUNT}"
  [ ${COMPONENT_COUNT} -gt 0 ] && printf '%s\n' "${COMPONENTS[@]}" | sed 's/^/- /'
  echo ""
  echo "**Pipelines:** ${PIPELINE_COUNT}"
  [ ${PIPELINE_COUNT} -gt 0 ] && printf '%s\n' "${PIPELINES[@]}" | sed 's/^/- /'
  echo ""
  echo "**Python Files:** ${PYTHON_FILES_COUNT}"
  [ ${PYTHON_FILES_COUNT} -gt 0 ] && printf '%s\n' "${PYTHON_FILES[@]}" | sed 's/^/- /'
  echo ""
  echo "**Markdown Files:** ${MARKDOWN_FILES_COUNT}"
  [ ${MARKDOWN_FILES_COUNT} -gt 0 ] && printf '%s\n' "${MARKDOWN_FILES[@]}" | sed 's/^/- /'
  echo ""
  echo "**YAML Files:** ${YAML_FILES_COUNT}"
  [ ${YAML_FILES_COUNT} -gt 0 ] && printf '%s\n' "${YAML_FILES[@]}" | sed 's/^/- /'
} >> "$GITHUB_STEP_SUMMARY"

# Show output if running standalone
if [ -z "${GITHUB_ACTIONS:-}" ]; then
  echo "Components: ${COMPONENT_COUNT}"
  [ ${COMPONENT_COUNT} -gt 0 ] && printf '  - %s\n' "${COMPONENTS[@]}"
  echo "Pipelines: ${PIPELINE_COUNT}"
  [ ${PIPELINE_COUNT} -gt 0 ] && printf '  - %s\n' "${PIPELINES[@]}"
  echo "Python Files: ${PYTHON_FILES_COUNT}"
  [ ${PYTHON_FILES_COUNT} -gt 0 ] && printf '  - %s\n' "${PYTHON_FILES[@]}"
  echo "Markdown Files: ${MARKDOWN_FILES_COUNT}"
  [ ${MARKDOWN_FILES_COUNT} -gt 0 ] && printf '  - %s\n' "${MARKDOWN_FILES[@]}"
  echo "YAML Files: ${YAML_FILES_COUNT}"
  [ ${YAML_FILES_COUNT} -gt 0 ] && printf '  - %s\n' "${YAML_FILES[@]}"
fi

exit 0
