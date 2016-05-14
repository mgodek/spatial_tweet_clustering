#!/bin/bash

sudo pip install geojson
sudo pip install tweepy
sudo pip install rpy2

FILE="tweets.tar.gz"

if [ -f $FILE ];
then
    rm -rf tweets/*
    tar -zxvf $FILE >/dev/null 2>&1
    rm $FILE
fi
