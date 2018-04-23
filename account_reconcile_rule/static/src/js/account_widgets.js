odoo.define('account_reconcile_rule', function (require) {
    "use strict";

    var core = require('web.core');
    var reconciliation_renderer = require('account.ReconciliationRenderer');

    reconciliation_renderer.LineRenderer.include({
        init: function (parent, state, params) {
            this._super(parent, state, params);
            this.preset_auto_clicked = false;
        },
        reconciliation_rule_models: function() {
            var self = this;
            // Get the statement line
            var line = this.model.getLine(this.handle)
            if (self.preset_auto_clicked) {
                return
            }
            this._rpc({
                model: 'account.reconcile.rule',
                method: 'models_for_reconciliation',
                args: [
                    line.st_line.id,
                    _.pluck(line.reconciliation_proposition, 'id')
                ],
            }).done(function(rule_models) {
                _.each(rule_models, function (rule_model_id) {
                    self.trigger_up('quick_create_proposition', {'data': rule_model_id});
                })
                self.preset_auto_clicked = true;
            })
        },
        start: function () {
            var self = this;
            var deferred = this._super();
            if (deferred) {
                deferred.done(this.reconciliation_rule_models());
            }
            return deferred;
        },
        /**
         * Click on add_line link if preset button have been clicked
         * automatically.
         */
//        formCreateInputChanged: function(elt, val) {
//            var self = this;
//            var deferred = this._super(elt, val);
//            deferred.done(function() {
//                if (self.preset_auto_clicked) {
//                    self.addLineBeingEdited();
//                }
//            });
//        },
//        restart: function () {
//            var deferred = this._super();
//            deferred.done(this.operation_rules());
//            return deferred;
//        }
    });
});
