# ClusterFuzzLite image for decode_kserve_binary fuzz target (MT-SC31-CFL).
# Assisted by: cursor, claude

FROM gcr.io/oss-fuzz-base/base-builder-python:v1@sha256:6768b69b56e3c6e654742e5109559fc37601b45d0cfe2e15ecb8e14f0e941a57

COPY . ${SRC}
WORKDIR ${SRC}

RUN pip install --no-cache-dir --require-hashes --requirement .clusterfuzzlite/requirements-fuzz.txt

RUN bash .clusterfuzzlite/build.sh
