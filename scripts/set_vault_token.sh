#!/usr/bin/env bash
echo -n "Please provide your GitHub personal access token for the vault: "
read -s token
echo ""
export VAULT_AUTH_GITHUB_TOKEN=${token}
