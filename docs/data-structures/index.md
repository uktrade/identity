# Data structures

The ID codebase uses Django Apps to isolate and abstract implementation details behind a service layer (Django two scoops terminology).

> *Core* deals with whole identities, splitting them into [*Users*](./users.md) and [*Profiles*](./profiles.md).

The `sso_email_id` - the Staff SSO system's primary unique identifier - is used by default as the "id" across all User and Profile records. All user records are exclusively managed by the Staff SSO service, this gives a unique and consistent means of identification.

User records contain only an ID and state / permission flags, all actual user information is stored in Profiles.

[History](https://django-simple-history.readthedocs.io/en/latest/) is enabled for all User and Profile information, as well as audit logs.
