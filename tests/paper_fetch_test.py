import unittest
from async_tasks.fetch_paper import fetch

class TestRegister(unittest.TestCase):
    def test_async(self):
        x = fetch.delay('https://arxiv.org/abs/1812.03170')
        print(x.get(10))
