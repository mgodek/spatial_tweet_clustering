#!/bin/bash

FILE="tweets.tar.gz"

if [ -f $FILE ];
then
    tar -zxvf $FILE >/dev/null 2>&1
    rm $FILE
fi
