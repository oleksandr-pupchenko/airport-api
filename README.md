# Airport API - AirGate

***

API service for airport management written on DRF

DB structure

![db_structure.png](documentation_image%2Fdb_structure.png)

### Environment Variables

***
This project uses environment variables for configuration. To set up the required variables, follow these steps:

1. Create a new `.env` file in the root directory of the project.

2. Copy the contents of the `.env_sample` file into `.env`.

3. Replace the placeholder values in the `.env` file with the actual values specific to your environment.

## Run with docker

```
docker-compose up --build
```

You can use this admin user

Email: `admin@admin.com`
Password: `1qazcde3`

or

***

- create user via /api/user/register/

***

and then generate access token:

- get access token via /api/user/token/

## Features

***

- JWT authenticated
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/
- Managing orders and tickets
- Creating routes with source and destination
- Creating airplanes
- Adding flights
- Filtering routes and flights

## Documentation

 ---

* api/doc/swagger/: Documentation using Swagger

![doc_api.png](documentation_image%2Fdoc_api.png)
