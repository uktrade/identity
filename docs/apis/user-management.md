# User management

The ID service exposes a limited SCIM API interface to allow management of Users.

This interface is only accessible to the Staff SSO service. Staff SSO directly manages the ID User statuses, and the StaffSSOProfile information via this API.

This API is enabled only on the `SSO_SCIM` *infra-service*, allowing it to be additionaly protected by netwrok-level protections; i.e. only being accessible via the Staff SSO network.
