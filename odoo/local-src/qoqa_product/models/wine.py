# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import _, api, exceptions, fields, models


def volume_to_string(value, unit='l'):
    prefix = u''
    if value < 1:
        value *= 100
        prefix = u'c'
    value = (u'%.2f' % value).rstrip(u'0').rstrip('.')
    return value + u' ' + prefix + unit


class WineWinemaker(models.Model):
    _name = 'wine.winemaker'
    _description = 'Winemaker'

    name = fields.Char(required=True)


class WineType(models.Model):
    _name = 'wine.type'
    _description = 'Wine Type'

    name = fields.Char(required=True)


class WineBottle(models.Model):
    """ The bottle is used to define the capacity of wine bottles.

    It is needed in reports to compute sums as we receive a qantity
    of bottle this needs to be translated in litres.
    """
    _name = 'wine.bottle'
    _description = 'Wine Bottle'

    _order = 'volume'

    name = fields.Char(required=True)
    complete_name = fields.Char(compute='_compute_complete_name')
    code = fields.Char()
    volume = fields.Float(required=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            volume = volume_to_string(record.volume)
            name = u'{} ({})'.format(record.name, volume)
            res.append((record['id'], name))
        return res

    @api.depends('name', 'volume')
    def _compute_complete_name(self):
        for record in self:
            record.complete_name = record.name_get()[0][1]


class WineClass(models.Model):
    """ The class is used on the reports to group the wines.

    The tree is something as follows (excerpt)::

        10 Classe AOC
          110 Suisse occidentale
            Vaud
            Valais
          120 Suisse orientale
            Zurich
            Autres cantons
          130 Tessin
        20 Classe Vin de pays
          Suisse occidentale
          Suisse orientale
          Vin Suisse

    Only the leaves can be assigned on products.
    It is close to the regions, but not necessarily, sometimes, a leaf
    is a region, sometimes a country, or a 'other'.
    """
    _name = 'wine.class'
    _description = 'Wine Class'

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code'
    _order = 'parent_left'

    name = fields.Char(required=True)
    complete_name = fields.Char(compute='_compute_complete_name')
    code = fields.Char()
    parent_id = fields.Many2one(
        comodel_name='wine.class',
        string='Parent class',
    )
    child_ids = fields.One2many(
        comodel_name='wine.class',
        inverse_name='parent_id',
        string='Children classes',
    )
    parent_left = fields.Integer(string='Left Parent', index=True)
    parent_right = fields.Integer(string='Right Parent', index=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.parent_id:
                name = record.parent_id.name_get()[0][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    @api.depends()
    def _compute_complete_name(self):
        for record in self:
            record.complete_name = record.name_get()[0][1]

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise exceptions.ValidationError(
                _('Error! You cannot create recursive classes.')
            )
