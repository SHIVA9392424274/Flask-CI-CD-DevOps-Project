// Declarative CI/CD pipeline: works on Windows (bat) and Linux (sh) Jenkins agents.

def run(String cmd) {
    if (isUnix()) { sh cmd } else { bat "@echo off\r\n${cmd}" }
}

def runStatus(String cmd) {
    return isUnix() ? sh(script: cmd, returnStatus: true)
                    : bat(script: "@echo off\r\n${cmd}", returnStatus: true)
}

def venvPython() { return isUnix() ? 'venv/bin/python' : 'venv\\Scripts\\python' }

pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 20, unit: 'MINUTES')
    }

    // githubPush needs the GitHub webhook; pollSCM is the fallback if no webhook is possible.
    triggers {
        githubPush()
        pollSCM('H/2 * * * *')
    }

    parameters {
        booleanParam(name: 'PUBLISH_IMAGE', defaultValue: false, description: 'Push the image to Docker Hub')
        string(name: 'DOCKERHUB_USER', defaultValue: 'your-dockerhub-username', description: 'Docker Hub username (used only when publishing)')
    }

    environment {
        IMAGE_NAME     = 'flask-cicd-app'
        CONTAINER_NAME = 'flask-cicd-container'
        HOST_PORT      = '5000'
        APP_VERSION    = "1.0.${env.BUILD_NUMBER}"
    }

    stages {
        stage('Source Code Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Dependency Installation') {
            steps {
                script {
                    def py = isUnix() ? 'python3' : 'python'
                    run("${py} -m venv venv")
                    run("${venvPython()} -m pip install --upgrade pip")
                    run("${venvPython()} -m pip install -r requirements.txt")
                }
            }
        }

        stage('Application Build') {
            steps {
                // Byte-compile to catch syntax errors early.
                script { run("${venvPython()} -m compileall app") }
            }
        }

        stage('Automated Testing') {
            steps {
                script {
                    run("${venvPython()} -m pytest tests --junitxml=reports/junit.xml")
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('Docker Image Build') {
            steps {
                script {
                    run("docker build --build-arg APP_VERSION=${env.APP_VERSION} -t ${env.IMAGE_NAME}:${env.BUILD_NUMBER} -t ${env.IMAGE_NAME}:latest .")
                }
            }
        }

        stage('Docker Image Publishing') {
            when { expression { params.PUBLISH_IMAGE } }
            steps {
                // Create a "Username with password" credential in Jenkins with ID: dockerhub-creds
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    script {
                        def remote = "${params.DOCKERHUB_USER}/${env.IMAGE_NAME}"
                        if (isUnix()) {
                            sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
                        } else {
                            bat '@echo off\r\necho %DH_PASS%| docker login -u %DH_USER% --password-stdin'
                        }
                        run("docker tag ${env.IMAGE_NAME}:${env.BUILD_NUMBER} ${remote}:${env.BUILD_NUMBER}")
                        run("docker tag ${env.IMAGE_NAME}:${env.BUILD_NUMBER} ${remote}:latest")
                        run("docker push ${remote}:${env.BUILD_NUMBER}")
                        run("docker push ${remote}:latest")
                    }
                }
            }
        }

        stage('Application Deployment') {
            steps {
                script {
                    // Remove the old container (ignore error if none exists). The previous
                    // working image is already preserved under the tag :stable (see below).
                    runStatus("docker rm -f ${env.CONTAINER_NAME}")
                    run("docker run -d --name ${env.CONTAINER_NAME} -p ${env.HOST_PORT}:5000 --restart unless-stopped ${env.IMAGE_NAME}:${env.BUILD_NUMBER}")
                }
            }
        }

        stage('Deployment Verification') {
            steps {
                script {
                    run("${venvPython()} scripts/verify.py http://localhost:${env.HOST_PORT}/health 10 3")
                    // New version is healthy: promote it to :stable for future rollbacks.
                    run("docker tag ${env.IMAGE_NAME}:${env.BUILD_NUMBER} ${env.IMAGE_NAME}:stable")
                }
            }
        }
    }

    post {
        success {
            echo "SUCCESS: version ${env.APP_VERSION} is live at http://localhost:${env.HOST_PORT}"
        }
        failure {
            script {
                echo 'FAILURE detected. Attempting rollback to the last stable image...'
                def hasStable = runStatus("docker image inspect ${env.IMAGE_NAME}:stable") == 0
                if (hasStable) {
                    runStatus("docker rm -f ${env.CONTAINER_NAME}")
                    def rc = runStatus("docker run -d --name ${env.CONTAINER_NAME} -p ${env.HOST_PORT}:5000 --restart unless-stopped ${env.IMAGE_NAME}:stable")
                    if (rc == 0) {
                        echo 'ROLLBACK COMPLETE: previous stable version is running again.'
                    } else {
                        echo 'ROLLBACK FAILED: please check Docker manually.'
                    }
                } else {
                    echo 'No stable image yet (first deployment). Nothing to roll back to.'
                }
            }
        }
        always {
            // Show recent container logs in the build log for troubleshooting.
            script { runStatus("docker logs --tail 30 ${env.CONTAINER_NAME}") }
        }
    }
}
