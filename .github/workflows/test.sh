test_plan=''

# ret=$(../../utils/manifest_get_compare.py --test_plan="com.canonical.certification::client-cert-desktop-24-04" --new_manifest="new.json" --orig_manifest="../../pc/default/manifest.json")
../../utils/manifest_get_compare.py --test_plan="com.canonical.certification::client-cert-desktop-24-04" --new_manifest="new.json" --orig_manifest="../../pc/default/manifest.json"
[ $? -eq 0 ] && cp new.json pc/default/manifest.json

git diff --quiet
if [ $? -eq 0 ]; then
  echo "no change"
  exit 0
else
  echo "cnange"
  # git config user.name "${{ github.actor }}"
  # git config user.email "${{ github.actor_id }}+${{ github.actor }}@users.noreply.github.com"
  # git commit -a -m "update default manifest for pc"
  # git push
fi