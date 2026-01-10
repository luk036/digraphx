cmake_minimum_required(VERSION 3.20)
project(digraphx VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Options
option(BUILD_SHARED_LIBS "Build shared library" OFF)
option(BUILD_TESTS "Build tests" ON)
option(BUILD_EXAMPLES "Build examples" ON)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include/cppcoro)

# Library source files
set(LIB_SOURCES
    src/tiny_digraph.cpp
    src/neg_cycle.cpp
    src/neg_cycle_q.cpp
    src/parametric.cpp
    src/min_cycle_ratio.cpp
    src/min_parmetric_q.cpp
)

# Library headers
set(LIB_HEADERS
    include/digraphx/tiny_digraph.hpp
    include/digraphx/neg_cycle.hpp
    include/digraphx/neg_cycle_q.hpp
    include/digraphx/parametric.hpp
    include/digraphx/min_cycle_ratio.hpp
    include/digraphx/min_parmetric_q.hpp
    include/digraphx/types.hpp
)

# Create library
add_library(digraphx ${LIB_SOURCES} ${LIB_HEADERS})
target_include_directories(digraphx PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# C++23 features
target_compile_features(digraphx PUBLIC cxx_std_23)

# Tests
if(BUILD_TESTS)
    # Find doctest
    find_package(doctest QUIET)
    if(NOT doctest_FOUND)
        message(STATUS "doctest not found, downloading...")
        include(FetchContent)
        FetchContent_Declare(
            doctest
            GIT_REPOSITORY https://github.com/doctest/doctest.git
            GIT_TAG v2.4.11
        )
        FetchContent_MakeAvailable(doctest)
    endif()

    # Test source files
    set(TEST_SOURCES
        tests/test_tiny_digraph.cpp
        tests/test_neg_cycle.cpp
        tests/integration_tests.cpp
    )

    # Add tests
    add_executable(digraphx_tests ${TEST_SOURCES})
    target_link_libraries(digraphx_tests PRIVATE digraphx doctest::doctest)
    target_include_directories(digraphx_tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)

    # Add test command
    add_test(NAME digraphx_tests COMMAND digraphx_tests)
endif()

# Examples
if(BUILD_EXAMPLES)
    # Example source files
    set(EXAMPLE_SOURCES
        examples/basic_usage.cpp
    )

    # Add examples
    add_executable(basic_usage examples/basic_usage.cpp)
    target_link_libraries(basic_usage PRIVATE digraphx)
    target_include_directories(basic_usage PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
endif()

# Install targets
install(TARGETS digraphx
    EXPORT digraphxTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(DIRECTORY include/digraphx
    DESTINATION include
    FILES_MATCHING PATTERN "*.hpp"
)

install(EXPORT digraphxTargets
    FILE digraphxTargets.cmake
    NAMESPACE digraphx::
    DESTINATION lib/cmake/digraphx
)
