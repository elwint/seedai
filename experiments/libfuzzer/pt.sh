#!/bin/bash
if [ ! -d "$1" ]; then
  echo "$1 does not exist."
  exit 1
fi
if [ -z "$2" ]; then
  echo "Need args"
  exit 1
fi
args="${@:2}"

for conf in ../../configs/*; do
  for pt_conf in ../../pt_configs/go/*.json; do
    params="-n 10"
    [[ "$pt_conf" == *multi.json ]] && params="-n 2 -C 5"
    timeout 10m bash ./collect.sh "$1"/pt/$(basename $conf)_$(basename $pt_conf) \
      sh -c "cd source && ../../../seedai.py -v -p ../../../bin/goparser $params -d ../corpus -c ../$conf -pt ../$pt_conf $args"
    exit_status=$?
    if [[ $exit_status -ne 0 ]] && [[ $exit_status -ne 124 ]]; then
      exit $exit_status
    fi
  done
done
