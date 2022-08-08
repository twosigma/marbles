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
pip-compile --upgrade --generate-hashes requirements/base.in
pip-compile --upgrade --generate-hashes requirements/dev.in
