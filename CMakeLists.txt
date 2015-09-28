cmake_minimum_required (VERSION 2.8.8)

project (ann_predictor C CXX)

FIND_PACKAGE ( Threads REQUIRED )

include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)

if(COMPILER_SUPPORTS_CXX11)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
elseif(COMPILER_SUPPORTS_CXX0X)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
else()
        message(STATUS "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
endif()

add_subdirectory (sqlite3)
include_directories(sqlite3)

add_executable (ann_predictor sqlite3
  connection.h
  exchange.cpp
  exchange.h
  main.cpp
  net.cpp
  net.h
  neuron.cpp
  neuron.h
  training.cpp
  training.h)

file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/data)

TARGET_LINK_LIBRARIES ( ann_predictor sqlite3 dl ${CMAKE_THREAD_LIBS_INIT} )
