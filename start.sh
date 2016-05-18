#!/bin/bash

R --version

sudo pip install geojson
sudo pip install tweepy
sudo pip install rpy2

mkdir cmake_tfidf
cd cmake_tfidf
cmake ../tfidf
make
cd ..

mkdir cmake_stemmer
cd cmake_stemmer
cmake ../libstemmer_c
make
cd ..

FILE="tweets.tar.gz"

if [ -f $FILE ];
then
    rm -rf tweets/*
    tar -zxvf $FILE >/dev/null 2>&1
    rm $FILE
fi
