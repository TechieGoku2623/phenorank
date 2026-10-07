#!/usr/bin/env bash
set +e
phenorank rank --vignette data/sample/negation.txt --compare-naive
exit $?
