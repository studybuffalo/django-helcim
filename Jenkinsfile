pipeline {
  agent { dockerfile true }
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
          sh 'pipenv install --dev --deploy --system --ignore-pipfile'
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
