# How to integrate an open pull request of an external repository

This is currently a manual and boring operation.
We manually consolidate the pull requests in a branch that we push on the camptocamp's GitHub account.


TODO: check the procedure

So the procedure to add a pull request is:

1. cd odoo/external-src/sale-workflow
2. if the branch is already a consolidated branch, skip to point 4.
3. `git checkout -b sale-workflow-9.0-1234` where 1234 is the id of the project on our Odoo instance (ask for it if needed
4. `git fetch origin pull/291/head:pr-291 && git merge pr-291` where 291 is the ID of the pull request
5. `git remote add camptocamp git@github.com:camptocamp/sale-workflow.git`
6. `git push camptocamp/sale-workflow-9.0-1234`
7. `cd ../..`
8. `git add odoo/external-src/sale-workflow`
9. `git commit`

Later, we'll want to have all the pull requests in a file and run a script that consolidate the branches together, that we can push on github.com/camptocamp
