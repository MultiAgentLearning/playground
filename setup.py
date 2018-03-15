from setuptools import setup, find_packages

setup(name='pommerman',
      version='0.1.0',
      description='PlayGround: AI Research into Multi-Agent Learning',
      url='https://www.pommerman.com',
      author='Pommerman',
      author_email='support@pommerman.com',
      license='Apache 2.0',
      packages=find_packages(),
      install_requires=[
        # @TODO
      ],
      entry_points = {
        'console_scripts': [
            'pom-battle=pommerman.cli.run_battle:main',
            'pom-tf-battle=pommerman.cli.train_with_tensorforce:main',
        ],
      },
      zip_safe=False)
