---
hide:
  - navigation
---

# About

Identity is the dedicated service for staff profile and directory information for the Department for Business and Trade (DBT) built using [Django](https://www.djangoproject.com/).

It currently provides no user-facing front end.

Identity is currently managed and developed by the [Employee Experience Team](https://github.com/orgs/uktrade/teams/employee-experience).

## Role of the service

Identity (ID) exists to bring together user information across a variety of products and services in use across the department, many of which do not interface with each other. It does not manage authentication or authorisation.

ID is the source of truth for only some of the fields available (generally user-generated data entered via People Finder) but aims to consolidate relevant people data across any service that contains it. Read more about ID's [data structures](./data-structures) and the [APIs](./apis) used to expose and manage it.

ID provides a simple integration point for custom-built services erquiring live people data for staff and users within the department.

## Core concepts

### Users and Profiles

To maintain the highest granularity of data, the ID system distinguishes between User and Profile records.

Within the ID system, a User represents a single person; other than an identifier and state flags, it holds no other personal information. User records and their state are "owned" by Staff SSO (see below).

Profile records are the way the ID service maintains (sometimes conflicting) data about a User from different sources. Each data source has its own Profile type and writes only to that type. The ID service maintains a distinct "combined" (de-normalised) Profile that represents the most accurate data across all the data sources.

Read more in [data structures](./data-structures/).

### "Infra services"

Named to follow the AWS ECS naming of "services", the ID service will deploy the main application runtime in multiple configurations, each called a "service" in AWS ECS.

This segmentation allows each service to have a distinct load balancer and network configuration allowing for a defence in depth approach to security.

The slightly different configurations used for each of these services will ensure that different APIs may or may not be enabled at all within each of the services; for example the SCIM user management API will only be enabled within the SSO_SCIM infra-service.

## Connected services

Staff SSO is the first point of contact for auth across many of the services in the department; it manages user records for all staff and staff-like users as regards their state and permissions.

In its integration with ID, Staff SSO "owns" User records, their creation, archival and merging, as well as a set of Profile data that arrives into Staff SSO via its other existing integrations.

There are hopes to integrate Oracle (the HR data system) and AD/ADD (the Tech IDAM system) and eventually Matrix (the forthcoming HR system) at some point.

# License information

[https://www.svgrepo.com/page/licensing](https://www.svgrepo.com/page/licensing)
