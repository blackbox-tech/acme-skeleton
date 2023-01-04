from acme.skeleton.helloworld import greeting
from acme.skeleton.example import welcome


def test_greeting():
    assert greeting() == "Hello World!"
    return


def test_welcome():
    assert welcome() == "Welcome"
    return
