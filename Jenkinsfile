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
        echo 'Running unit tests'
        script {
          sh 'pipenv run py.test --junitxml=reports/tests.xml --cov=helcim tests/'
        }

      }
    }
    stage('Reporting') {
      steps {
        echo 'Generating report'
        script {
          sh 'pipenv run coverage xml'
        }
      }
    }
  }
  post {
    always {
      step([$class: 'CoberturaPublisher', coberturaReportFile: 'reports/coverage.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 10, onlyStable: false, sourceEncoding: 'ASCII'])
      junit 'reports/tests.xml'
    }
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
}