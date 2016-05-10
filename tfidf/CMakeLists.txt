cmake_minimum_required(VERSION 2.6)
project(tfidf)

add_executable(tfidf main.cpp)

install(TARGETS tfidf RUNTIME DESTINATION bin)
