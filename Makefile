# CAIsat developer convenience targets
# Assisted by: cursor, claude

.PHONY: pre-commit check install-hooks

pre-commit:
	SKIP=no-commit-to-branch pre-commit run --all-files

check: pre-commit

install-hooks:
	pre-commit install
	pre-commit install --hook-type commit-msg
