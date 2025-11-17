PYTHON_SOURCES := $(shell find components pipelines third_party scripts -name "*.py")
MARKDOWN_SOURCES := $(shell find . -name "*.md" -not -path "./.git/*" -not -path "./.venv/*")
YAML_SOURCES := $(shell find . -name "*.yml" -o -name "*.yaml" -not -path "./.git/*" -not -path "./.venv/*")

BLACK ?= black
PYDOCSTYLE ?= pydocstyle
MARKDOWNLINT ?= markdownlint
YAMLLINT ?= yamllint
PYTHON ?= python3

.PHONY: format lint lint-black lint-docstrings lint-markdown lint-yaml lint-imports check-imports

format:
	$(BLACK) --config pyproject.toml $(PYTHON_SOURCES)

lint: lint-black lint-docstrings lint-markdown lint-yaml lint-imports

lint-black:
	$(BLACK) --config pyproject.toml --check $(PYTHON_SOURCES)

lint-docstrings:
	$(PYDOCSTYLE) --config=pyproject.toml $(PYTHON_SOURCES)

lint-markdown:
	$(MARKDOWNLINT) -c .markdownlint.json $(MARKDOWN_SOURCES)

lint-yaml:
	$(YAMLLINT) -c .yamllint.yml $(YAML_SOURCES)

lint-imports:
	$(PYTHON) scripts/check_imports.py components pipelines third_party scripts

check-imports: lint-imports

