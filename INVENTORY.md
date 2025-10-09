# Inventory Guide

Inventory files define authorized targets. FortiForge will refuse to apply to any host without explicit authorization=true.

Format (YAML):

version: 1
hosts:
  - name: sandbox-web-1
    address: sandbox-web-1
    connection: docker
    labels: [web, ubuntu-22.04]
    authorized: true
  - name: sandbox-db-1
    address: sandbox-db-1
    connection: docker
    labels: [db, ubuntu-22.04]
    authorized: true
groups:
  - name: prod
    hosts: [sandbox-web-1, sandbox-db-1]
    labels: [environment:prod]

Notes:
- connection can be docker|ssh|aws|azure
- For ssh, supply username, port, and optionally key path in per-host auth block.
- For cloud, API credentials must be supplied via environment variables and allow-listing in inventory.
