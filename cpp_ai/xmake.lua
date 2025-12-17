-- xmake.lua for digraphx C++ library
set_project("digraphx")
set_version("0.1.0")

-- Set C++ standard
set_languages("c++23")

-- Add cppcoro include path
add_includedirs("include/cppcoro")

-- Library target
target("digraphx")
    set_kind("static")
    set_default(true)
    
    -- Source files
    add_files("src/*.cpp")
    
    -- Header files
    add_headerfiles("include/digraphx/*.hpp")
    
    -- Public include directory
    add_includedirs("include", {public = true})
    
    -- C++23 features
    set_policy("build.c++.modules", true)

-- Tests with doctest
target("digraphx_tests")
    set_kind("binary")
    set_default(false)
    
    -- Test source files
    add_files("tests/*.cpp")
    
    -- Dependencies
    add_deps("digraphx")
    
    -- Add doctest
    add_requires("doctest")
    add_packages("doctest")
    
    -- Run tests after build
    after_build(function (target)
        os.exec(target:targetfile())
    end)

-- Examples
target("basic_usage")
    set_kind("binary")
    set_default(false)
    
    -- Example source
    add_files("examples/basic_usage.cpp")
    
    -- Dependencies
    add_deps("digraphx")

-- Package configuration
package("digraphx")
    set_description("C++23 directed graph optimization library")
    set_homepage("https://github.com/luk036/digraphx")
    set_license("MIT")
    
    on_install(function (package)
        import("package.tools.cmake").install(package)
    end)
    
    on_test(function (package)
        os.exec("digraphx_tests")
    end)