cmake_minimum_required(VERSION 3.20.0)

list(APPEND ZEPHYR_EXTRA_MODULES
  ${CMAKE_CURRENT_SOURCE_DIR}/drivers
)


find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})



project(project_ssns)

target_sources(app PRIVATE src/main.c)
zephyr_include_directories(drivers)
