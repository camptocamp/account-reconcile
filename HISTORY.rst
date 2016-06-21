.. :changelog:

Release History
---------------

unreleased (unknown)
++++++++++++++++++++

**Features and Improvements**

**Bugfixes**

* Slow accounting dashboard: had to override
  account.account_journal_dashboard methods to change a few
  ORM calls by direct SQL and to totally remove one slow computation (account
  balance) and the graphs

**Build**

* Use camptocamp/postgresql:pg9.5-latest in the dev composition

**Documentation**

.. Template:

.. 0.0.1 (2016-05-09)
.. ++++++++++++++++++

.. **Features and Improvements**

.. **Bugfixes**

.. **Build**

.. **Documentation**

.. Template:
