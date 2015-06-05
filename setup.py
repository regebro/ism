from setuptools import setup, find_packages

version = '0.1'

with open('README.rst', 'rt') as readme:
    description = readme.read()

with open('CHANGES.txt', 'rt') as changes:
    history = changes.read()


setup(name='ism',
      version=version,
      description="Ism is a console code editor",
      long_description=description + '\n' + history,
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Environment :: Console :: Curses',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.4',
                   'Topic :: Text Editors',
                   ],
      keywords='editor',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='https://github.com/regebro/ism',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      test_suite='tests.make_suite',
      install_requires=[
          'doctrine.urwid',
      ],
      entry_points = {
          'console_scripts': ['ism=ism.main:main'],
      }
)
