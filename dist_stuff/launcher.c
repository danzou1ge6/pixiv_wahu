#include "Python.h"


int wmain ( int argc, wchar_t* argv[] ) {
    int myargc = argc + 2;
    wchar_t** myargv = (wchar_t**) malloc( myargc * sizeof(wchar_t*) );

    myargv[0] = argv[0];
    myargv[1] = L"-m";
    myargv[2] = L"wahu_backend.__init__";

    memcpy( myargv + 3, argv + 1, ( argc - 1 ) * sizeof(wchar_t*) );

    return Py_Main(myargc, myargv);
}
