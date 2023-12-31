#!/bin/bash
set -o pipefail

if [ -f "$1"/data.out ]; then
  echo "Warning: $1/data.out already exists, skipping ..."
  exit 0
fi

if [ -z "$SOURCE_DIR" ] || [ ! -f "./$SOURCE_DIR/libfuzzer" ]; then
  echo "Cannot find libfuzzer in SOURCE_DIR: ./$SOURCE_DIR/libfuzzer"
  exit 1
fi

mkdir -p "$1" || exit 1

rm -r corpus
mkdir corpus || exit 1

date +"START: %Y-%m-%d %H:%M:%S.%3N" >"$1"/data.out || exit 1

if [ ! -z "$2" ]; then
  echo "${@:2}"
  "${@:2}" || exit 1
  cp -r corpus "$1"/corpus # Log generated corpus
  date +"SEEDS: %Y-%m-%d %H:%M:%S.%3N" >>"$1"/data.out
fi

date +"RUN: %Y-%m-%d %H:%M:%S.%3N" >>"$1"/data.out
awk '{
  if (match($0, /cov: ([0-9]+)/, covArr) && match($0, /ft: ([0-9]+)/, ftArr)) {
    system("date +\"%Y-%m-%d %H:%M:%S.%3N\" | tr -d \"\\n\"");
    printf ",cov: %s,ft: %s\n", covArr[1], ftArr[1]
  }
}' < <(
timeout 10m ./$SOURCE_DIR/libfuzzer corpus -use_value_profile=1 2>&1 >>"$1"/data.out | tee "$1"/log.out
exit_status=$?
if [[ $exit_status -eq 124 ]]; then
  date +"TIMEDOUT: %Y-%m-%d %H:%M:%S.%3N" >>"$1"/data.out
else
  date +"DONE: %Y-%m-%d %H:%M:%S.%3N" >>"$1"/data.out
fi
) >"$1"/cov.out

exit 0
