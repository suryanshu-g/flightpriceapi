pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checkout successful'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t travel-predictor:latest .'
            }
        }

        stage('Verify Image') {
            steps {
                sh 'docker images'
            }
        }
    }
}
