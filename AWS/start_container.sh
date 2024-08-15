#!/bin/bash
set -e

# Pull the image from docker hub
docker pull eliyasankark/pyaws-app

# Run the docker image as a container
docker run -d -p 5002:5002/eliyasankark/pyaws-app
