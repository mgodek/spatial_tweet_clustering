#!/bin/bash

sudo pip install geojson
sudo pip install tweepy
sudo pip install rpy2

mkdir cmake_tfidf
cd cmake_tfidf
cmake ../tfidf
make
./tfidf -help
cd ..

FILE="tweets.tar.gz"

if [ -f $FILE ];
then
    rm -rf tweets/*
    tar -zxvf $FILE >/dev/null 2>&1
    rm $FILE
fi
