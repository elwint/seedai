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

  for conf in ../../configs/*; do
    for pt_conf in ../../pt_configs/go/*.json; do
      params="-n 10 -g 200"
      [[ "$pt_conf" == *multi.json ]] && params="-n 2 -C 5 -g 2000"
      bash ./collect.sh "$results"/pt/$(basename $conf)_$(basename $pt_conf) \
        sh -c "cd $dir && python3 ../../../seedai.py -p ../../../bin/goparser $params -d ../corpus -c ../$conf -pt ../$pt_conf $args" || exit 1
    done
  done
done

echo "Done ..."
