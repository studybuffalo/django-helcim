pipeline {
  agent any
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
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
}
