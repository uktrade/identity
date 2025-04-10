# User management

> This API is available at `/api/scim/v2/Users`

The ID service exposes a limited [SCIM](https://scim.cloud/) API interface to allow management of Users.

Due to the risk this API's exposure carries, it interface is only accessible to the Staff SSO service. Staff SSO directly manages the ID User statuses, and the StaffSSOProfile information via this API.

This API is enabled only on the `SSO_SCIM` *infra-service*, allowing it to be additionaly protected by netwrok-level protections; i.e. only being accessible via the Staff SSO network.
