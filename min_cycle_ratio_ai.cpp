#include <unordered_map>
#include <vector>
#include <algorithm>
#include <type_traits>
#include <string>

template<typename V, typename R>
class CycleRatioAPI {
private:
    std::unordered_map<V, std::unordered_map<V, std::unordered_map<std::string, R>>> gra;
    std::type_info const& T;
public:
    CycleRatioAPI(std::unordered_map<V, std::unordered_map<V, std::unordered_map<std::string, R>>> gra, std::type_info const& T) : gra(gra), T(T) {}
    R Distance(R ratio, std::pair<V, V> e) {
        auto [u, v] = e;
        return gra[u][v]["cost"] - ratio * gra[u][v]["time"];
    }
    R ZeroCancel(std::vector<std::pair<V, V>> cycle) {
        R totalCost = 0, totalTime = 0;
        for (auto e : cycle) {
            totalCost += gra[e.first][e.second]["cost"];
            totalTime += gra[e.first][e.second]["time"];
        }
        return static_cast<R>(static_cast<typename std::underlying_type<R>::type>(totalCost) / totalTime);
    }
};

template<typename V, typename R>
class MaxParametricSolver {
private:
    std::unordered_map<V, std::unordered_map<V, std::unordered_map<std::string, R>>> gra;
    CycleRatioAPI<V, R> omega;
public:
    MaxParametricSolver(std::unordered_map<V, std::unordered_map<V, std::unordered_map<std::string, R>>> gra, CycleRatioAPI<V, R> omega) : gra(gra), omega(omega) {}
    std::pair<R, std::vector<std::pair<V, V>>> Run(std::unordered_map<V, R> dist, R r0) {
        std::vector<std::pair<V, V>> cycle;
        R ratio = r0;
        for (int i = 0; i < 100; i++) {
            std::unordered_map<V, std::unordered_map<V, R>> g;
            for (auto [u, adj] : gra) {
                for (auto [v, e] : adj) {
                    g[u][v] = omega.Distance(ratio, {u, v});
                }
            }
            auto [d, p] = dist;
            auto [d2, p2] = dist;
            for (int i = 0; i < gra.size(); i++) {
                for (auto [u, adj] : gra) {
                    for (auto [v, e] : adj) {
                        if (d2[v] > d[u] + g[u][v]) {
                            d2[v] = d[u] + g[u][v];
                            p2[v] = u;
                        }
                    }
                }
                std::swap(d, d2);
                std::swap(p, p2);
            }
            V x = V();
            for (auto [u, adj] : gra) {
                for (auto [v, e] : adj) {
                    if (d[u] + g[u][v] < d[v]) {
                        x = u;
                        break;
                    }
                }
                if (x != V()) break;
            }
            if (x == V()) break;
            std::vector<V> path;
            std::unordered_map<V, int> vis;
            while (!vis.count(x)) {
                vis[x] = path.size();
                path.push_back(x);
                x = p[x];
            }
            cycle.clear();
            for (int i = vis[x]; i < path.size(); i++) {
                cycle.push_back({path[i], p[path[i]]});
            }
            R r = omega.ZeroCancel(cycle);
            if (r > ratio) {
                ratio = r;
            } else {
                break;
            }
        }
        return {ratio, cycle};
    }
};

template<typename V, typename R>
class MinCycleRatioSolver {
private:
    std::unordered_map<V, std::unordered_map<V, std::unordered_map<std::string, R>>> gra;
public:
    MinCycleRatioSolver(std::unordered_map<V, std::unordered_map<V, std::unordered_map<std::string, R>>> gra) : gra(gra) {}
    std::pair<R, std::vector<std::pair<V, V>>> Run(std::unordered_map<V, R> dist, R r0) {
        CycleRatioAPI<V, R> omega(gra, typeid(r0));
        MaxParametricSolver<V, R> solver(gra, omega);
        auto [ratio, cycle] = solver.Run(dist, r0);
        return {ratio, cycle};
    }
};

