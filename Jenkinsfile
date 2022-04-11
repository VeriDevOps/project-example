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
 stage("Set label to security-related GitHub issue") {
  script {
    final String response = sh(script: "curl -s $issue_url", returnStdout: true).trim()
    def responseObject = readJSON text: response
    def issue_title = "$responseObject.title"
    def issue_body = "$responseObject.body"
    println("issue_title:  $issue_title")
    println("issue_body:  $issue_body")
  }
 }
}
}