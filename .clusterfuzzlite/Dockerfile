# ClusterFuzzLite image for decode_kserve_binary fuzz target (MT-SC31-CFL).
# Assisted by: cursor, claude

FROM gcr.io/oss-fuzz-base/base-builder-python:v1

COPY . ${SRC}
WORKDIR ${SRC}

RUN pip install --no-cache-dir --requirement .clusterfuzzlite/requirements-fuzz.txt

RUN bash .clusterfuzzlite/build.sh
