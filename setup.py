from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='ansible-galaxy-local-deps',
      version='0.5.6',
      description='CLI for interacting with Ansible roles and their CIs',
      url='http://github.com/andrewrothstein/ansible-galaxy-local-deps',
      author='Andrew Rothstein',
      author_email='andrew.rothstein@gmail.com',
      license='MIT',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      python_requires='>=3.5',
      install_requires=['PyYAML'],
      extras_require={
          "test": ['nose2']
      },
      long_description=long_description,
      long_description_content_type='text/markdown',
      zip_safe=False,
      entry_points={
        'console_scripts': [
            'ansible-galaxy-local-deps-install=ansiblegalaxylocaldeps.installdeps:main',
            'ansible-galaxy-local-deps-write=ansiblegalaxylocaldeps.writedeps:main',
            'gengithubactions=ansiblegalaxylocaldeps.gengithubactions:main',
            'ansible-galaxy-local-deps-change-dep=ansiblegalaxylocaldeps.changedep:main',
        ]
      }
      )
