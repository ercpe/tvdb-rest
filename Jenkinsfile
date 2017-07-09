node {
	try {
		checkout scm
		updateGitlabCommitStatus name: 'jenkins', state: 'running'

		docker.withRegistry('https://registry.docks.ercpe.de', 'docker-registry') {
			docker.image('python:3.4').inside {
				stage("Install dependencies") {
					sh "make install_deps"
				}

				stage("Compile") {
					sh "make compile compile_optimized"
				}

				stage("Run tests") {
					sh "make test"
				}

				stage("Run coverage") {
					sh "make coverage"
				}

				stage("Run pylint") {
					sh "pylint -r n --msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}' > pylint-report.txt || true"
				}
			}

			withCredentials([[
				$class: 'UsernamePasswordMultiBinding',
				credentialsId: 'sonar',
				usernameVariable: 'USERNAME',
				passwordVariable: 'PASSWORD']]) {

				docker.image('ercpe/sonar-scanner:latest').inside {
					stage("Run sonar-scanner") {
						sh "sonar-scanner -Dsonar.host.url=${SONAR_HOST} -Dsonar.login=${USERNAME} -Dsonar.password=${PASSWORD}"
					}
				}
			}
		}

		updateGitlabCommitStatus name: 'jenkins', state: 'success'
	} catch (e) {
    	currentBuild.result = "FAILED"
		updateGitlabCommitStatus name: 'jenkins', state: 'failed'
    	notifyFailedBuild()
    	throw e
	}
}

def notifyFailedBuild() {
  emailext (
      subject: "FAILED: ${env.JOB_NAME} [${env.BUILD_NUMBER}]",
      body: """Job ${env.JOB_NAME} [${env.BUILD_NUMBER}] has FAILED: ${env.BUILD_URL}""",
      recipientProviders: [[$class: 'CulpritsRecipientProvider']]
    )
}
