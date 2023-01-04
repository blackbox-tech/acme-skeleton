#include <boost/test/unit_test.hpp>
#include "acme/skeleton/helloworld.hpp"

using namespace acme::skeleton;
using namespace boost::unit_test_framework;

BOOST_AUTO_TEST_SUITE(test_example)

BOOST_AUTO_TEST_CASE(test_greeting)
{
    BOOST_CHECK(greeting() == "Hello World!");
}

BOOST_AUTO_TEST_SUITE_END()
