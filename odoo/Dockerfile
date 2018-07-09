FROM camptocamp/odoo-project:9.0-2.6.1
MAINTAINER Camptocamp

# Install additional debian packages if needed
# RUN set -x; \
#         apt-get update \
#         && apt-get install -y --no-install-recommends \
#         python-shapely \
#         && apt-get clean \
#         && rm -rf /var/lib/apt/lists/*

COPY ./before-migrate-entrypoint.d/* odoo/before-migrate-entrypoint.d/
COPY ./start-entrypoint.d/* odoo/start-entrypoint.d/
RUN chmod +x odoo/before-migrate-entrypoint.d/* \
    && chmod +x odoo/start-entrypoint.d/*

# Install additional python packages if needed
COPY ./requirements.txt /opt/odoo
RUN pip install --upgrade pip setuptools && cd /opt/odoo && pip install -r requirements.txt

ENV ADDONS_PATH="/opt/odoo/external-src/enterprise, \
  /opt/odoo/src/addons, \
  /opt/odoo/local-src, \
  /opt/odoo/external-src/l10n-switzerland, \
  /opt/odoo/external-src/account-analytic, \
  /opt/odoo/external-src/account-financial-reporting, \
  /opt/odoo/external-src/account-financial-tools, \
  /opt/odoo/external-src/account-fiscal-rule, \
  /opt/odoo/external-src/account-invoice-reporting, \
  /opt/odoo/external-src/account-invoicing, \
  /opt/odoo/external-src/bank-payment, \
  /opt/odoo/external-src/bank-statement-reconcile, \
  /opt/odoo/external-src/carrier-delivery, \
  /opt/odoo/external-src/connector, \
  /opt/odoo/external-src/connector-ecommerce, \
  /opt/odoo/external-src/crm, \
  /opt/odoo/external-src/e-commerce, \
  /opt/odoo/external-src/margin-analysis, \
  /opt/odoo/external-src/multi-company, \
  /opt/odoo/external-src/odoo-cloud-platform, \
  /opt/odoo/external-src/odoo-usability, \
  /opt/odoo/external-src/partner-contact, \
  /opt/odoo/external-src/product-attribute, \
  /opt/odoo/external-src/product-variant, \
  /opt/odoo/external-src/purchase-workflow, \
  /opt/odoo/external-src/purchase-reporting, \
  /opt/odoo/external-src/reporting-engine, \
  /opt/odoo/external-src/rma, \
  /opt/odoo/external-src/sale-workflow, \
  /opt/odoo/external-src/server-tools, \
  /opt/odoo/external-src/stock-logistics-warehouse, \
  /opt/odoo/external-src/stock-logistics-reporting, \
  /opt/odoo/external-src/stock-logistics-workflow, \
  /opt/odoo/external-src/web" \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736
