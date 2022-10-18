#!/bin/sh -e

export PREFIX=""
if [ -d 'venv' ] ; then
    export PREFIX="venv/bin/"
fi

set -x

${PREFIX}black --target-version=py36 charset_normalizer
${PREFIX}isort charset_normalizer
