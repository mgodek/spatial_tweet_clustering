cmake_minimum_required(VERSION 2.6)
project(tfidf)

set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11" )

file( GLOB_RECURSE TFIDF_FILES
      *h
      *cpp
)

add_executable(tfidf ${TFIDF_FILES})

install(TARGETS tfidf RUNTIME DESTINATION bin)
