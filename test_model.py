import unittest
import numpy as np
from model import *
class Tests(unittest.TestCase):
 def test_pv(self): np.testing.assert_allclose(pv(1000,[0,20,40]),[90,82.8,75.6])
 def test_knee(self): self.assertAlmostEqual(acceleration(.75,Config(0,25,0)),1.25)
 def test_thermal(self): self.assertAlmostEqual(thermal(25,25,50,3600,Config(0,25,0)),25+.78125*(1-np.exp(-1.8)))
 def test_balance(self):
  b=Plant(Config(1e-10,25,0)); r=b.step(1,80,10,40); self.assertAlmostEqual(r['pv']+r['discharge'],r['served']+r['charge']+r['curtailment']); self.assertLess(b.h,.8)
if __name__=='__main__': unittest.main()
