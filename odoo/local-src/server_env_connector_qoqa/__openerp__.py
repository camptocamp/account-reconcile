# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{'name': 'Server environment for QoQa Connector',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Tools',
 'complexity': 'expert',
 'depends': ['server_environment',
             'connector_qoqa',
             ],
 'description': """
Server environment for QoQa Connector
=====================================

This module is based on the `server_environment` module to use files for
configuration.  Thus we can have a different configutation for each
environment (dev, test, staging, prod).  This module define the config
variables for the `connector_qoqa` module.

In the configuration file, you can configure the url of the QoQa Backends.

Exemple of the section to put in the configuration file::

    [qoqa_backend.name_of_the_backend]
    location = http://localhost

""",
 'website': 'http://www.camptocamp.com',
 'data': [],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
