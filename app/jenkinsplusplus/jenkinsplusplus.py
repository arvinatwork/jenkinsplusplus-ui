import os
import jenkins
import requests
from requests.auth import HTTPBasicAuth

""" Default API urls """
Q_INFO = 'queue/api/json?depth=0'

""" JenkinsPlusPlus Custom Urls """
COMPUTERS_URL = 'computer/api/json'
BUILD_DURATION_INFO = '{build_url}/api/json?tree=timestamp,estimatedDuration,fullDisplayName,building,url'
BUILDS_ONGOING= 'computer/api/json?tree=computer[executors[currentExecutable[*]]]'
LABEL_NODES = 'label/{label_name}/api/json'
COMPUTER_INFO = 'computer/{label_name}/api/json'


class JenkinsPlusPlus:

    def __init__(self, url, user, token):
        self.base_url = url
        # Use this for the python-jenkins api calls
        self.orig_api = jenkins.Jenkins(url, username=user, password=token)

        if user is not None and token is not None:
            self.auth = HTTPBasicAuth(user.encode('utf-8'), token.encode('utf-8'))

    def get_computers(self):
        url = self._build_url(COMPUTERS_URL)
        response = self._request(url)

        return {'computer': response['computer']}

    def get_ongoing_builds(self):
        url = self._build_url(BUILDS_ONGOING)
        response = self._request(url)

        return response['computer']

    def get_build_duration_info(self, build_url):
        url = BUILD_DURATION_INFO.format(build_url=build_url)
        response = self._request(url)

        return response

    def get_nodes(self, label):
        label_uri = LABEL_NODES.format(label_name=label)
        url = self._build_url(label_uri)
        response = self._request(url)

        return response['nodes']

    def get_node_info(self, name):
        computer_uri = COMPUTER_INFO.format(label_name=name)
        url = self._build_url(computer_uri)
        response = self._request(url)

        return response

    def get_job(self, build_url):
        job_url = f'{build_url}/api/json'
        url = self._build_url(job_url)
        response = self._request(url)

        return response

    def get_queue_info(self):
        url = self._build_url(Q_INFO)
        response = self._request(url)

        return response['items']

    def _build_url(self, path):
        return f'{self.base_url}{path}'

    def _request(self, url):
        # TODO add exception handling

        response = requests.get(url, auth=self.auth)
        return response.json()


if __name__ == '__main__':
    JENKINS_URL = os.environ['JENKINS_URL']
    JENKINS_USER = os.environ['JENKINS_USER']
    JENKINS_TOKEN = os.environ['JENKINS_TOKEN']

    jpp = JenkinsPlusPlus(JENKINS_URL, JENKINS_USER, JENKINS_TOKEN)
    print(jpp.orig_api.get_whoami())
    print(jpp.get_ongoing_builds())
