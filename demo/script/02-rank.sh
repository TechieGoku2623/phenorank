#!/usr/bin/env bash
set +e
phenorank rank --vignette data/sample/classic.txt --explain --summary
exit $?
