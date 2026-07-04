# ClusterFuzzLite image stub for future Phase 31 CI (not wired in workflows yet).
# Assisted by: cursor, claude

FROM gcr.io/oss-fuzz-base/base-builder-python:v1

COPY . ${SRC}
WORKDIR ${SRC}

RUN pip install --no-cache-dir --requirement .clusterfuzzlite/requirements-fuzz.txt

RUN bash .clusterfuzzlite/build.sh
