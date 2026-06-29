# CAIsat developer convenience targets
# Assisted by: cursor, claude

.PHONY: pre-commit check install-hooks helm-template push-check push

pre-commit:
	SKIP=no-commit-to-branch pre-commit run --all-files

check: pre-commit

install-hooks:
	pre-commit install
	pre-commit install --hook-type commit-msg

helm-template:
	helm template test ./chart

push-check: check helm-template
	@branch="$$(git branch --show-current)"; \
	if [ "$${branch}" = "main" ] || [ "$${branch}" = "master" ]; then \
		echo "Refusing to push from $${branch}"; \
		exit 1; \
	fi

push: push-check
	git push -u origin HEAD
