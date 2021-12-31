from setuptools import setup


setup(
  name='m42pl_core',
  author='@jpclipffel',
  url='https://github.com/jpclipffel/m42pl-core',
  version='0.0.1',
  packages=['m42pl',],
  package_data={
      '': ['m42pl/files/*',]
  },
  entry_points={
    'console_scripts': [
      'm42pl=m42pl.__main__:main'
    ]
  },
  install_requires=[
    'regex>=2021.11.10',
    'jsonpath-ng>=1.5.3',
    'lark-parser[regex]>=0.12.0',
    'types-setuptools',
    'tabulate>=0.8.9',
    'flask>=2.0.2'
  ],
)
