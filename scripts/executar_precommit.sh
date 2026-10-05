#!/usr/bin/env bash

docker compose -f docker-compose-dev.yml run --rm gateway pre-commit run --all-files