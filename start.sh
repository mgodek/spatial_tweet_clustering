#!/bin/bash

R --version

sudo pip install numpy

#install matplotlib dependencies
FILE="basemap-1.0.7.tar.gz"
if [ ! -f $FILE ];
then
    wget https://sourceforge.net/projects/matplotlib/files/matplotlib-toolkits/basemap-1.0.7/basemap-1.0.7.tar.gz
    tar -zxvf $FILE >/dev/null 2>&1
    cd basemap-1.0.7/geos-3.3.3
    export GEOS_DIR=`pwd`/../lib
    ./configure --prefix=$GEOS_DIR
    make -j3; make install
    cd ..
    sudo -E python setup.py install
    cd ..
fi

sudo apt-get install python-matplotlib
sudo pip install geojson
#sudo pip install geopy
sudo pip install tweepy
sudo pip install rpy2

rm -rf cmake_tfidf
mkdir cmake_tfidf
cd cmake_tfidf
cmake ../tfidf
make
cd ..

rm -rf cmake_stemmer
mkdir cmake_stemmer
cd cmake_stemmer
cmake ../libstemmer_c
make
cd ..

FILE="tweets.tar.gz"
echo "Now manually create a directory named 'tweets' in which will be *.json tweets"
#if [ -f $FILE ];
#then
#    rm -rf tweets/*
#    tar -zxvf $FILE >/dev/null 2>&1
#    rm $FILE
#fi
