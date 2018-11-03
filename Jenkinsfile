pipeline {
  agent {
    docker { image 'python:3.6.7-alpine' }
  }
  options {
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '10'))
    timeout(time: 1, unit: 'HOURS')
  }
  stages {
    stage('Build') {
      steps {
        echo 'Setup virtual environment'
        script {
          sh 'pip install pipenv'
          sh 'apk add python-dev jpeg-dev zlib-dev'
          sh 'pipenv install --dev --ignore-pipfile'
        }
      }
    }
  }
}
