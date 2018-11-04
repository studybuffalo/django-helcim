pipeline {
  agent {
    docker { image 'ubuntu:16.04' }
  }
  options {
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '5'))
    timeout(time: 60, unit: 'MINUTES')
  }
  stages {
    stage('Build') {
      steps {
        echo 'Setup virtual environment'
        script {
          sh 'apt-get update'
          sh 'apt-get upgrade -y'
          sh 'apt-get install -y locales locales-all'
          sh 'export LANG C.UTF8'
          sh 'export LC_ALL C.UTF8'
          sh 'apt-get install -y software-properties-common'
          sh 'add-apt-repository ppa:deadsnakes/ppa'
          sh 'apt-get update'
          sh 'apt-get install -y python3.4 python3.5 python3.6 python3.7 python-pip'
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
