pipeline {
    agent any

    environment {
        // Build locally first, then tag the image for the DockerHub account configured in Jenkins.
        LOCAL_IMAGE_NAME = "house-price-api:latest"
        CONTAINER_NAME = "house-api"
    }

    stages {
        stage('Clone latest code') {
            steps {
                // Jenkins checks out the repository so the pipeline always uses the newest commit.
                checkout scm
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build -t "$LOCAL_IMAGE_NAME" .'
            }
        }

        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                    sh '''
                        echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                    '''
                    script {
                        env.FULL_IMAGE_NAME = "${env.DOCKERHUB_USER}/house-price-api:latest"
                    }
                }
            }
        }

        stage('Push image to DockerHub') {
            steps {
                sh '''
                    docker tag "$LOCAL_IMAGE_NAME" "$FULL_IMAGE_NAME"
                    docker push "$FULL_IMAGE_NAME"
                '''
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh '''
                    docker compose pull app prometheus grafana
                    docker compose up -d
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment completed successfully.'
        }
        failure {
            echo 'Deployment failed. Check the console output for details.'
        }
    }
}
