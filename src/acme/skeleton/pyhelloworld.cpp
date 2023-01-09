#include <pybind11/pybind11.h>
#include "acme/skeleton/helloworld.hpp"

namespace py = pybind11;

PYBIND11_MODULE(pyhelloworld, module) {
    module.def("greeting", &acme::skeleton::greeting);
}
