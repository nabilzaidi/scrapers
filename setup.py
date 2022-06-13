from setuptools import setup, find_packages

version = '1.5'

setup(
  name = 'scrapers',         # How you named your package folder (MyLib)
  packages = find_packages(),   # Chose the same as "name"
  version = version,      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Scrapers for some websites',   # Give a short description about your library
  author = 'NZF',                   # Type in your name
  author_email = 'nabilcodemail@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/nabilzaidi/scrapers',   # Provide either the link to your github or to your website
  download_url = f'https://github.com/nabilzaidi/scrapers/archive/{version}.tar.gz',    # I explain this later on
  keywords = ['SCRAPPING', "Trustpilot", "Avis Vérifiés"],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'requests',
          'unidecode',
          'lxml',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)