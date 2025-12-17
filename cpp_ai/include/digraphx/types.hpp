#pragma once
#ifndef DIGRAPHX_TYPES_HPP
#define DIGRAPHX_TYPES_HPP

#include <concepts>
#include <cstdint>
#include <limits>
#include <memory>
#include <type_traits>
#include <vector>
#include <unordered_map>
#include <string>

namespace digraphx {

// Forward declarations
template<typename N, typename E, typename D>
class NegCycleFinder;

template<typename N, typename E, typename R>
class NegCycleFinderQ;

template<typename N, typename E, typename R>
class MaxParametricSolver;

template<typename N, typename E, typename R>
class MinCycleRatioSolver;

template<typename N, typename E, typename R, typename API>
class MinParametricQSolver;

// Type traits and concepts
template<typename T>
concept Node = requires(T a, T b) {
    { a == b } -> std::convertible_to<bool>;
    { a != b } -> std::convertible_to<bool>;
    { std::hash<T>{}(a) } -> std::convertible_to<std::size_t>;
    requires std::copyable<T>;
};

template<typename T>
concept Edge = requires(T a) {
    requires std::copyable<T>;
    requires std::equality_comparable<T>;
};

template<typename T>
concept Domain = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
    { a - b } -> std::convertible_to<T>;
    { a * b } -> std::convertible_to<T>;
    { a / b } -> std::convertible_to<T>;
    { a > b } -> std::convertible_to<bool>;
    { a < b } -> std::convertible_to<bool>;
    { a == b } -> std::convertible_to<bool>;
    { T::zero() } -> std::convertible_to<T>;
    requires std::copyable<T>;
};

template<typename T>
concept RatioType = Domain<T> && requires(T a) {
    { a.numerator() } -> std::integral;
    { a.denominator() } -> std::integral;
};

// Alias for cycle representation
template<typename E>
using Cycle = std::vector<E>;

// Graph representation type
template<typename N, typename E>
using Digraph = std::unordered_map<N, std::unordered_map<N, E>>;

// Distance map type
template<typename N, typename D>
using DistanceMap = std::unordered_map<N, D>;

// Helper functions for numeric types
template<typename T>
struct numeric_traits {};

template<>
struct numeric_traits<int> {
    static constexpr int zero() { return 0; }
    static constexpr int max() { return std::numeric_limits<int>::max(); }
};

template<>
struct numeric_traits<double> {
    static constexpr double zero() { return 0.0; }
    static constexpr double max() { return std::numeric_limits<double>::max(); }
};

template<>
struct numeric_traits<float> {
    static constexpr float zero() { return 0.0f; }
    static constexpr float max() { return std::numeric_limits<float>::max(); }
};

// Rational number type for ratio calculations
template<typename IntType = int64_t>
class Rational {
private:
    IntType num_;
    IntType den_;
    
    void normalize() {
        if (den_ < 0) {
            num_ = -num_;
            den_ = -den_;
        }
        IntType g = gcd(std::abs(num_), den_);
        num_ /= g;
        den_ /= g;
    }
    
    static IntType gcd(IntType a, IntType b) {
        while (b != 0) {
            IntType t = b;
            b = a % b;
            a = t;
        }
        return a;
    }
    
public:
    Rational() : num_(0), den_(1) {}
    Rational(IntType n) : num_(n), den_(1) {}
    Rational(IntType n, IntType d) : num_(n), den_(d) {
        if (den_ == 0) {
            throw std::invalid_argument("Denominator cannot be zero");
        }
        normalize();
    }
    
    IntType numerator() const { return num_; }
    IntType denominator() const { return den_; }
    
    double to_double() const {
        return static_cast<double>(num_) / static_cast<double>(den_);
    }
    
    // Arithmetic operators
    Rational operator+(const Rational& other) const {
        return Rational(num_ * other.den_ + other.num_ * den_, den_ * other.den_);
    }
    
    Rational operator-(const Rational& other) const {
        return Rational(num_ * other.den_ - other.num_ * den_, den_ * other.den_);
    }
    
    Rational operator*(const Rational& other) const {
        return Rational(num_ * other.num_, den_ * other.den_);
    }
    
    Rational operator/(const Rational& other) const {
        return Rational(num_ * other.den_, den_ * other.num_);
    }
    
    // Comparison operators
    bool operator==(const Rational& other) const {
        return num_ == other.num_ && den_ == other.den_;
    }
    
    bool operator!=(const Rational& other) const {
        return !(*this == other);
    }
    
    bool operator<(const Rational& other) const {
        return num_ * other.den_ < other.num_ * den_;
    }
    
    bool operator>(const Rational& other) const {
        return num_ * other.den_ > other.num_ * den_;
    }
    
    bool operator<=(const Rational& other) const {
        return num_ * other.den_ <= other.num_ * den_;
    }
    
    bool operator>=(const Rational& other) const {
        return num_ * other.den_ >= other.num_ * den_;
    }
    
    // Unary operators
    Rational operator-() const {
        return Rational(-num_, den_);
    }
    
    // Static methods
    static Rational zero() { return Rational(0, 1); }
    static Rational one() { return Rational(1, 1); }
};

} // namespace digraphx

#endif // DIGRAPHX_TYPES_HPP