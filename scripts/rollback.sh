#!/usr/bin/env bash
# Manual rollback on Linux/macOS: restores the last known-good image.
docker rm -f flask-cicd-container 2>/dev/null
docker run -d --name flask-cicd-container -p 5000:5000 --restart unless-stopped flask-cicd-app:stable
echo "Rolled back to flask-cicd-app:stable"
