cmake_minimum_required(VERSION 3.2)
project(tvm-rpc)

option(TVM_PATH "")

set(USE_CPP_RPC ON)
add_subdirectory("${TVM_PATH}" "bin")