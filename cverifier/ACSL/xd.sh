#!/bin/bash

for f in *.c
do
    python3 removeAt.py $f
done
