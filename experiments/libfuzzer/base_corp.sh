#!/bin/bash
for dir in source_*; do
  folder_name_without_prefix="${dir#source_}"
  results="./results/$folder_name_without_prefix"

  for i in {1..14}; do
    bash ./collect.sh "$results"/base_corp/$i \
      sh -c "rm -r corpus && cp -r base_corp corpus" || exit 1
  done
done
echo "Done ..."
