# Basic profile retrieval

> This API is available at `/api/basic/`

The ID service exposes an API that provides read-only basic/minimal profile information and nothing else.

Because this API's use is on the "hot path" of user authentication, and will therefore see high usage and pressure on performance and availability, it is split into its own *infra-service*: `BASIC_PROFILE`.
