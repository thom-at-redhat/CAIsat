# CAIsat developer convenience targets
# Assisted by: cursor, claude

.PHONY: pre-commit check install-hooks helm-template push-check push smoke scorecard-local test fuzz-kserve-binary image push-image image-frontend push-frontend mirror-image mirror-all

pre-commit:
	SKIP=no-commit-to-branch pre-commit run --all-files

check: pre-commit helm-template test

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

# Build a workload image (COMPONENT=frontend|backend|detection-backend|backend-changedetection; chart tag matches).
# Override registry with CAISAT_IMAGE_REPO=quay.io/<your-quay-user>/caisat (else chart/values.yaml)
image:
	bash scripts/build-image.sh

push-image:
	PUSH=1 bash scripts/build-image.sh

image-frontend:
	COMPONENT=frontend $(MAKE) image

push-frontend:
	COMPONENT=frontend $(MAKE) push-image

# Pull/retag/push pre-built OCI images (model, yoloobb, sentinel2, backend-changedetection).
# CAISAT_UPSTREAM_REPO defaults to quay.io/rh-ai-quickstart/caisat; destination from chart/values.yaml.
mirror-image:
	bash scripts/mirror-image.sh

mirror-all:
	COMPONENT=all bash scripts/mirror-image.sh

smoke:
	bash scripts/smoke-local.sh

test:
	@PY="python3.12"; command -v "$${PY}" >/dev/null 2>&1 || PY="python3"; \
	"$${PY}" -m pip install -q -r requirements-dev.txt -r backend/requirements.txt; \
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$${PY}" -m pytest

scorecard-local:
	bash scripts/scorecard-local.sh

# Local Atheris spike for decode_kserve_binary (~45s default; override FUZZ_TIME / FUZZ_RUNS).
fuzz-kserve-binary:
	@PY="python3.12"; command -v "$${PY}" >/dev/null 2>&1 || PY="python3"; \
	"$${PY}" -m pip install -q atheris numpy -r backend/requirements.txt; \
	FUZZ_TIME="$${FUZZ_TIME:-45}"; FUZZ_RUNS="$${FUZZ_RUNS:-}"; \
	if [ -n "$${FUZZ_RUNS}" ]; then \
		"$${PY}" .clusterfuzzlite/fuzz_kserve_binary_fuzzer.py -runs="$${FUZZ_RUNS}"; \
	else \
		"$${PY}" .clusterfuzzlite/fuzz_kserve_binary_fuzzer.py -max_total_time="$${FUZZ_TIME}"; \
	fi
