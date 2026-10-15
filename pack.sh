#!/usr/bin/env sh
# Packs a widget folder into widgets/<name>-<version>.zip and prints
# the registry fields that describe it. Usage: ./pack.sh ../my-widget
set -eu
src=${1:?usage: ./pack.sh <widget folder>}
here=$(cd "$(dirname "$0")" && pwd)
name=$(node -p "require('$(cd "$src" && pwd)/manifest.json').name")
version=$(node -p "require('$(cd "$src" && pwd)/manifest.json').version")
out="$here/widgets/$name-$version.zip"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
# Fixed timestamps and no extra attributes, so the same files give the same ZIP.
cp -R "$src"/. "$tmp"/
find "$tmp" -exec touch -t 202001010000 {} +
rm -f "$out"
(cd "$tmp" && find . -type f ! -name '.*' | sort | sed 's|^\./||' | zip -X -q "$out" -@)
sha=$(sha256sum "$out" 2>/dev/null || shasum -a 256 "$out")
echo "\"version\": \"$version\","
echo "\"zip\": \"widgets/$name-$version.zip\","
echo "\"sha256\": \"${sha%% *}\""
