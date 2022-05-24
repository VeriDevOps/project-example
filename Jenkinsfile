ISSUE_SECURITY_LABEL = 'SECURITY'
ISSUE_NON_SECURITY_LABEL = 'NON-SECURITY'
SEND_STIG_SUGGESTIONS_TO_RQCODE = true
ARQAN_CLASSIFICATION_API_ENDPOINT = "http://51.178.12.108:8000"
VDO_PATTERNS_REPO = [owner: "anaumchev", name: "VDO-Patterns", url: "https://github.com/anaumchev/VDO-Patterns.git"]

//General variables
def issueUrl = ""
def issueTitle = ""
def issueBody = ""

//Workflow 1 related variables
def issueTitleClassificationResult
def issueBodyClassificationResult
def issueLabel

//Workflow 2 related variables
def stigList = []
def commentStigs = ''

//Workflow 3 related variables
def testList = []
def commentTests = ''
def missingTestList = []


pipeline {
  agent any
  triggers {
    GenericTrigger(
    // the workflow is triggered on issue opening/closing/editing/reopening
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
        anyOf{
            triggeredBy cause: 'UserIdCause'
            expression {
                env.issueUrl != 'noUrl' && env.action ==~ /(opened|reopened|edited)/
            }
        }
      }
      stages {
        stage('Extract body and title from the issue') {
            when {
                anyOf{
                    triggeredBy cause: 'UserIdCause'
                    expression {
                        env.issueUrl != 'noUrl' && env.action ==~ /(opened|reopened|edited)/
                    }
                }
            }
            steps{
                script {
                    issueUrl = env.issueUrl
                    def issue = sh(script: "curl -s $issueUrl", returnStdout: true).trim()
                    def responseObject = readJSON text: issue
                    issueTitle = "$responseObject.title" ?: error('Could not extract issue title')
                    issueBody = "$responseObject.body" ?: error('Could not extract issue body')
                }
            }
        }
        stage('Send request to ARQAN classification API') {
            steps {
                script {
                    issueBodyClassificationResult = ArqanClassificationApi("$issueBody")
                    issueTitleClassificationResult = ArqanClassificationApi("$issueTitle")
                }
            }
        }
        stage('Determine label value') {
            steps {
                script {
                    issueLabel = ISSUE_SECURITY_LABEL
                    if (issueBodyClassificationResult == null && issueTitleClassificationResult == null){
                        error('Issue title and Issue body were not processed successfully')
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
                        httpRequest (consoleLogResponseBody: true,
                            customHeaders: [[name: 'Accept', value: 'application/vnd.github.v3+json'],
                                            [name: 'Authorization', value: "token $TOKEN", maskValue: true]],
                            httpMode: 'POST',
                            requestBody: """{"labels": ["$issueLabel"]}""",
                            url: "$issueUrl/labels",
                            validResponseCodes: '200'
                        )
                    }
                }
            }
        }
      }
    }
    
    stage ('Jenkins Workflow 2') {
        when {
            allOf{
                // if the issue is not related to security
                // STIGs and tests suggestion stages should be skipped
                expression {
                    issueLabel == ISSUE_SECURITY_LABEL
                }
                anyOf{
                    triggeredBy cause: 'UserIdCause'
                    expression {
                        env.issueUrl != 'noUrl' && env.action ==~ /(opened|edited)/
                    }
                }
            }
        }
        stages {
            stage('Initialize docker'){
                steps{
                    script{
                        def dockerHome = tool 'myDocker'
                        env.PATH = "${dockerHome}/bin:/usr/bin:${env.PATH}"
                    }
                }
            }
            stage ('Get STIGs suggestions for the issue') {
                agent {
                    docker {
                    image 'python:3'
                    reuseNode true
                    }
                }
                steps{
                    script {
                        sh 'pip install -r requirements.txt'
                        def stigListJsonString = sh (script: 'python ARQAN_suggestion_API_emulation.py', returnStdout: true).trim()
                        stigList = new groovy.json.JsonSlurper().parseText(stigListJsonString).result_stigs
                    }
                }
            }
            stage ('Generate a comment with STIGs suggestion for the issue') {
                steps{
                    script {
                        if (stigList.size()>0) {
                            commentStigs = "Suggested STIGs:\\n"
                            def matcher = /https:\/\/www.stigviewer.com\/stig\/(.*)\/finding\/(.*)/                        
                            for (link in stigList) {
                                def stigName = (link =~ matcher)[0][-1]
                                commentStigs = commentStigs + """\\r\\n- [$stigName]($link)"""
                            }
                        }
                        else {
                            commentStigs = 'No STIGs found for the issue'
                        }
                    }
                }
            }
            stage ('Post a comment with STIGs suggestion for the issue') {
                steps{
                    script {
                        withCredentials([string(credentialsId: 'personal-token-github', variable: 'TOKEN')]) {
                            httpRequest (consoleLogResponseBody: true,
                                customHeaders: [[name: 'Accept', value: 'application/vnd.github.v3+json'],
                                                [name: 'Authorization', value: "token $TOKEN", maskValue: true]],
                                httpMode: 'POST',
                                requestBody: """{"body": "$commentStigs"}""",
                                url: "$issueUrl/comments",
                                validResponseCodes: '201'
                            )
                        }
                    }
                }
            }
        }
    }
    stage ('Jenkins Workflow 3') {
        when {
            allOf{
                // if the issue is not related to security
                // STIGs and tests suggestion stages should be skipped
                expression {
                    stigList.size()>0
                }
                anyOf{
                    triggeredBy cause: 'UserIdCause'
                    expression {
                        env.issueUrl != 'noUrl' && env.action ==~ /(opened|edited)/
                    }
                }
            }
        }
        stages {
            stage('Initialize - clone VDO-patterns repo'){
                steps{
                    script{
                        git url: "$VDO_PATTERNS_REPO.url"
                    }
                }
            }
            stage('Get tests suggestion for the issue') {
                steps{
                    script {
                        sh "ls"
                        dir ('src/rqcode/stigs') {
                            def matcher = /https:\/\/www.stigviewer.com\/stig\/(.*)\/finding\/(.*)/
                            sh "ls"
                            sh "pwd"
                            for (link in stigList) {
                                def stigName = (link =~ matcher)[0][-1].replace('-','_')
                                println(stigName)
                                def test = sh(script: "find . -type d -name $stigName", returnStdout: true).trim()
                                println(test)
                                if (test && test ==~ /\.\/.*\/V_[0-9]+/) {
                                    testList.add(test.substring(2))
                                }
                                else {
                                    missingTestList.add([link: "$link", name: "$stigName"])
                                }
                            }
                        }
                        print(missingTestList)
                        print(testList)
                    }
                }
            }
            stage('Generate a comment with tests suggestion for the issue') {
                steps{
                    script {
                        if (testList.size()>0) {
                            commentTests = "Suggested tests from VDO-Patterns:\\n"
                            def matcher = /(.*)\/(.*)/                     
                            for (test in testList) {
                                def testName = (test =~ matcher)[0][-1]
                                def testLink = "https://github.com/$VDO_PATTERNS_REPO.owner/$VDO_PATTERNS_REPO.name/tree/master/src/rqcode/stigs/" + test
                                commentTests = commentTests + """\\r\\n- [$testName]($testLink)"""
                            }
                        }
                        else {
                            commentTests = 'No RQCODE tests found for the issue'
                        }
                    }
                }
            }
            stage ('Post a comment with RQCODE tests suggestion for the issue') {
                steps{
                    script {
                        withCredentials([string(credentialsId: 'personal-token-github', variable: 'TOKEN')]) {
                            httpRequest (consoleLogResponseBody: true,
                                customHeaders: [[name: 'Accept', value: 'application/vnd.github.v3+json'],
                                                [name: 'Authorization', value: "token $TOKEN", maskValue: true]],
                                httpMode: 'POST',
                                requestBody: """{"body": "$commentTests"}""",
                                url: "$issueUrl/comments",
                                validResponseCodes: '201'
                            )
                        }
                    }
                }
            }
            stage ('Post an issue with tests implementation suggestions for RQCODE') {
                when {
                    expression {
                        SEND_STIG_SUGGESTIONS_TO_RQCODE
                    }
                }
                steps{
                    script {
                        for (test in missingTestList) {
                            withCredentials([string(credentialsId: 'personal-token-github', variable: 'TOKEN')]) {
                                httpRequest (consoleLogResponseBody: true,
                                    customHeaders: [[name: 'Accept', value: 'application/vnd.github.v3+json'],
                                                    [name: 'Authorization', value: "token $TOKEN", maskValue: true]],
                                    httpMode: 'POST',
                                    requestBody: """{"title":"STIG implementation ($test.name)","body":"STIG [$test.name]($test.link) is not implemented yet","assignees":["$VDO_PATTERNS_REPO.owner"],"labels":["STIG suggestion"]}""",
                                    url: "https://api.github.com/repos/$VDO_PATTERNS_REPO.owner/$VDO_PATTERNS_REPO.name/issues",
                                    validResponseCodes: '201'
                                )
                            }
                        }
                    }
                }
            }
        }
    }
  }
}

String ArqanClassificationApi (String textInput) {
    def response
    try {
        response = httpRequest (consoleLogResponseBody: true,
                            contentType: 'TEXT_PLAIN',
                            httpMode: 'POST',
                            requestBody: textInput,
                            url: "$ARQAN_CLASSIFICATION_API_ENDPOINT/text",
                            validResponseCodes: '200'
                        )
    }
    catch (err) {
        echo err.getMessage()
        return null
    }

    def jsonResponse = new groovy.json.JsonSlurper().parseText(response.getContent())
    println(jsonResponse.security_text)
    return jsonResponse.security_text
}