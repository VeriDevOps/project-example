// def String ISSUE_SECURITY_LABEL = "SECURITY"
// def String ISSUE_NON_SECURITY_LABEL = "NON-SECURITY"
// def String ARQAN_CLASSIFICATION_API_ENDPOINT = "51.178.12.108:8000"
def issueTitle
def issueBody

pipeline {
  agent any
  triggers {
    GenericTrigger(
     genericVariables: [
      [key: 'action', value: '$.action'],
      [key: 'issueUrl', value: '$.issue.url', defaultValue: null]
     ],

     causeString: 'Triggered on $.action',

     printContributedVariables: true,
     printPostContent: true,

     silentResponse: false,
    )
  }
  stages {
    stage('Start workflow') {
      when {
        expression {
            issueUrl && action ==~ /(opened|reopened|edited)/
        }
      }
      stages {
        stage('Extract body and title from the issue') {
            script {
                final String issueUrl = sh(script: "curl -s $issueUrl", returnStdout: true).trim()
                def responseObject = readJSON text: issueUrl
                issueTitle = "$responseObject.title" ?: error "Could not extract issue title"
                issueBody = "$responseObject.body" ?: error "Could not extract issue body"
                println("issueTitle:  $issueTitle")
                println("issueBody:  $issueBody")
            }
        }
        stage('Send request to ARQAN classification API') {
            script {
                final String responseBodyClassification = sh(script: "curl -X POST -H 'Content-Type: text/plain' --data \$'$issue_body' 51.178.12.108:8000/text", returnStdout: true).trim() ?: error "Issue body classification failed"
                final String responseTitleClassification = sh(script: "curl -X POST -H 'Content-Type: text/plain' --data \$'$issue_title' 51.178.12.108:8000/text", returnStdout: true).trim() ?: error "Issue title classification failed"

                def responseObject_body = readJSON text: responseBodyClassification
                def responseObject_title = readJSON text: responseTitleClassification

                def security_text_title = "$responseObject_title.security_text"
                def security_text_body = "$responseObject_body.security_text"

                def issue_label = "Security JENKINS"
                if (security_text_body == [] && security_text_title == []){
                    issue_label = "Non-security JENKINS"
                }

                println(issue_label)
            }
        }
      }
    }
  }
}
