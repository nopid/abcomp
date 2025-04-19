#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
#include <chrono>

#include "gmpq.hh"
#include "reduce.hh"
#include <awali/sttc/algos/sum.hh>
#include <awali/sttc/algos/determinize.hh>
#include <awali/sttc/algos/complete.hh>
#include "walnut.hh"


using namespace std;
using namespace awali::sttc;
using namespace dfa;

using weightset_t = gmpq;
using labelset_t = ctx::lal_int;
using context_t = context<labelset_t, weightset_t>;
using automaton_t = mutable_automaton<context_t>;

auto now() {
    return chrono::steady_clock::now();
}

void log_duration(const std::string& label, std::chrono::steady_clock::time_point start) {
    using namespace std;
    auto end = chrono::steady_clock::now();
    auto duration_ms = chrono::duration_cast<chrono::milliseconds>(end - start).count();

    long long total_seconds = duration_ms / 1000;
    int ms = duration_ms % 1000;

    cout << label << " ";

    if (total_seconds < 60) {
        // Format : 4.321s
        cout << fixed << setprecision(3) << (duration_ms / 1000.0) << "s";
    } else {
        int hours = static_cast<int>(total_seconds / 3600);
        int minutes = static_cast<int>((total_seconds % 3600) / 60);
        int seconds = static_cast<int>(total_seconds % 60);

        if (hours > 0)
            cout << hours << ":" << setfill('0') << setw(2);
        cout << minutes << ":" << setfill('0') << setw(2) << seconds;
    }

    cout << endl << endl;
}

int main(int argc, char** argv) {
    if (argc != 3) {
        cerr << "Usage: " << argv[0] << " first.txt output.txt\n"
             << "  where first.txt is is the input computing abeqfirst(i,k,n)\n"
             << "  and output.txt is the output file for the matrix representation\n";
        return 1;
    }

    string first = argv[1];
    string dest = argv[2];

    vector<map<vector<int>,int>> trans_raw;
    vector<int> out_raw;
    LabelMapper labelmap;

    cout << "* Chargement de " << first << endl;
    auto t0 = now();
    dfa_from_walnut(first, trans_raw, out_raw, labelmap);
    cout << "labelmap size: " << labelmap.size() << endl;
    log_duration(">>>", t0);

    automaton_t s;
    LabelMapper proj_map;

    cout << "Comptage de s" << endl;
    t0 = now();
    vector<int> vars = {1,2};
    tie(s, proj_map) = dfa_count(trans_raw, out_raw, labelmap, vars);
    summary(*s);
    cout << "proj_map size: " << proj_map.size() << endl;
    log_duration(">>>", t0);

    cout << "Réduction de s1" << endl;
    t0 = now();
    auto s1 = reduce(s);
    summary(*s1);
    log_duration(">>>", t0);

    ofstream fout(dest);
    show_matrix(s1, proj_map, fout, true);
    return 0;
}

