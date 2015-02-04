#!/bin/sh
date=`date`
dir=${date// /-}
dir="$1Archive-Of-$dir"
echo "Archiving logs to $dir"
mkdir logs/$dir
mv logs/*.err logs/$dir
mv logs/*.out logs/$dir
