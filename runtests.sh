#!/bin/bash
cd nexus/test
for testfile in `ls -1 *.py`; do
    echo $testfile
    python $testfile
done

cd test_tools
for testfile in `ls -1 *.py`; do
    echo $testfile
    python $testfile
done

cd ../..