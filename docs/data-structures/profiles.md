# Profiles

Profiles are the most complex area of the identity service. They hold and manage all the parts of an identity's data that are not related to auth.

## Core concepts

The ID service connects various providers of overlapping user data, and is the source of truth of some but not all of that data.

There are a few concepts we're following in the codebase to make sense of all that.

### Provider-specific Profiles

To account for different providers having different data about the same users, Identity maintains a distinct Profile record for each provider, which holds all the data retrieved from that provider. The idea is that it's always possible to see which data provider has submitted any given information to ID.

The `StaffSSOProfile` record contains `first_name`, `last_name`, `contact_email` and `emails`.

The `PeopleFinderProfile` record contains many more fields than this, but will also contain a `first_name` and a `last_name` field, as well as `preferred_name`.

### The "combined" Profile

The provider-specific Profile records maintain data integrity but contain overlapping information, so Identity maintains a "combined" `Profile` record.

This combined record is de-normalised (i.e. it only contains duplicates of data held in other profiles) but it represents ID's best effort understanding of the _right_ data for any given field.

This Profile should never have data written directly to it; instead it should always have its data generated via the service function, which ensures a consistent approach to hierarchy between overlapping field data.

### Emails, Teams and similar data

Data such as Email and Team is seen as concrete data needing a representation outside and as well as the providers' differing views. This is to allow us to rationalise about differing providers' understanding of the role of a given email and to get a combined view of all the emails a personn has access to, for example.

These are rendered as "generic" models, with explicit M2M thrgouh models to the provider-specific Profiles providing context as needed.

## Internal app structure

Since there are a lot of models and services in this module, we've further split them into Abstract (non-concrete ancestors of classes), Generic (concrete but non-provider-specific), Specific (e.g. `StaffSSOProfile`), and Combined (`Profile`) submodules, which makes it easier to group related models.

Note that `__init__.py` is used at the higher level services module to provide functionality abstracting away these distinctions.
