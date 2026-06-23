:::writing{variant="document" id="42817"}
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
                bat 'dir'
            }
        }

        stage('Verify Python Files') {
            steps {
                bat 'if exist app.py (echo app.py found)'
                bat 'if exist train_model.py (echo train_model.py found)'
            }
        }

    }
}
:::
