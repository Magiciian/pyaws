#!/bin/bash
set -e

# Pull the image from Docker Hub
docker pull eliyasankark/pyaws-app

# Run the Docker image as a container
docker run -d -p 5002:5002 eliyasankark/pyaws-app
 
