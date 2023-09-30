#!/bin/sh -e

export PREFIX=""
if [ -d 'venv' ] ; then
    export PREFIX="venv/bin/"
fi

set -x

${PREFIX}pip install -r ./dev-requirements.txt
${PREFIX}black --target-version=py37 charset_normalizer
${PREFIX}isort charset_normalizer
