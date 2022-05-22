def String ISSUE_SECURITY_LABEL = "SECURITY"
def String ISSUE_NON_SECURITY_LABEL = "NON-SECURITY"
// def String ARQAN_CLASSIFICATION_API_ENDPOINT = "51.178.12.108:8000"
def issueTitle
def issueBody

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
    stage('Start workflow') {
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
                    //final String responseBodyClassification = sh(script: "curl -X POST -H 'Content-Type: text/plain' --data \$'$issueBody' 51.178.12.108:8000/text", returnStdout: true).trim() ?: error("Issue body classification failed")
                    //final String responseTitleClassification = sh(script: "curl -X POST -H 'Content-Type: text/plain' --data \$'$issueTitle' 51.178.12.108:8000/text", returnStdout: true).trim() ?: error("Issue title classification failed")
                    

                    def responseBody = ArqanClassificationApi("$issueBody")
                    def responseTitle = ArqanClassificationApi("$issueTody")
                    def issueLabel = ISSUE_SECURITY_LABEL

                    if (responseBody == null && responseTitle == null){
                        error("Issue title and Issue body were not processed successfully")
                    }
                    else if (responseBody == [] && responseTitle == []){
                        issueLabel = ISSUE_NON_SECURITY_LABEL
                    }
                    println(issueLabel)
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
    def response = httpRequest (consoleLogResponseBody: true,
                        contentType: 'TEXT_PLAIN',
                        httpMode: 'POST',
                        requestBody: textInput,
                        url: "http://51.178.12.108:8000/text",
                        validResponseCodes: "100:599"
                    )
    
    if (response.status >= 400) {
        throw new Exception("The request could not be proceeded \n Error: \n + $response.content")
        return null
    }

    jsonResponse = readJSON text: response.content
    return "$jsonResponse.security_text"
}
