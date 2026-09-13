#!/bin/bash
set -e

echo "=== INITIATING AUTOMATED INFRASTRUCTURE TEARDOWN ==="
echo "Ensuring zero cloud cost by destroying all provisioned resources..."

terraform destroy -auto-approve

echo "=== TEARDOWN COMPLETED: Cloud resources eradicated cleanly ($0 balance protected) ==="
