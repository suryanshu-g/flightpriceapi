pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Repository checked out successfully'
            }
        }

        stage('Project Structure') {
            steps {
                sh 'ls -la'
            }
        }

        stage('Verify Python Files') {
            steps {
                sh 'test -f app.py && echo "app.py found"'
                sh 'test -f train_model.py && echo "train_model.py found"'
            }
        }

    }
}
