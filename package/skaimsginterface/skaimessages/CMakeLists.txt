# Minimum CMake required
cmake_minimum_required(VERSION 2.8.12)

# Project
project(skaimessages)

# Find required protobuf package
find_package(Protobuf REQUIRED)


include_directories(generated_cpp)


add_executable(${PROJECT_NAME} SkaiMessages.cpp)
target_link_libraries(${PROJECT_NAME} PUBLIC ${Protobuf_LIBRARIES})
target_include_directories(${PROJECT_NAME} PUBLIC generated_cpp ${Protobuf_INCLUDE_DIRS})
