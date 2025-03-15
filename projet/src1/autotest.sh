#!/bin/bash

echo "automatisation of testing omp"

make all
for threads in 1 2 3 4 5 6 7 8
do
    for time in 1 2 3 4 5
    do
        echo "threads $threads"
        OMP_NUM_THREADS=$threads ./simulation.exe
    done
done
