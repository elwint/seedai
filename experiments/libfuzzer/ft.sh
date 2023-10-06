#!/bin/bash
if [ -z "$1" ]; then
  echo "Need results folder name"
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

for dir in source_*; do
  export SOURCE_DIR="$dir"
  folder_name_without_prefix="${dir#source_}"
  results="./results/$folder_name_without_prefix/$1"

  for i in {1..4}; do
    for conf in ../../configs/*; do
      bash ./collect.sh "$results"/ft/$(basename $conf)_$i \
        sh -c "cd $dir && python3 ../../../seedai.py -p ../../../bin/goparser -n 10 -g 200 -d ../corpus -c ../$conf $args" || exit 1
    done
  done
done

echo "Done ..."
