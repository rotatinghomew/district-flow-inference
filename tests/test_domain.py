import json
import unittest
from pathlib import Path
from district_flow.partner import operate, parse_time


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(Path('data/release.json').read_text())

    def test_existing_domain_contract(self):
        result=operate('/v1/matrix-check',{'window':'late','cells':[{'origin':'north','destination':'south','count':2}]},self.data)
        self.assertIn(['north','south'],result['violations'])
        self.assertEqual(len(result['differences']),8)


if __name__=='__main__':
    unittest.main()
