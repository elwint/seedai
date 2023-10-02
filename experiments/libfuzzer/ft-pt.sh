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

for i in {1..4}; do
  for conf in ../../configs/*; do
    bash ./collect.sh "$1"/ft/$(basename $conf)_$i \
      sh -c "cd source && python3 ../../../seedai.py -v -p ../../../bin/goparser -n 10 -d ../corpus -c ../$conf -pt ../../../pt_configs/go/openai_ft/gpt-3.5-turbo.json $args" || exit 1
  done
done

echo "Done ..."
