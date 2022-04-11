/*
 * curl -X POST -H "Content-Type: application/json" -H "headerWithNumber: nbr123" -H "headerWithString: a b c" -d '{ "before": "1848f12", "after": "5cab1", "ref": "refs/heads/develop" }' -vs http://admin:admin@localhost:8080/jenkins/generic-webhook-trigger/invoke?requestWithNumber=nbr%20123\&requestWithString=a%20string
 */
node {
 properties([
  pipelineTriggers([
   [$class: 'GenericTrigger',
    genericVariables: [
     [key: 'action', value: '$.action'],
     [
      key: 'issue_url',
      value: '$.issue.url',
      defaultValue: 'not_an_issue'
     ]
    ]
   ]
  ])
 ])
if(issue_url != 'not_an_issue' && action ==~ /(opened|reopened|edited)/) {
 stage("Extract body and title from issue") {
  script {
    final String response = sh(script: "curl -s $issue_url", returnStdout: true).trim()
    def responseObject = readJSON text: response
    def issue_title = "$responseObject.title"
    def issue_body = "$responseObject.body"
    println("issue_title:  $issue_title")
    println("issue_body:  $issue_body")
    final String response_body = sh(script: "curl -X POST -H 'Content-Type: text/plain' --data \$'$issue_body' 51.178.12.108:8000/text", returnStdout: true).trim()
    final String response_title = sh(script: "curl -X POST -H 'Content-Type: text/plain' --data \$'$issue_title' 51.178.12.108:8000/text", returnStdout: true).trim()

    def responseObject_body = readJSON text: response_body
    // def responseObject_title = readJSON text: response_title
    // def security_text_title = "$responseObject_title.security_text"
    def security_text_body = "$responseObject_body.security_text"
    def issue_label = "Security JENKINS"
    // if (security_text_body == [] && security_text_title == []){
    //     issue_label = "Non-security JENKINS"
    // }
    if (security_text_body == []) {
        issue_label = "Non-security JENKINS"
    }
    withCredentials([string(credentialsId: 'personal-token-github', variable: 'TOKEN')]) {
        final String response_label = sh(script: "curl -X POST -H 'Accept: application/vnd.github.v3+json' -H \"authToken: $TOKEN\" https://api.github.com/repos/VeriDevOps/project-example/issues/2/labels -d '{\"labels\" : [$issue_label]}'")
        println(response_label)
    }
}
}
}
}