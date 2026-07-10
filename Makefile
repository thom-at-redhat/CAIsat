# CAIsat developer convenience targets
# Assisted by: cursor, claude

.PHONY: pre-commit check install-hooks helm-template push-check push smoke scorecard-local test test-frontend fuzz-kserve-binary image push-image image-frontend push-frontend mirror-image mirror-all e2e-stub-local

pre-commit:
	SKIP=no-commit-to-branch pre-commit run --all-files

check: pre-commit helm-template test test-frontend

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
	"$${PY}" -m pip install -q -r requirements-dev.txt -r backend/requirements.txt -r backend-detection/requirements.txt; \
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$${PY}" -m pytest

test-frontend:
	cd frontend && CI=true npm test -- --watchAll=false

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

# Local Playwright gate: stub APIs + built frontend + MT-R3a layout check (no cluster).
e2e-stub-local:
	@set -o errexit -o nounset -o pipefail; \
	REPO_ROOT="$$(pwd)"; \
	STARTED_PIDS=(); \
	cleanup() { \
		for PID in "$${STARTED_PIDS[@]}"; do \
			kill "$${PID}" 2>/dev/null || true; \
		done; \
	}; \
	trap cleanup EXIT; \
	wait_for_url() { \
		local URL="$${1}"; \
		local NAME="$${2}"; \
		local ATTEMPT=0; \
		while [ "$${ATTEMPT}" -lt 60 ]; do \
			ATTEMPT=$$((ATTEMPT + 1)); \
			if curl -sf "$${URL}" >/dev/null 2>&1; then \
				echo "OK: $${NAME} ready at $${URL}"; \
				return 0; \
			fi; \
			sleep 1; \
		done; \
		echo "FAIL: $${NAME} not ready at $${URL}" >&2; \
		return 1; \
	}; \
	echo "Installing scripts/ dependencies..."; \
	cd "$${REPO_ROOT}/scripts" && npm ci; \
	npx playwright install chromium; \
	echo "Starting stub server..."; \
	node e2e-stub-server.mjs & \
	STARTED_PIDS+=("$$!"); \
	echo "Building frontend..."; \
	cd "$${REPO_ROOT}/frontend" && npm ci && npm run build; \
	echo "Serving frontend on :3000..."; \
	cd "$${REPO_ROOT}/scripts" && npx serve -s ../frontend/build -l 3000 & \
	STARTED_PIDS+=("$$!"); \
	wait_for_url "http://127.0.0.1:8080/health" "enhance stub"; \
	wait_for_url "http://127.0.0.1:8081/health" "detection stub"; \
	wait_for_url "http://127.0.0.1:3000" "frontend"; \
	echo "Running MT-R3a Playwright..."; \
	CAISAT_FRONTEND_URL=http://localhost:3000 node "$${REPO_ROOT}/scripts/mt-r3a-playwright.mjs"
