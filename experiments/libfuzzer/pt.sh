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

echo "Init ..."
sh -c "cd ../../test && python3 ../seedai.py -v -p ../bin/goparser -n 1 -d /tmp -c ../configs/temp_0.8.json -g 1 $args" || exit 1
echo "Running ..."

for conf in ../../configs/*; do
  for pt_conf in ../../pt_configs/go/*.json; do
    params="-n 10"
    [[ "$pt_conf" == *multi.json ]] && params="-n 2 -C 5"
    bash ./collect.sh "$1"/pt/$(basename $conf)_$(basename $pt_conf) \
      sh -c "cd source && python3 ../../../seedai.py -v -p ../../../bin/goparser $params -d ../corpus -c ../$conf -pt ../$pt_conf $args" || exit 1
  done
done

echo "Done ..."
