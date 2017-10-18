# Local Documentation

Empty. You can add an index for the documentation specific to this project.

# How to replication RDS from production to integration

* First: Ask the infrastructure Team to make a snapshot of the production to integration.
* With connexionlinks we have 
```qoqa-platform-int-db 9451
```
for the connexion we use
```psql -p 9451 -h localhost -U postgres postgres
```
 Grab the password on Lastpass
 
* Second: We will need to rename database name
```
ALTER database qoqa_odoo_prod RENAME TO qoqa_odoo_integration
```
* Third: We will grand all privileges to database 
Reconnect with:
```psql -p 9451 -h localhost -U qoqa_odoo_integration qoqa_odoo_integration
```
Grab password from lastpass
```
 GRANT ALL ON schema public TO qoqa_odoo_integration ;
 ```
