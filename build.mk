################################################################################
# This example file is included by main Makefile and contains the rules to build
# all the pure C++ components (non-python extensions) in this repository.
#

# example static library
$(eval $(call STATIC_LIBRARY,acme-skeleton-static,acme/skeleton/helloworld.cpp))

# example shared library
$(eval $(call SHARED_LIBRARY,acme-skeleton-shared,acme/skeleton/helloworld.cpp))

# example executable, here we link to our static library
$(eval $(call EXECUTABLE,example_exec,acme/skeleton/example.cpp))
${bin_dir}/example_exec: ${lib_dir}/libacme-skeleton-shared.so   # depends on building the static library
${bin_dir}/example_exec: LIBS += acme-skeleton-shared  # link this executable to this static library

# example of boost unit-test, this time we link dynamically to our shared library
$(eval $(call TEST_HARNESS,test_example,acme/skeleton/test_example.cpp))
${obj_dir}/acme/skeleton/test_example.o: CPPFLAGS += -DBOOST_AUTO_TEST_MAIN  # define a macro in this object file only
${test_dir}/test_example: ${lib_dir}/libacme-skeleton-static.a  # depends on building the shared library
${test_dir}/test_example: LIBS += acme-skeleton-shared boost_unit_test_framework boost_test_exec_monitor  # link this test to this shared libraries
