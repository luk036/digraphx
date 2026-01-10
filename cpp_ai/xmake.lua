-- xmake.lua for digraphx C++ library
set_project("digraphx")
set_version("0.1.0")

-- Set C++ standard to C++20
set_languages("c++20")

-- Global configuration
set_warnings("all")

-- Add doctest package
add_requires("doctest")

-- Library target
target("digraphx")
    set_kind("static")
    set_default(true)

    -- Source files
    add_files("src/*.cpp")

    -- Header files
    add_headerfiles("include/digraphx/*.hpp")

    -- Include directories
    add_includedirs("include", {public = true})
    add_includedirs("include/cppcoro")

    -- Enable coroutines for C++20
    -- add_cxxflags("-fcoroutines")

-- Test target
target("tests")
    set_kind("binary")
    set_default(false)

    -- Test files
    add_files("tests/*.cpp")

    -- Dependencies
    add_deps("digraphx")

    -- Add doctest package
    add_packages("doctest")

    -- Include directories
    add_includedirs("include")
    add_includedirs("include/cppcoro")

    -- Enable coroutines
    -- add_cxxflags("-fcoroutines")

-- Example target
target("example")
    set_kind("binary")
    set_default(false)

    -- Example source
    add_files("examples/basic_usage.cpp")

    -- Dependencies
    add_deps("digraphx")

    -- Include directories
    add_includedirs("include")
    add_includedirs("include/cppcoro")

    -- Enable coroutines
    -- add_cxxflags("-fcoroutines")
