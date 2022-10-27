import unittest
import os  
import selenium.common.exceptions as exceptions

class MyTestCase(unittest.TestCase):
  
#   def test_1(self):
#      os.system('python -u CharmmGuiAuto.py -i tests/test1.yaml')
#  
#   def test_2(self):
#      os.system('python -u CharmmGuiAuto.py -i tests/test2.yaml')
#
#   def test_3(self):
#      os.system('python -u CharmmGuiAuto.py -i tests/test3.yaml')
#
#   def test_4(self):
#      os.system('python -u CharmmGuiAuto.py -i tests/test4.yaml')
    def test_fail(self):
        os.system('python -u CharmmGuiAuto.py -i fail.yaml')
if __name__ == '__main__': 
    unittest.main()
