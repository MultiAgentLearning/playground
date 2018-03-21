from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    install_requires = f.readlines()

with open('requirements_extra.txt', 'r') as f:
    extras_require = f.readlines()

with open('VERSION') as f:
    version = f.read().strip()

setup(name='pommerman',
      version=version,
      description='PlayGround: AI Research into Multi-Agent Learning',
      url='https://www.pommerman.com',
      author='Pommerman',
      author_email='support@pommerman.com',
      license='Apache 2.0',
      packages=find_packages(),
      install_requires=install_requires,
      extras_require={
        'extras': extras_require # @TODO this might need refinement
      },
      entry_points={
        'console_scripts': [
            'pom_battle=pommerman.cli.run_battle:main',
            'pom_tf_battle=pommerman.cli.train_with_tensorforce:main',
        ],
      },
      zip_safe=False)
