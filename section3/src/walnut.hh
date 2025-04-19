#ifndef WALNUT_HH
#define WALNUT_HH

#include <map>
#include <numeric>
#include <unordered_map>
#include <vector>
#include <string>
#include <sstream>
#include <fstream>
#include <set>
#include <functional>
#include <stdexcept>
#include <iostream>

#include <awali/sttc/automaton.hh>
#include <awali/sttc/weightset/q.hh>
#include <awali/sttc/weightset/b.hh>
#include <awali/sttc/ctx/lal_int.hh>
#include <awali/sttc/algos/copy.hh>
#include <awali/sttc/algos/product.hh>
#include "reduce.hh"
#include "gmpq.hh"

using namespace awali;
using namespace awali::sttc;

using labelset_t = ctx::lal_int;
using weightset_t = gmpq;
using value_t = gmpq::value_t;
using context_t = context<labelset_t, weightset_t>;

namespace dfa {


struct VectorHash {
    std::size_t operator()(const std::vector<int>& v) const {
        std::size_t hash = 0;
        for (int i : v) {
            hash ^= std::hash<int> {}(i) + 0x9e3779b9 + (hash << 6) + (hash >> 2);
        }
        return hash;
    }
};

struct LabelMapper {
public:
    std::unordered_map<std::vector<int>, int, VectorHash> to_int;
    std::vector<std::vector<int>> to_tuple;

    int get(const std::vector<int>& tuple) {
        auto it = to_int.find(tuple);
        if (it != to_int.end())
            return it->second;

        int id = static_cast<int>(to_tuple.size());
        to_tuple.push_back(tuple);
        to_int[tuple] = id;
        return id;
    }

    const std::vector<int>& operator[](int id) const {
        return to_tuple[id];
    }

    int size() const {
        return static_cast<int>(to_tuple.size());
    }

    std::set<int> labels_set() const {
        std::set<int> res;
        for (int i = 0; i < size(); ++i)
            res.insert(i);
        return res;
    }

    std::vector<int> labels() const {
        std::vector<int> res(size());
        std::iota(res.begin(), res.end(), 0);
        std::sort(res.begin(), res.end(), [&](int a, int b) {
            return to_tuple[a] < to_tuple[b];
        });
        return res;
    }
};

inline void dfa_from_walnut(
    const std::string& filename,
    std::vector<std::map<std::vector<int>, int>>& trans,
    std::vector<int>& out,
    LabelMapper& label_mapper
) {
    std::ifstream in(filename);
    if (!in)
        throw std::runtime_error("Cannot open file: " + filename);

    std::string line;
    std::getline(in, line);

    int current_state = -1;
    std::map<std::vector<int>, int> current_trans;

    while (std::getline(in, line)) {
        std::stringstream ss(line);
        std::string s = line;
        if (s.empty()) continue;

        auto pos = s.find("->");
        if (pos == std::string::npos) {
            if (current_state != -1)
                trans[current_state] = current_trans;
            current_trans.clear();

            std::stringstream st_line(s);
            int q, o;
            st_line >> q >> o;
            current_state = q;
            if (q >= (int)out.size())
                out.resize(q + 1);
            out[q] = o;
            if (q >= (int)trans.size())
                trans.resize(q + 1);
        } else {
            std::string left = s.substr(0, pos);
            std::string right = s.substr(pos + 2);
            std::stringstream left_ss(left);
            std::vector<int> label;
            int val;
            while (left_ss >> val)
                label.push_back(val);
            int target = std::stoi(right);
            current_trans[label] = target;
            label_mapper.get(label);
        }
    }

    if (current_state != -1)
        trans[current_state] = current_trans;
}

inline std::pair<mutable_automaton<context_t>, LabelMapper>
dfa_count(
    const std::vector<std::map<std::vector<int>, int>>& trans,
    const std::vector<int>& out,
    LabelMapper &label_mapper,
    const std::vector<int>& vars,
std::function<std::vector<int>(const std::vector<int>&)> remap = [](const std::vector<int>& x) {
    return x;
}
) {

    LabelMapper proj_map;

    for (const auto& [tuple, label] : label_mapper.to_int) {
        std::vector<int> projected;
        for (int i : vars)
            projected.push_back(tuple[i]);
        proj_map.get(remap(projected));
    }

    labelset_t alphabet = labelset_t(proj_map.labels_set());
    weightset_t weights;
    context_t ctx(alphabet, weights);
    auto A = make_mutable_automaton(ctx);

    std::vector<state_t> states(out.size());
    for (size_t i = 0; i < out.size(); ++i)
        states[i] = A->add_state();

    for (size_t i = 0; i < out.size(); ++i)
        if (out[i] > 0)
            A->set_final(states[i],value_t(out[i]));

    for (size_t q = 0; q < trans.size(); ++q) {
        for (const auto& [t, qq] : trans[q]) {
            std::vector<int> proj;
            for (int i : vars)
                proj.push_back(t[i]);
            int label = proj_map.get(remap(proj));
            A->add_transition(states[q], states[qq], label, value_t(1));
        }
    }

    int ze = proj_map.get(std::vector<int>(vars.size(), 0));

    std::map<state_t, int> cur, nxt;
    nxt[states[0]] = 1;

    while (cur != nxt) {
        cur = nxt;
        nxt.clear();
        for (const auto& [q, w] : cur) {
            for (const auto& tr : A->all_out(q))
                if (A->label_of(tr) == ze)
                    nxt[A->dst_of(tr)] += w * A->weight_of(tr).get_num().get_si();
        }
    }

    for (const auto& [q, w] : cur)
        A->set_initial(q, value_t(w));

    return { A, proj_map };
}

mutable_automaton<context_t> remap_labels(
    const mutable_automaton<context_t>& A,
    dfa::LabelMapper& al,
    const std::function<std::vector<int>(const std::vector<int>&)>& reorder
) {
    using namespace awali::sttc;

    using label_t = int;
    using weight_t = weightset_t;

    auto B = make_mutable_automaton(A->context());
    std::map<state_t, state_t> state_map;

    for (state_t qA : A->states())
        state_map[qA] = B->add_state();

    for (auto itA : A->initial_transitions())
        B->set_initial(state_map[A->dst_of(itA)], A->weight_of(itA));

    for (state_t ftA : A->final_transitions())
        B->set_final(state_map[A->src_of(ftA)], A->weight_of(ftA));

    for (const auto& tr : A->transitions()) {
        std::vector<int> tuple = al[A->label_of(tr)];
        std::vector<int> reordered = reorder(tuple);
        int new_label = al.get(reordered);
        B->add_transition(state_map[A->src_of(tr)], state_map[A->dst_of(tr)], new_label, A->weight_of(tr));
    }

    return B;
}

void opposite_here(mutable_automaton<context_t>& A) {
    for (auto itA : A->initial_transitions()) {
        auto w = A->weight_of(itA);
        w = mpq_class(-w.get_num(), w.get_den());
        A->set_initial(A->dst_of(itA), w);
    }
}

inline std::string pretty(const std::vector<int>& v) {
    std::ostringstream oss;
    for (size_t i = 0; i < v.size(); ++i) {
        if (i > 0) oss << " ";
        oss << v[i];
    }
    return oss.str();
}

template<typename T>
void to_walnut(
    const mutable_automaton<T>& A,
    const dfa::LabelMapper& al,
    std::ostream& out,
    const std::string& ns
) {
    std::vector<int> ordered;
    state_t q0 = A->dst_of(*A->initial_transitions().begin());

    ordered.push_back(q0);
    for (auto q : A->states())
        if (q != q0)
            ordered.push_back(q);

    int n = ordered.size();
    int k = al[0].size();

    for (int i = 0; i < k; ++i)
        out << ns << (i + 1 == k ? "\n" : " ");

    std::vector<int> labels = al.labels();

    for (int s = 0; s < n; ++s) {
        state_t q = ordered[s];
        out << "\n" << s << " " << A->get_final_weight(q) << "\n";

        for (const auto& a : labels)
            for (const auto& tr : A->out(q, a)) {
                int ss = std::find(ordered.begin(), ordered.end(), A->dst_of(tr)) - ordered.begin();
                out << pretty(al[A->label_of(tr)]) << " -> " << ss << "\n";
            }
    }
}

template<typename Automaton>
void summary(const Automaton& A) {
    std::cout << A.num_states() << " states, "
              << A.num_transitions() << " transitions" << std::endl;
}

}  // namespace dfa


template<typename Aut>
void show_matrix(const Aut& A, const dfa::LabelMapper& al, std::ostream& out, bool check_int = false)
{
    using automaton_t = Aut;
    using context_t = context_t_of<automaton_t>;
    using weightset_t = typename context_t::weightset_t;
    using label_t = label_t_of<automaton_t>;
    using weight_t = typename context_t::weight_t;
    using vector_t = std::vector<weight_t>;
    using matrix_t = std::vector<std::map<std::size_t, weight_t> > ;
    using matrix_set_t = std::map<label_t, matrix_t>;

    vector_t init;
    vector_t final;
    matrix_set_t letter_matrix_set;

    weight_t damin = weightset_t::zero();
    weight_t damax = weightset_t::zero();

    std::unordered_map<state_t, unsigned> state_to_index;
    unsigned i = 0;
    for (auto s: A->states())
        state_to_index[s] = i++;
    unsigned dimension = i;
    if (dimension == 0)
        return;
    init.resize(i);
    final.resize(i);
    for (auto t : A->initial_transitions())
        init[state_to_index[A->dst_of(t)]] = A->weight_of(t);
    for (auto t : A->final_transitions())
        final[state_to_index[A->src_of(t)]] = A->weight_of(t);
    for (auto t : A->transitions())
    {
        auto it = letter_matrix_set.find(A->label_of(t));
        if (it == letter_matrix_set.end())
            it = letter_matrix_set.emplace(A->label_of(t), matrix_t(dimension)).first;
        it->second[state_to_index[A->src_of(t)]]
        [state_to_index[A->dst_of(t)]] = A->weight_of(t);
    }
    weight_t v;
    out << "lambda = [";
    bool first=true;
    for (i=0; i<dimension; ++i) {
        v = init[i];
        if (v < damin) damin = v;
        if (v > damax) damax = v;
        if constexpr (std::is_same_v<weightset_t, gmpq>) {
            if (check_int) assert(v.get_den() == 1);
        }
        out << (first?"":", ") << v;
        first = false;
    }
    out << "]" << std::endl;

    out << std::endl;
    for (const auto& [label, matrix] : letter_matrix_set) {
        out << "mu[";
       first=true;
       for (const auto &v : al[label]) {
          out << (first?"":", ") << v;
         first = false;
       } 
       out << "] = [" << std::endl;
       for(i=0; i<dimension; i++) {
           out << "[";
           first = true;
           for(unsigned j=0; j<dimension; j++) {
                v = weightset_t::zero();
                auto search = letter_matrix_set[label][i].find(j);
                if (search != letter_matrix_set[label][i].end())
                    v = search->second;
                if (v < damin) damin = v;
                if (v > damax) damax = v;
                if constexpr (std::is_same_v<weightset_t, gmpq>) {
                    if (check_int) assert(v.get_den() == 1);
                }
                out << (first?"":", ") << v;
                first=false;
           }
           out << "]" << ((i<dimension-1)?",":"") << std::endl;
       }
       out << "]" << std::endl << std::endl;
    }

    out << "rho = [";
    first=true;
    for (i=0; i<dimension; ++i) {
        v = final[i];
        if (v < damin) damin = v;
        if (v > damax) damax = v;
        if constexpr (std::is_same_v<weightset_t, gmpq>) {
            if (check_int) assert(v.get_den() == 1);
        }
        out << (first?"":", ") << v;
        first = false;
    }
    out << "]" << std::endl;

    std::cout << "min: " << damin << std::endl;
    std::cout << "max: " << damax << std::endl;
}

template<typename Automaton>
Automaton prefix_absorb(const Automaton& input, const std::vector<label_t_of<Automaton>>& u) {
    using automaton_t = Automaton;
    using context_t = context_t_of<automaton_t>;
    using weightset_t = typename context_t::weightset_t;
    using weight_t = typename context_t::weight_t;
    using label_t = label_t_of<automaton_t>;
    using state_t = typename automaton_t::element_type::state_t;

    using namespace std;
    using namespace awali::sttc;

    auto A = copy(input, false, false, false);

    map<state_t, weight_t> cur, nxt;

    for (auto t : A->initial_transitions()) {
        cur[A->dst_of(t)] += A->weight_of(t);
    }

    for (label_t a : u) {
        nxt.clear();
        for (const auto& [q, w] : cur) {
            for (auto tr : A->all_out(q)) {
                if (A->label_of(tr) == a) {
                    state_t dst = A->dst_of(tr);
                    weight_t wt = A->weight_of(tr);
                    nxt[dst] += w * wt;
                }
            }
        }
        cur = nxt;
    }

    for (auto q : A->states()) {
        A->set_initial(q, weightset_t::zero());
    }

    for (const auto& [q, w] : cur) {
        A->set_initial(q, w);
    }

    return A;
}

template<typename Automaton>
void modify_transitions(Automaton& s, label_t_of<Automaton> z) {
    using state_t = typename Automaton::element_type::state_t;
    using weight_t = typename Automaton::element_type::weight_t;

    for (auto q : s->states()) {
        std::vector<std::pair<state_t, weight_t>> qtrans;
        std::set<label_t_of<Automaton>> qlab;

        for (auto tr : s->all_out(q)) {
            if (s->label_of(tr) == z) {
                state_t dst = s->dst_of(tr);
                weight_t wt = s->weight_of(tr);
                qtrans.push_back({dst, wt});
            }
            else {
                s->set_weight_of(tr, weight_t::zero());
                qlab.insert(s->label_of(tr));
            }
        }

        qlab.insert(z);

        for (auto a : qlab) {
            for (auto [q_prime, w] : qtrans) {
                s->add_transition(q, q_prime, a, w);
            }
        }
    }
}

template<typename Automaton>
Automaton gview(Automaton& s, label_t_of<Automaton> z) {
    Automaton s2 = s.copy();
    modify_transitions(s2, z);
    opposite_here(s2);
    auto s1 = s;
    auto s2_reduced = reduce(s2);
    auto result = sum(s1, s2_reduced);
    return result;
}

template<typename Automaton, typename label_t>
Automaton fromthere(Automaton& s, label_t_of<Automaton> zero, 
                 std::vector<label_t> u, Automaton& sup, int n) {
    auto su = prefix_absorb(s, u);
    auto cur = gview(su, zero);
    
    if (sup == nullptr) {
        return reduce(cur);
    }
    
    auto curs = prefix_absorb(*sup, u);
    auto res = join_automata(&cur, &curs);
    res.product();
    return reduce(res);
}

#endif // WALNUT_HH

