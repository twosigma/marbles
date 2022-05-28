#!/bin/bash

set -e
set -u

(
    cd marbles/core
    pip-compile --upgrade --generate-hashes
)
(
    cd marbles/mixins
    pip-compile --upgrade --generate-hashes
)
pip-compile --upgrade --generate-hashes requirements.in
pip-compile --upgrade --generate-hashes dev-requirements.in
