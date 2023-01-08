PYTHON_FILES = `(find . -type f -iname "*.py" -not -path "./.venv/*")`
TOML_FILES = `(find . -iname "*.toml" -o -not -path "**/.venv/**")`


setup: ## Install developer experience
	yarn install
	yarn husky:setup

setup-hard: ## Install developer experience with no cache
	rm -rf node_modules/
	yarn cache clean
	make setup

install: ## Install package dependencies
	poetry install --sync

install-hard: ## Install package dependencies from scratch
	rm -rf .venv/
	make install

poetry-update: ## Upgrade poetry and dependencies
	poetry self update
	poetry run pip install --upgrade pip wheel setuptools
	poetry update

poetry-export: ## Export as requirements.txt
	poetry export -f requirements.txt --output requirements.txt --without dev,devops,quality --without-hashes

toml-sort: ## Upgrade poetry and dependencies
	poetry run toml-sort --all --in-place $(TOML_FILES)

start: ## Start streamlit application locally
	poetry run streamlit run ./src/cassini/application/main.py

black: ## Run Black
	poetry run black --check --quiet $(PYTHON_FILES)

black-fix: ## Run Black with automated fix
	poetry run black --quiet $(PYTHON_FILES)

isort: ## Run Isort
	poetry run isort --check-only $(PYTHON_FILES)

isort-fix: ## Run Isort with automated fix
	poetry run isort $(PYTHON_FILES)

mypy: ## Run Mypy
	poetry run mypy $(PYTHON_FILES)

pytest: ## Run Pytest
	poetry run pytest tests/

pytest-coverage: ## Run coverage report
	poetry run coverage run -m pytest tests/
	poetry run coverage report

ruff: ## Run Ruff
	poetry run ruff $(PYTHON_FILES)

ruff-fix: ## Run Ruff with automated fix
	poetry run ruff --fix $(PYTHON_FILES)


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
