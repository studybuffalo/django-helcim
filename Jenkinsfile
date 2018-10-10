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
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
}