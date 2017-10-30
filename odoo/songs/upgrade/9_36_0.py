# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.uninstaller import uninstall


@anthem.log
def main(ctx):
    # we will uninstalled modules
    uninstall(ctx, ['password_security'])
