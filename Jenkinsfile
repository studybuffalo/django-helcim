pipeline {
  agent {
    docker { image 'ubuntu:16.04' }
  }
  options {
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '10'))
    timeout(time: 60, unit: 'MINUTES')
  }
  stages {
    stage('Build') {
      steps {
        echo 'Setup virtual environment'
        script {
          sh 'apt-get update'
          sh 'add-apt-repository ppa:deadsnakes/ppa'
          sh 'apt-get update'
          sh 'apt-get install python3.4 python3.5 python3.6 python3.7'
          sh 'pip install pipenv'
          sh 'pipenv install --dev --ignore-pipfile'
        }
      }
    }
    stage('Test') {
      steps {
        echo 'Running tests'
        script {
          sh 'pipenv run tox'
        }

      }
    }
    stage('Security') {
      steps {
        echo 'Running security checks'
        script {
          sh 'pipenv check'
        }
      }
    }
  }
  post {
    always {
      step([$class: 'CoberturaPublisher', coberturaReportFile: 'reports/coverage.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 10, onlyStable: false, sourceEncoding: 'ASCII'])
      junit 'reports/tests.*.xml'
    }
  }
}
