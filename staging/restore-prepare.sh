#!/usr/bin/env bash
env | grep -E '^(VAULT_ADDR|VAULT_AUTH_GITHUB_TOKEN)' > shared/vault_config
