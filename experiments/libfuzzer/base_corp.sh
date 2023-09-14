#!/bin/bash
if [ ! -d "$1" ]; then
  echo "$1 does not exist."
  exit 1
fi
for i in {1..14}; do
  bash ./collect.sh "$1"/base_corp/$i \
    sh -c "rm -r corpus && cp -r base_corp corpus" || exit 1
done
