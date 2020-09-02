import os
import humanfriendly

from flask import Flask
from flask import render_template
from flask_cors import CORS
from datetime import datetime
from datetime import timedelta

from .jenkinsplusplus import JenkinsPlusPlus

app = Flask(__name__)
CORS(app)

JENKINS_URL = os.environ['JENKINS_URL']
JENKINS_USER = os.environ['JENKINS_USER']
JENKINS_TOKEN = os.environ['JENKINS_TOKEN']

# TODO Extract all of this


class Node:
    def __init__(self, node_json):
        self.name = node_json['displayName']
        self.description = node_json['description']
        self.offline = node_json['offline']
        self.labels = self.__get_labels(node_json['assignedLabels'])

    @staticmethod
    def __get_labels(assigned_labels):
        labels = list(map(lambda label: label['name'], assigned_labels))
        return labels


def get_all_labels(computers):
    labels = {}

    for node_data in computers:
        node = Node(node_data)

        for label_name in node.labels:
            if label_name == node.name:
                continue

            if label_name not in labels.keys():
                labels[label_name] = 1
            else:
                labels[label_name] = labels[label_name] + 1

    sorted_labels = dict(sorted(labels.items(), key=lambda x: x[0].casefold()))
    return sorted_labels


def get_build_urls(computers):
    active_computers = []

    for computer in computers:
        not_null_executor = list(filter(lambda ex: ex['currentExecutable'] is not None, computer['executors']))
        not_null_one_off_executor = list(filter(lambda ex: ex['currentExecutable'] is not None, computer['oneOffExecutors']))

        if not_null_executor:
            active_computers.extend(not_null_executor)
        if not_null_one_off_executor:
            active_computers.extend(not_null_one_off_executor)

    build_urls = list(map(lambda cmp: {'url': cmp['currentExecutable']['url']}, active_computers))

    # TODO optimize
    urls = []
    for url in build_urls:
        urls.append(url['url'])

    return urls


def get_build_durations_info(computers):
    active_computers = []

    for computer in computers:
        not_null_executor = list(filter(lambda ex: ex['currentExecutable'] is not None, computer['executors']))
        if not_null_executor:
            active_computers.extend(not_null_executor)

    builds = list(map(lambda cmp: cmp['currentExecutable'], active_computers))
    return builds


def query_builds():
    server = JenkinsPlusPlus(JENKINS_URL, JENKINS_USER, JENKINS_TOKEN)
    computers = server.get_ongoing_builds()

    builds = get_build_durations_info(computers)

    now = datetime.now()
    now_timestamp = datetime.timestamp(now) * 1000

    build_durations = []
    for build_info in builds:
        duration = now_timestamp - build_info['timestamp']
        duration_display = timedelta(milliseconds=duration)
        human_friendly_duration = humanfriendly.format_timespan(duration_display)

        build_data = {
            'name': build_info['fullDisplayName'],
            'url': build_info['url'],
            'duration': duration,
            'duration_display': human_friendly_duration
        }

        build_durations.append(build_data)

    sorted_build_durations = sorted(build_durations, key=lambda i: i['duration'], reverse=True)

    return sorted_build_durations


def query_labels():
    server = JenkinsPlusPlus(JENKINS_URL, JENKINS_USER, JENKINS_TOKEN)
    nodes_data = server.get_computers()
    computers = nodes_data['computer']
    labels = get_all_labels(computers)
    links = []

    for name, count in labels.items():
        data = {
            'name': name,
            'link': f'{JENKINS_URL}/label/{name}/',
            'count': count
        }
        links.append(data)

    return links


def query_queue():
    server = JenkinsPlusPlus(JENKINS_URL, JENKINS_USER, JENKINS_TOKEN)
    jobs_in_queue = server.get_queue_info()

    now = datetime.now()
    now_timestamp = datetime.timestamp(now) * 1000

    queue_durations = []
    for job_info in jobs_in_queue:
        duration = now_timestamp - job_info['inQueueSince']
        duration_display = timedelta(milliseconds=duration)
        human_friendly_duration = humanfriendly.format_timespan(duration_display)

        build_data = {
            'why': job_info['why'],
            'url': "#",
            'duration': duration,
            'duration_display': human_friendly_duration
        }

        queue_durations.append(build_data)

    sorted_queue_durations = sorted(queue_durations, key=lambda i: i['duration'], reverse=True)

    return sorted_queue_durations

#
# Routes
#


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/labels')
def get_labels():
    labels = query_labels()
    return render_template('labels.html', labels=labels)


@app.route('/builds')
def get_builds():
    build_durations = query_builds()
    return render_template('build_durations.html', items=build_durations)


@app.route('/queue')
def get_queue():
    queue_durations = query_queue()
    return render_template('queue_durations.html', items=queue_durations)


if __name__ == "__main__":
    app.run()
