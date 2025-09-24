#!/bin/bash

for i in */;do
    echo $i

    # Append to subject list (removing last character slash)
    echo ${i%?} >> subjects.txt
done


