def String ISSUE_SECURITY_LABEL = "SECURITY"
def String ISSUE_NON_SECURITY_LABEL = "NON-SECURITY"
// def String ARQAN_CLASSIFICATION_API_ENDPOINT = "51.178.12.108:8000"
def issueTitle
def issueBody
def issueTitleClassificationResult
def issueBodyClassificationResult
def issueLabel

pipeline {
  agent any
  triggers {
    GenericTrigger(
     genericVariables: [
      [key: 'action', value: '$.action', defaultValue: 'noAction'],
      [key: 'issueUrl', value: '$.issue.url', defaultValue: 'noUrl']
     ],

     printContributedVariables: true,
     printPostContent: true,

     silentResponse: false,
    )
  }
  stages {
    stage('Jenkins Workflow 1') {
      when {
        beforeAgent true
        expression {
            issueUrl != 'noUrl' && action ==~ /(opened|reopened|edited)/
        }
      }
      stages {
        stage('Extract body and title from the issue') {
            steps{
                script {
                    final String issueUrl = sh(script: "curl -s $issueUrl", returnStdout: true).trim()
                    def responseObject = readJSON text: issueUrl
                    issueTitle = "$responseObject.title" ?: error("Could not extract issue title")
                    issueBody = "$responseObject.body" ?: error("Could not extract issue body")
                    println("issueTitle:  $issueTitle")
                    println("issueBody:  $issueBody")
                }
            }
        }
        stage('Send request to ARQAN classification API') {
            steps {
                script {
                    issueBodyClassificationResult = ArqanClassificationApi("$issueBody")
                    issueTitleClassificationResult = ArqanClassificationApi("$issueTitle")
                    println(issueBodyClassificationResult)
                }
            }
        }
        stage('Determine label value') {
            steps {
                script {
                    issueLabel = ISSUE_SECURITY_LABEL

                    if (issueBodyClassificationResult == null && issueTitleClassificationResult == null){
                        error("Issue title and Issue body were not processed successfully")
                    }
                    else if (issueBodyClassificationResult == [] && issueTitleClassificationResult == []){
                        issueLabel = ISSUE_NON_SECURITY_LABEL
                    }
                    println(issueLabel)
                }
            }
        }
        stage('Set label') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'personal-token-github', variable: 'TOKEN')]) {
                        final String response_label = sh(script: "curl -X POST -H 'Accept: application/vnd.github.v3+json' -H \"Authorization: token $TOKEN\" https://api.github.com/repos/VeriDevOps/project-example/issues/2/labels -d '{\"labels\" : [\"$issueLabel\"]}'")
                        println(response_label)
                    }
                }
            }
        }
      }
    }
  }
}

String ArqanClassificationApi (String textInput) {
    warnError(message: "ARQAN Classification API was not able to proceed the request") {
        def response = httpRequest (consoleLogResponseBody: true,
                            contentType: 'TEXT_PLAIN',
                            httpMode: 'POST',
                            requestBody: textInput,
                            url: "http://51.178.12.108:8000/text",
                            validResponseCodes: "100:399"
                        )
        if (response.status >= 400) {
            println(response.status)
            println(response.content.getClass())
            return null
        }
        println(response.content)
        println(response.content.getClass())
        jsonResponse = readJSON text: response.content
        println(jsonResponse + "\n" + "$jsonResponse.security_text")
        return $jsonResponse.security_text
    }
}
