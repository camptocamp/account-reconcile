# Automated Rancher build

## Travis deployment

When commiting on master branch, if tests pass, travis will:

1. Build a docker image
2. Push it on dockerhub with `latest` tag
3. Upgrade the stack on rancher with image `latest`

Thus test server will be continuously upgraded.

## Rancher templates

The templates for rancher are defined in [rancher folder](../rancher).

In which we find [template/dev](../rancher/template/dev). This templates defines the rancher stack automatically upgraded.

## Rancher environement setup

In order to configure the container builded by rancher, `.rancher.env.enc` is used.

To create it, uses:

```
travis encrypt-file -f --pro .rancher.env
```

It contains credentials for rancher, Postgres config, scenario tag and Odoo environment.
(An unencrypted copy of `.rancher.env` is available on LastPass)
