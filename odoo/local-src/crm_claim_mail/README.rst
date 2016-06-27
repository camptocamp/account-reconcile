
CRM Claim Mail
==============

Customizations for QoQa on CRM and e-mails.
This is specific because it makes assumptions about how the setup is done.
Exemple: the number of the claims should be RMA-\\d+

Features:

* When an email cannot be linked with its originating claim with the
 'In-Reply-To' or 'References' header, it tries to match it with it
 number. The numbers of the claims must start with RMA-
* When a new claim is created, an email is sent to the customer and the claim
 is set to the stage 'In Progress'.
* When an email is received on an existing claim, the claim is set back to a
  new stage "Response Received"

** WARNING **
This module installs the fr_FR and de_DE languages.
