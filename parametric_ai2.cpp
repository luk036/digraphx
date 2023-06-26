#include <algorithm>
#include <map>
#include <utility>
#include <vector>

template <typename V, typename R> class ParametricAPI {
public:
  virtual R Distance(R ratio, std::pair<V, V> e) = 0;
  virtual R ZeroCancel(std::vector<std::pair<V, V>> cycle) = 0;
};

template <typename V, typename R> class MaxParametricSolver {
private:
  std::map<V, std::map<V, R>> gra;
  ParametricAPI<V, R> *omega;
  NegCycleFinder<V, R> *ncf;

public:
  MaxParametricSolver(std::map<V, std::map<V, R>> gra,
                      ParametricAPI<V, R> *omega) {
    this->gra = gra;
    this->omega = omega;
    this->ncf = new NegCycleFinder<V, R>(gra);
  }
  std::pair<R, std::vector<std::pair<V, V>>> Run(std::map<V, R> dist, R ratio) {
    R r_min = ratio;
    std::vector<std::pair<V, V>> c_min;
    std::vector<std::pair<V, V>> cycle;
    while (true) {
      for (auto ci : ncf->FindNegCycle(dist, [&](std::pair<V, V> e) {
             return omega->Distance(ratio, e);
           })) {
        R ri = omega->ZeroCancel(ci);
        if (r_min > ri) {
          r_min = ri;
          c_min = ci;
        }
      }
      if (r_min >= ratio) {
        break;
      }
      cycle = c_min;
      ratio = r_min;
    }
    return std::make_pair(ratio, cycle);
  }
};
