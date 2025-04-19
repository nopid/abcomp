#ifndef AWALI_WEIGHTSET_GMPQ_HH
#define AWALI_WEIGHTSET_GMPQ_HH

#include <gmpxx.h>
#include <iostream>
#include <string>
#include <stdexcept>
#include <cmath>
#include <awali/sttc/weightset/z.hh>


namespace awali {
namespace sttc {

class gmpq {
public:
    using value_t = mpq_class;
    using self_type = gmpq;

    static std::string sname() {
        return "gmpq";
    }

    std::string vname(bool = true) const {
        return sname();
    }

    static value_t zero() {
        return value_t(0);
    }

    static value_t one() {
        return value_t(1);
    }

    static value_t add(const value_t& l, const value_t& r) {
        return l + r;
    }

    static value_t sub(const value_t& l, const value_t& r) {
        return l - r;
    }

    static value_t mul(const value_t& l, const value_t& r) {
        return l * r;
    }

    static value_t rdiv(const value_t& l, const value_t& r) {
        if (r == 0) throw std::domain_error("gmpq: division by zero");
        return l / r;
    }

    static value_t ldiv(const value_t& l, const value_t& r) {
        return rdiv(r, l);
    }

    value_t star(const value_t& v) const {
        if (abs(v) < 1)
            return one() / (one() - v);
        throw std::domain_error("gmpq: star invalid value (|v| ≥ 1)");
    }

    value_t plus(const value_t& v) const {
        if (abs(v) < 1)
            return v / (one() - v);
        throw std::domain_error("gmpq: plus invalid value (|v| ≥ 1)");
    }

    static bool is_zero(const value_t& v) {
        return v == 0;
    }

    static bool is_one(const value_t& v) {
        return v == 1;
    }

    static bool equals(const value_t& l, const value_t& r) {
        return l == r;
    }

    static bool less_than(const value_t& l, const value_t& r) {
        return l < r;
    }

    static value_t abs(const value_t& v) {
        return (v < 0) ? -v : v;
    }

    static value_t transpose(const value_t& v) {
        return v;
    }

    static value_t
    conv(self_type, value_t v)
    {
        return v;
    }

    static value_t
    conv(z, z::value_t v)
    {
        return {v, 1};
    }

    static value_t
    conv(n, n::value_t v)
    {
        return {(int)v, 1};
    }

    static value_t
    conv(b, b::value_t v)
    {
        return {v, 1};
    }

    static value_t conv(std::istream& is) {
        mpq_class v;
        is >> v;
        if (!is) throw std::runtime_error("gmpq: invalid rational input");
        return v;
    }

    static std::ostream& print(const value_t& v, std::ostream& o,
                               const std::string& format = "text") {
        if (format == "json") {
            if (v.get_den() == 1)
                o << v.get_num();
            else
                o << "{\"num\":" << v.get_num() << ",\"den\":" << v.get_den() << "}";
        } else if (format == "latex") {
            if (v.get_den() == 1)
                o << v.get_num();
            else
                o << "\\frac{" << v.get_num() << "}{" << v.get_den() << "}";
        } else {
            o << v;
        }
        return o;
    }

    std::ostream& print_set(std::ostream& o, const std::string& format = "text") const {
        if (format == "latex")
            o << "\\mathbb{Q}";
        else if (format == "text")
            o << "Q";
        else
            throw std::runtime_error("gmpq: invalid format: " + format);
        return o;
    }

    static value_t conv(int v) {
        return value_t(v);
    }

    static value_t conv(bool v) {
        return value_t(v ? 1 : 0);
    }

    static value_t conv(const value_t& v) {
        return v;
    }
};

inline gmpq join(const gmpq&, const gmpq&) {
    return {};
}


} // namespace sttc
} // namespace awali

#endif // AWALI_WEIGHTSET_GMPQ_HH

