# CAIsat developer convenience targets
# Assisted by: cursor, claude

.PHONY: pre-commit check install-hooks helm-template push-check push smoke scorecard-local

pre-commit:
	SKIP=no-commit-to-branch pre-commit run --all-files

check: pre-commit helm-template

install-hooks:
	pre-commit install
	pre-commit install --hook-type commit-msg

helm-template:
	@command -v helm >/dev/null 2>&1 || { \
		echo "helm is not installed; install from https://helm.sh/docs/intro/install/"; \
		exit 1; \
	}
	helm template test ./chart

push-check: check
	@branch="$$(git branch --show-current)"; \
	if [ "$${branch}" = "main" ] || [ "$${branch}" = "master" ]; then \
		echo "Refusing to push from $${branch}"; \
		exit 1; \
	fi

push: push-check
	git push -u origin HEAD

smoke:
	bash scripts/smoke-local.sh

scorecard-local:
	bash scripts/scorecard-local.sh
