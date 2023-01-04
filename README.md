# acme-skeleton

This is an example 'hello world' repository, using a fictional company name 'acme' as a placeholder for the root
namespace, and the name 'skeleton' an example the project name. I use this repository as a template for starting new
C++/python projects which are managed and deployed by conda. This public repository is not supported, it just serves as
an example project to help others because the online setuptools and conda documentation/examples are patchy and
packaging C++/python hybrid repositories can be tricky.

These examples are currently configured for Linux using g++. The conda recipe uses a Makefile to build the pure C++
components and python's setuptools to build C++ python extensions then package all the built components together. All
the C++ components and python extensions are built using conda's compiler and linked against the libraries that are in
the conda environment, rather than the system compiler/libraries to avoid any ABI incompatibilities with the host's
distribution. There are also some subtle features like setting rpath=$ORIGIN to avoid the need to set LD_LIBRARY_PATH
when doing local development.

To develop and test applications locally in this repository you first need to build the components and set the
PYTHONPATH in your local environment:

```bash
$ python setup.py build
$ export PYTHONPATH=${PWD}/packages
```

_* note these conda packages need to be already installed in the environment that you are using for development:_
```make cxx-compiler pybind11 boost pytest```

C++ and python test harnesses are automatically run by conda-build, but can be run manually:

```bash
$ make test
$ pytest
```

You can also activate some example git pre-commit hooks by running:

```bash
$ pre-commit install
```
