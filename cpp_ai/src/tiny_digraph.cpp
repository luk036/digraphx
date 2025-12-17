#include "digraphx/tiny_digraph.hpp"

// Most implementation is in the header file due to templates
// This file exists to ensure the library compiles correctly

namespace digraphx {
    // Explicit template instantiations for common types
    template class TinyDiGraph<int, int>;
    template class TinyDiGraph<int, double>;
    template class TinyDiGraph<int, float>;
    template class TinyDiGraph<std::string, int>;
    template class TinyDiGraph<std::string, double>;
    template class TinyDiGraph<std::string, std::string>;
}