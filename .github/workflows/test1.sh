#!/bin/bash

# Define the test plan and manifest paths
TEST_PLAN="com.canonical.certification::client-cert-desktop-24-04"
NEW_MANIFEST="new.json"
ORIG_MANIFEST="../../pc/default/manifest.json"

# Run the manifest comparison script
../../utils/manifest_get_compare.py --test_plan="$TEST_PLAN" --new_manifest="$NEW_MANIFEST" --orig_manifest="$ORIG_MANIFEST"

# Check the exit status of the previous command
if [ $? -eq 0 ]; then
  cp "$NEW_MANIFEST" "$ORIG_MANIFEST"
else
  echo "Error: Manifest comparison failed."
  exit 1
fi

# Check for changes in the git repository
if git diff --quiet; then
  echo "No change"
  exit 0
else
  echo "Change detected"
  # Uncomment the following lines to enable git commit and push
  # git config user.name "${{ github.actor }}"
  # git config user.email "${{ github.actor_id }}+${{ github.actor }}@users.noreply.github.com"
  # git commit -a -m "Update default manifest for PC"
  # git push
fi