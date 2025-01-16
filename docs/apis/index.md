# APIs

The Identity service exposes different APIs for different purposes, split along lines related to different purposes.

The most restricted, highest risk API is for [user management](./user-management.md) and encompasses creation, archiving and merging.

The most optimisation-prioritised API is for [Staff SSO profile retrieval](./sso-profile.md); this is on the "hot path" for the Staff SSO auth process during user authentication.

The [most general use API](./main.md) is for most use cases.

## Infrastructure "services" and authentication

The ID service at runtime will be split into a running "service" (in AWS ECS terminology) per API, allowing infrastructure-level security to be applied per API.

The *ENV* var `INFRA_SERVICE` is used by the runtime code to tell which service it's running under; this is in turn used to load or unload the URLs for a given API, among other things.

Hawk/Mohawk key-based header auth is also used to protect every API endpoint; there's a distinct id/key pair per API, also based on the same ENV var.

## Direct documentation

APIs in the ID service are directly auto-documented by the Django-ninja package.

With the right permission levels, if you are able to access an API, you can find HTML documentation on the `./docs` endpoint; for example if your API is on `/api/example` the docs would be on `/api/example/docs`.

You will need to be directly user-authenticated on the ID service to access the documentation.
