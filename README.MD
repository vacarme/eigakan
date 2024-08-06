# Eigakan
Demo of a full asynchronous backend API server based on FastAPI and SQLAlchemy.

# Stack
## API
+ *fastapi* for routing,
+ *sqlalchemy* for ORM and everything database related,
+ *pydantic* for serialization,
+ *uvicorn* for ASGI web server,
+ *slowapi* for rate limiting.
## Database
+ *postgis* (geospatial enriched PostgreSQL)
## Toolchain
+ [*mise*](https://mise.jdx.dev) for managing environment variables, python version and tasks,
+ [*poetry*](https://python-poetry.org) for dependency management.
+ *vscode* (with vim motions) for development.
## Deployment
I am used to work with kubernetes, so upon release this image would be pushed to a container registry and then deployed on a k8s cluster from a gitlab or github job/action. Consequently, this explain the absence of a concurrency configuration for *uvicorn* as scaling would be done at the *k8s* level.
# How to Run
Docker is required.
+ Mount the stack by running: `docker compose -f docker/compose.yaml up`
+ Seed the database by running: `seed` (current package should be installed)

API interactive swagger should be available at http://localhost:8000/api/docs, use the following credentials to get a token for authenticated routes:
+ username: alex@nd.re
+ pwd: aloha
# TODO
+ testing
+ cli
# References
This project is inspired by netflix's [dispatch](https://github.com/Netflix/dispatch) repo.