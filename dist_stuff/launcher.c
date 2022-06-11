#include "Python.h"

typedef short unsigned int wchar_t;

int main(int argc, wchar_t** argv) {
    int argc_mod = argc + 2;

    wchar_t** argv_mod = (wchar_t**) malloc(sizeof(wchar_t) * argc_mod);
    argv_mod[1] = L"-m";
    argv_mod[2] = L"wahu_backend.__init__";


    for (int i = 1; i < argc; i++) {
        argv_mod[i + 2] = argv[i];
    }

    return Py_Main(argc_mod, argv_mod);
}
