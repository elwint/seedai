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

for i in {1..4}; do
  for conf in ../../configs/*; do
    timeout 10m bash ./collect.sh "$1"/ft/$(basename $conf)_$i \
      sh -c "cd source && ../../../seedai.py -v -p ../../../bin/goparser -C 20 -d ../corpus -c ../$conf $args"
    exit_status=$?
    if [[ $exit_status -ne 0 ]] && [[ $exit_status -ne 124 ]]; then
      exit $exit_status
    fi
  done
done
