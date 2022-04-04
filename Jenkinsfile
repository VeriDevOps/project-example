pipeline  {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building..'
                echo sh(returnStdout: true, script: 'env')
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}

