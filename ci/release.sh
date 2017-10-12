#!/bin/bash -xe

DIR=$(dirname $0)
"${DIR}/build.sh"
"${MINICONDA}/bin/ts-conda-upload" ts "$("${MINICONDA}/bin/conda" build --python "${PYTHON_VERSION}" --output recipe)"