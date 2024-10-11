---
hide:
  - navigation
---

## Setup
To get started you will need to copy the example .env file.
```bash
cp .env.example .env
```


Afterwards, run the following command to build and start the project:
```bash
make setup
```

## Build project styling
To build the front end styling you will need to run, the command bellow, in a seperate terminal.
```bash
make vite
```

### Assets
Assets are handled via vite. A number of npm
tasks are provided for development:

- `npm run dev` watches the asset folder and recompiles on changes
- `npm run build` compiles assets once