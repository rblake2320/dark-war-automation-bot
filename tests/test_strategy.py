import unittest
from darkwar_strategy import choose

class TestStrategy(unittest.TestCase):
 def test_reward_first(self): self.assertEqual(choose({'free_rewards': True}).action, 'claim_free_reward')
 def test_purchase_blocks(self): self.assertEqual(choose({'purchase_modal': True}).action, 'stop')
 def test_idle_research(self): self.assertEqual(choose({'research_active': False}).action, 'start_idle_research')
