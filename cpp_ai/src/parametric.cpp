#include "digraphx/parametric.hpp"

namespace digraphx {
    // Explicit template instantiations for common types
    template class MaxParametricSolver<int, int, int>;
    template class MaxParametricSolver<int, double, double>;
    template class MaxParametricSolver<int, float, float>;
    template class MaxParametricSolver<std::string, int, int>;
    template class MaxParametricSolver<std::string, double, double>;
    
    // Specialization for Rational type
    template class MaxParametricSolver<int, int, Rational<int64_t>>;
    template class MaxParametricSolver<std::string, int, Rational<int64_t>>;
}