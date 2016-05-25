cmake_minimum_required(VERSION 2.6)
project(tfidf)

set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Werror -std=c++11 -fpic -O3" )

file( GLOB_RECURSE TFIDF_FILES
      stemmedfileinmemoryparser.h
      stemmedfileinmemoryparser.cpp
)

add_library(tfidf SHARED ${TFIDF_FILES})

add_executable(tfidf_make main.cpp)

TARGET_LINK_LIBRARIES(tfidf_make tfidf)
