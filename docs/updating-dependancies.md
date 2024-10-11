---
hide:
  - navigation
---

## Managing Python dependencies

This project uses [Poetry](https://python-poetry.org) for dependency management.

We recommend reading through the [docs](https://python-poetry.org/docs/), in particular
the sections on the [CLI](https://python-poetry.org/docs/cli/) and [Dependency
specification](https://python-poetry.org/docs/dependency-specification/).

Below is an example of how to use Poetry to handle the dependencies in this project.

```bash
# Start a bash session
make bash
# Update all packages (respects the version constraints in pyproject.toml)
poetry update
# Update selected packages (respects the version constraints in pyproject.toml)
poetry update django wagtail
# Update a package to a version outside it's constraints
poetry add django@^5.1.0
```