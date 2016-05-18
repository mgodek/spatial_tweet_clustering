cmake_minimum_required(VERSION 2.6)
project(snowballStemmer)

set( CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Werror -fpic -O3" )

# choose which version You want
include( mkinc.cmake )
#include( mkinc_utf8.cmake )

include_directories( 
  src_c
  include
  libstemmer
  runtime
  examples
)

file( GLOB_RECURSE STEMMER_FILES
      examples/stemwords.c
)

add_library(stemmer SHARED ${STEMMER_FILES} ${snowball_sources})
