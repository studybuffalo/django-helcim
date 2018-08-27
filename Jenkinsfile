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
          sh 'pipenv run py.test --cov=helcim tests/'
        }

      }
    }
    stage('Reporting') {
      steps {
        echo 'Generating coverage report'
        script {
          sh 'pipenv run coverage xml'
        }
      }
    }
    post {
        always {
            step([$class: 'CoberturaPublisher', autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'reports/coverage.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
        }
    }
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
}