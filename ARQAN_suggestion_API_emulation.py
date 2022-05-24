import requests
import json
from bs4 import BeautifulSoup
import random

def main():
    #parse all STIGs links
    r = requests.get('https://www.stigviewer.com/stigs')
    soup = BeautifulSoup(r.text, 'html.parser')
    stig_links = []
    for link in soup.find_all('a'):
        if link.get('href') and "/stig/" in link.get('href'):
            stig_links.append("https://www.stigviewer.com"+link.get('href').strip())

    #pick a random STIG (emulation, should not be random)
    stig = random.choice(stig_links)
    r = requests.get(stig)
    #get all findings list for this STIG
    soup = BeautifulSoup(r.text, 'html.parser')
    finding_links = []
    for link in soup.find_all('a'):
        if link.get('href') and "/finding/" in link.get('href'):
            finding_links.append("https://www.stigviewer.com"+link.get('href').strip())

    #pick 2 random findings and a predefined finding to construct a result
    V_214961 = "https://www.stigviewer.com/stig/canonical_ubuntu_16.04_lts/2020-12-09/finding/V-214961"
    result_stigs = [random.choice(finding_links) for i in range(2)] + [V_214961]

    #generate a HTTP response to emulate a behavior of an API server
    response = requests.models.Response()
    response.headers = {'Content-Type': 'application/json'}
    response.status_code = 200
    data = {}
    data["result_stigs"] = result_stigs
    response._content = json.dumps(data).encode('UTF-8')

    print(response.text)

if __name__ == "__main__":
    main()