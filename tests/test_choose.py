import os, sys, json, unittest
choose_path = sys.path.insert(1, '../src/')
import choose as c

class test_choose(unittest.TestCase):
    def setUp(self):
        default_config_file = open(os.getcwd() + '/../src/res/defaults.json', mode='r')
        data = default_config_file.read()
        default_config_file.close()
        self.default_config = json.loads(data)
        self.randmomizer = c.CivRandomizer()

    def testFound(self):
        self.assertTrue(True)

    def randomizerHasDefaultConfig(self):
        self.assertEquals(randomizer.config, default_config)
