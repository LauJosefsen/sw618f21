# sw618f21

## Setup
Make sure you have docker and docker-compose installed and working

To build the docker-containers:
`docker-compose build`

To start the docker network:

`docker-compose up`

To remove the network:

`docker-compose down`

To fix pycharm errors, you need to add docker-composer as the interpreter in pycharm.

The services can be accessed as following:

PostgreSQL: `postgres@localhost:5432 -p password`

API: `localhost:5000`

React: `localhost:3000` in browser
