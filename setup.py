#!/usr/bin/env python3

"""
Python setuptools config to package the all the components of this repository.

Note conda load_setup_py_data() requires that this script is runnable during the build stage so we avoid non default
classes such as Pybind11Extension as these packages are unlikely to be installed in the conda base environment.
"""
import os
import sys
import subprocess
from setuptools import setup, find_namespace_packages, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from distutils.command.clean import clean
from distutils.dir_util import copy_tree
from pathlib import Path


class BuildExtensions(build_ext):
    """
    Extends the standard extension builder building the pure C++ dependencies before the python extensions, then creates
    a handy 'pylib' symlink for the PYTHONPATH.
    """
    def run(self):
        subprocess.check_call("make build=release", shell=True)

        # Overwrite any of the env variables that might be the conda environment that will prepend rpaths we don't want.
        os.environ["LDFLAGS"] = "-shared"
        os.environ["LDSHARED"] = "-shared"

        build_ext.run(self)  # call parent
        packages = Path("packages")
        packages.unlink(missing_ok=True)
        packages.symlink_to(self.get_finalized_command("build_py").build_lib)
        return


class Install(install):
    """
    Extends the standard installer to build the pure C++ dependencies and install the headers, libraries and binaries as
    well as the non-platform specific shared files.
    """
    def run(self):
        subprocess.check_call("make build=release", shell=True)
        copy_tree("include", f"{sys.prefix}/include")
        copy_tree("lib", f"{sys.prefix}/lib")
        copy_tree("bin", f"{sys.prefix}/bin")
        copy_tree("share", f"{sys.prefix}/share")
        install.run(self)  # call parent
        return


class Clean(clean):
    """
    Extends the standard clean command.
    """
    def run(self):
        clean.run(self)  # call parent, this removes the temp files only
        packages_link = Path("packages")
        packages_link.unlink(missing_ok=True)
        subprocess.check_call(f"rm -rf {self.get_finalized_command('build_py').build_lib}", shell=True)
        subprocess.check_call(f"rm -rf {self.get_finalized_command('build').build_scripts}", shell=True)
        subprocess.check_call("make build=release clean", shell=True)
        return


# C++ python extensions are compiled and packaged using setuptools, not using the Makefile.
ext_modules = [
    Extension(name="acme.skeleton.helloworld",
              sources=["src/acme/skeleton/py_helloworld.cpp"],
              include_dirs=["include"],
              extra_compile_args=["-fvisibility=hidden", "-std=c++17"],  # required for pybind11
              library_dirs=["lib"],
              extra_link_args=["-Wl,-rpath,$ORIGIN/../../../../lib"],  # conda-build will also append the env rpath
              libraries=["acme-skeleton-shared"],
              language="c++")
]


if __name__ == "__main__":
    setup(
        name="acme-skeleton",
        version="0.0.0",  # automatically updated by deploy tool
        package_dir={"acme": "acme"},
        packages=find_namespace_packages(include=["acme.*"]),
        scripts=[str(f) for f in Path("scripts").glob("**/*") if f.is_file()],
        cmdclass={"build_ext": BuildExtensions, "install": Install, "clean": Clean},
        ext_modules=ext_modules,
        include_package_data=True,
        zip_safe=False,  # implicit namespaces do not appear to import from zipped egg
    )
