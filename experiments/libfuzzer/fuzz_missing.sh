#!/bin/bash
set -o pipefail

for source in clean_html iban saml; do
  if [ ! -f "./source_$source/libfuzzer" ]; then
    echo "Cannot find libfuzzer for $source: ./source_$source/libfuzzer"
    exit 1
  fi
done

for source in clean_html iban saml; do # In this order (saml/deflate last)
  for dir in ./results/$source/*/*/*; do
    echo "In: $dir"
    if [ -f "$dir"/cov.out ]; then
      echo "Warning: $dir/cov.out already exists, skipping ..."
      continue
    fi

    rm -r corpus
    cp -r "$dir/corpus" corpus || exit 1

    date +"RUN: %Y-%m-%d %H:%M:%S.%3N" >>"$dir"/data.out
    awk '{
      if (match($0, /cov: ([0-9]+)/, covArr) && match($0, /ft: ([0-9]+)/, ftArr)) {
        system("date +\"%Y-%m-%d %H:%M:%S.%3N\" | tr -d \"\\n\"");
        printf ",cov: %s,ft: %s\n", covArr[1], ftArr[1]
      }
    }' < <(
    timeout 10m ./source_$source/libfuzzer corpus -use_value_profile=1 2>&1 >>"$dir"/data.out | tee "$dir"/log.out
    exit_status=$?
    if [[ $exit_status -eq 124 ]]; then
      date +"TIMEDOUT: %Y-%m-%d %H:%M:%S.%3N" >>"$dir"/data.out
    else
      date +"DONE: %Y-%m-%d %H:%M:%S.%3N" >>"$dir"/data.out
    fi
    ) >"$dir"/cov.out
  done
done
