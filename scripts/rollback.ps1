# Manual rollback on Windows: restores the last known-good image.
docker rm -f flask-cicd-container 2>$null
docker run -d --name flask-cicd-container -p 5000:5000 --restart unless-stopped flask-cicd-app:stable
Write-Host "Rolled back to flask-cicd-app:stable"
