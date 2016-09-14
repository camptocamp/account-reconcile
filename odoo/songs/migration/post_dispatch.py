# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

logger = logging.getLogger('migration.dispatch')


def _get_dispatch_pickings(cr, dispatch_id):
    """ Return all stock.picking (id, state) which should be linked
    to the batch and check if each pickings have all their moves
    in the dispatch.
    """
    cr.execute(
            "SELECT picking_id, p.state, COUNT(*) AS all_count, "
            "COUNT(*) FILTER (WHERE dispatch_id=%s) AS filter_count "
            "FROM stock_move "
            "JOIN stock_picking p ON picking_id=p.id "
            "WHERE picking_id IN ("
            "    SELECT picking_id FROM stock_move WHERE dispatch_id = %s"
            ") GROUP BY picking_id, p.state", (dispatch_id, dispatch_id)
        )

    picking_ids = []
    bad_picking_ids = []
    for pick_id, state, all_count, filter_count in cr.fetchall():
        if all_count == filter_count:
            picking_ids.append((pick_id, state))
        else:
            bad_picking_ids.append(pick_id)

    if bad_picking_ids:
        logging.error(
            "The dispatch id=%s has been ignored because "
            "the following pickings have not all their moves in "
            "the dispatch: %s",
            dispatch_id, bad_picking_ids
        )
    return picking_ids


def dispatch_migration(ctx):
    """ Migrate active picking dispatch to stock_batch_picking
    """
    cr = ctx.env.cr

    cr.execute(
        "SELECT id, create_uid, create_date, write_uid, picker_id, "
        "notes, date, name "
        "FROM picking_dispatch WHERE state NOT IN ('done', 'cancel')"
    )

    dispatches = cr.fetchall()
    migrated_ids = []
    for dispatch_row in dispatches:
        dispatch_row = list(dispatch_row)

        dispatch_id = dispatch_row.pop(0)

        picking_states = _get_dispatch_pickings(cr, dispatch_id)
        if not picking_states:
            continue

        migrated_ids.append(dispatch_id)

        if all(p[1] == 'assigned' for p in picking_states):
            state = 'assigned'
        else:
            state = 'draft'

        dispatch_row.append(state)

        cr.execute(
            "INSERT INTO stock_batch_picking "
            "(create_uid, create_date, write_uid, picker_id, "
            "notes, date, name, state, active)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true) RETURNING id",
            dispatch_row
        )
        batch_id = cr.fetchone()[0]

        cr.execute(
            "UPDATE stock_picking SET batch_picking_id=%s WHERE id IN %s",
            (batch_id, tuple(p[0] for p in picking_states))
        )

    if migrated_ids:
        cr.execute("DELETE FROM picking_dispatch WHERE id IN %s",
                   (tuple(migrated_ids), ))
