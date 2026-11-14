import unittest, importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('update_offers',Path(__file__).parents[1]/'update_offers.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class OffersTest(unittest.TestCase):
 def test_empty(self):self.assertEqual(m.check({'offers':[]},{}),[])
 def test_bad_offer(self):self.assertEqual(m.check({'offers':[{'name':'Test'}]},{}),[])
 def test_expired(self):self.assertEqual(m.check({'offers':[{'name':'Gurke','market':'netto','price':0.88,'validFrom':'2020-01-01','validTo':'2020-01-02','sourceUrl':'https://example.org/'}]},{}),[])
if __name__=='__main__':unittest.main()
