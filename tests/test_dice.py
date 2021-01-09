import unittest
from app import app

def test_test():
    assert app.test() == "Works!"
