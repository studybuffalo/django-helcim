pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        echo 'Setup virtual environment'
        script {
          sh 'pipenv install --dev'
        }

      }
    }
    stage('Test') {
      steps {
        echo 'This is the Testing Stage'
        script {
          sh 'pipenv run pytest'
        }

      }
    }
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
}