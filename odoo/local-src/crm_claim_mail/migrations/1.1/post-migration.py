# -*- encoding: utf-8 -*-

__name__ = "Set the 'confirmation email sent' flag on all existing claims"


def migrate(cr, version):
    cr.execute("UPDATE crm_claim SET confirmation_email_sent = true ")
