ARG FUNCTION_DIR="/function"
ARG RUNTIME_VERSION="3.9"

FROM python:${RUNTIME_VERSION}-buster as base-image

RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev


ARG FUNCTION_DIR
RUN mkdir -p ${FUNCTION_DIR}

COPY * ${FUNCTION_DIR}/

RUN python${RUNTIME_VERSION} -m pip install \
                   --target ${FUNCTION_DIR} \
                   --no-cache-dir \
                   awslambdaric \
                   -r ${FUNCTION_DIR}/requirements.txt

FROM base-image

ARG FUNCTION_DIR

WORKDIR ${FUNCTION_DIR}

COPY --from=base-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

CMD [ "app.handler" ]