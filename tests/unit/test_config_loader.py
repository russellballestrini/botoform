from unittest import TestCase

from botoform.config import ConfigLoader

TEMPLATE_DIR = 'tests'
TEMPLATE_FILE = 'webapp.yaml'

class TestConfigLoader(TestCase):
    def setUp(self):
        self.template_dir    = TEMPLATE_DIR
        self.template_file   = TEMPLATE_FILE
        with open(TEMPLATE_DIR + '/' + TEMPLATE_FILE) as f:
            self.template_string = f.read()
        self.context_vars = {
                 'vpc_name'  : 'webapp01',
                 'cidrblock' : '192.168.1.1/24',
             }

    def test_constructor_templates_in_searchpath(self):
        loader = ConfigLoader()
        self.assertTrue('templates' in loader.jinja2_env.loader.searchpath)

    def test_constructor_template_dir_in_searchpath(self):
        loader = ConfigLoader(template_dir='taco')
        self.assertTrue('taco' in loader.jinja2_env.loader.searchpath)

    def test_constructor_default_context_vars_is_empty_dict(self):
        loader = ConfigLoader()
        self.assertTrue(len(loader.context_vars) == 0)
        self.assertEqual(loader.context_vars, {}) 

    def test_constructor_context_vars_is_set(self):
        loader = ConfigLoader(context_vars=self.context_vars)
        self.assertTrue(len(loader.context_vars.keys()) == 2)
        self.assertTrue('cidrblock' in loader.context_vars.keys())

    def test_load_template_string_without_context(self):
        loader = ConfigLoader(self.template_dir)
        config = loader.load(template_string=self.template_string)
        self.assertEqual(len(config), 9)
        self.assertEqual(len(config['instance_roles']), 1)
        self.assertEqual(len(config['amis']), 4)
        self.assertEqual(len(config['security_groups']), 2)
        self.assertEqual(len(config['security_groups']['web']), 1)
        self.assertEqual(config['cidrblock'], '192.168.1.0/24')

    def test_load_template_file_without_context(self):
        loader = ConfigLoader(self.template_dir)
        config = loader.load(template_file = self.template_file)
        self.assertEqual(len(config), 9)
        self.assertEqual(len(config['instance_roles']), 1)
        self.assertEqual(len(config['amis']), 4)
        self.assertEqual(len(config['security_groups']), 2)
        self.assertEqual(len(config['security_groups']['web']), 1)
        self.assertEqual(config['cidrblock'], '192.168.1.0/24')


