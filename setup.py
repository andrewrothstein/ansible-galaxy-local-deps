from setuptools import setup, find_packages

setup(name='ansible-galaxy-local-deps',
      version='0.0.14',
      description='CLI for building, tagging, and publishing Docker containers',
      url='http://github.com/andrewrothstein/ansible-galaxy-local-deps',
      author='Andrew Rothstein',
      author_email='andrew.rothstein@gmail.com',
      license='MIT',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      python_requires='>=3.5',
      install_requires=['PyYAML'],
      tests_require=['nose2'],
      zip_safe=False,
      entry_points={
        'console_scripts': [
            'ansible-galaxy-local-deps-install=ansiblegalaxylocaldeps.installdeps:main',
            'ansible-galaxy-local-deps-write=ansiblegalaxylocaldeps.writedeps:main',
            'gendottravis=ansiblegalaxylocaldeps.gendottravis:main'
        ]
      }
      )
