#!/usr/bin/env python3

"""
Python setuptools config to package the all the components of this repository.

Note conda load_setup_py_data() requires that this script is runnable during the build stage, so we avoid non default
classes such as Pybind11Extension as these packages are unlikely to be installed in the conda base environment.
"""

import os
import sys
import subprocess
from pathlib import Path
from shutil import copytree

from setuptools import setup, find_namespace_packages, Extension, Command
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install


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
        copytree("include", f"{sys.prefix}/include", dirs_exist_ok=True)
        copytree("lib", f"{sys.prefix}/lib", dirs_exist_ok=True)
        copytree("bin", f"{sys.prefix}/bin", dirs_exist_ok=True)
        copytree("share", f"{sys.prefix}/share", dirs_exist_ok=True)
        install.run(self)  # call parent
        return


class Clean(Command):
    """
    Implement the clean command (unlike the deprecated distutils there is no setuptools.command.clean command to extend)
    """
    def initialize_options(self) -> None:
        return

    def finalize_options(self) -> None:
        return

    def run(self):
        packages_link = Path("packages")
        packages_link.unlink(missing_ok=True)
        shutil.rmtree(self.get_finalized_command("build_py").build_lib)
        shutil.rmtree(self.get_finalized_command("build").build_scripts)
        shutil.rmtree(self.get_finalized_command("build").build_temp)
        subprocess.check_call("make build=release clean", shell=True)
        return


# C++ python extensions are compiled and packaged using setuptools, not using the Makefile.
COMMON_EXT_ARGS = {
    "include_dirs": ["include", f"{sys.prefix}/include"],
    "library_dirs": ["lib", f"{sys.prefix}/lib"],
    "extra_compile_args": ["-fvisibility=hidden", "-std=c++2b"],  # required for pybind11
    "extra_link_args": ["-Wl,-rpath,$ORIGIN/../../../../lib"],  # conda-build will also append the env rpath
    "language": "c++",
}

# C++ python extensions are compiled and packaged using setuptools, not using the Makefile.
ext_modules = [
    Extension(name="acme.skeleton.pyhelloworld",
              sources=["src/acme/skeleton/pyhelloworld.cpp"],
              libraries=["acme-skeleton-shared"], **COMMON_EXT_ARGS),
]


if __name__ == "__main__":
    setup(
        name="acme-skeleton",
        version="0.0.0",  # automatically updated by deploy tool
        packages=find_namespace_packages(where="python"),
        package_dir={"": "python"},
        include_package_data=True,
        scripts=[str(f) for f in Path("scripts").glob("**/*") if f.is_file()],
        ext_modules=ext_modules,
        zip_safe=False,
        cmdclass={"build_ext": BuildExtensions, "install": Install, "clean": Clean},
    )
