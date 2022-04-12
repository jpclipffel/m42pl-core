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
    'regex',
    'jsonpath-ng',
    'lark-parser[regex]',
    'lark_cython',
    'types-setuptools',
    # Required by the mains
    # TODO: Remove once mains moved to custom repo/project/...
    'tabulate',
    'prompt_toolkit',
  ],
)
