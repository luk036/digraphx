#include "digraphx/neg_cycle.hpp"

namespace digraphx {
    // Explicit template instantiations for common types
    template class NegCycleFinder<int, int, int>;
    template class NegCycleFinder<int, double, double>;
    template class NegCycleFinder<int, float, float>;
    template class NegCycleFinder<std::string, int, int>;
    template class NegCycleFinder<std::string, double, double>;
    
    // Specialization for Rational type
    template class NegCycleFinder<int, int, Rational<int64_t>>;
    template class NegCycleFinder<std::string, int, Rational<int64_t>>;
}