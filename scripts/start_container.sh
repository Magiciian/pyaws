#!/bin/bash
set -e

# Pull the image from Docker Hub
docker pull eliyasankark/pyaws-app

# Run the Docker image as a container
docker run -d -p 5003:5003 eliyasankark/pyaws-app
 
