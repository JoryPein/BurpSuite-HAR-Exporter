# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bpi2har']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.7.0,<0.8.0']

entry_points = \
{'console_scripts': ['bpi2har = bpi2har.cli:app']}

setup_kwargs = {
    'name': 'bpi2har',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Gideon Pein',
    'author_email': 'none@none.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
