# Automated Rancher build

## Travis deployment

When committing on master branch, if tests pass, Travis will:

1. Build a docker image
2. Push it on DockerHub with the tag: `latest`
3. Upgrade the stack on rancher with image `latest`

Thus, the test server will be continuously upgraded.

## Rancher templates

The templates for rancher are defined in [rancher folder](../rancher).

In which we find [latest](../rancher/latest). This templates defines the
rancher stack automatically upgraded by Travis.

## Rancher environment setup

In order to configure the variables for the container built on Rancher by
Travis, `.rancher.env.enc` is used.

To create it, uses:

```
travis encrypt-file -f --pro .rancher.env
```

It contains credentials for rancher, Postgres configuration, scenario tag and
Odoo environment variables.
(An unencrypted copy of `.rancher.env` is available on LastPass)
