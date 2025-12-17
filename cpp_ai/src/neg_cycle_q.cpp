#include "digraphx/neg_cycle_q.hpp"

namespace digraphx {
    // Explicit template instantiations for common types
    template class NegCycleFinderQ<int, int, int>;
    template class NegCycleFinderQ<int, double, double>;
    template class NegCycleFinderQ<int, float, float>;
    template class NegCycleFinderQ<std::string, int, int>;
    template class NegCycleFinderQ<std::string, double, double>;
    
    // Specialization for Rational type
    template class NegCycleFinderQ<int, int, Rational<int64_t>>;
    template class NegCycleFinderQ<std::string, int, Rational<int64_t>>;
}