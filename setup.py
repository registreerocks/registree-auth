from setuptools import setup

setup(name='registree-auth',
  version='0.2',
  description='Registree API authorization functionality',
  url='https://github.com/registreerocks/registree-auth',
  maintainer='Sabine Bertram',
  maintainer_email='sabine@registree.io',
  license='MIT',
  packages=['registree_auth'],

  install_requires = ['Flask', 'python-jose-cryptodome']
)