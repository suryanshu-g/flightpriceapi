pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Repository checked out successfully'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t travel-predictor:jenkins .'
            }
        }

        stage('Verify Image') {
            steps {
                sh 'docker images | grep travel-predictor'
            }
        }

    }
}
