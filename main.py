#!/usr/bin/env python
from flask import Flask, render_template
import pypuppetdb
import datetime

app = Flask(__name__)
pdb = pypuppetdb.connect(host='puppet')
FACT_PREFIX = "mhs"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/deployments/")
def application_list():
    application_list = []

    for factname in pdb.fact_names():

        if not factname.startswith('mhs_'):
            continue
        if not factname.endswith('_deploy_date'):
            continue

        app_name = factname.replace('mhs_', '')
        app_name = app_name.replace('_deploy_date', '')
        application_list.append(app_name)

    return render_template(
        "application_list.html",
        {
            'application_list': application_list,
        }
    )


@app.route("/deployments/<application_name>/")
def deployment(application_name):
    deployment_date_fact = 'mhs_%s_deploy_date' % application_name
    deployment_version_fact = 'mhs_%s_version' % application_name
    nodes = {}
    current_date = now()

    clean_up_map = (
        # (deployment_date_fact, 'deployment_date'),
        (deployment_version_fact, 'deployment_version'),
    )

    for fact in pdb.facts(deployment_date_fact):
        facts = {}
        node_name = fact.node
        environment_name = 'unknown'
        for nf in pdb.node(node_name).facts():
            node_fact_name = nf.name
            node_fact_value = nf.value
            facts[node_fact_name] = node_fact_value

        if 'mhs_environment' in facts:
            environment_name = facts['mhs_environment']

        # clean up the facts to what we want to use.
        for dirty, clean in clean_up_map:
            facts[clean] = facts[dirty]

        deployment_date = strptime(
            facts[deployment_date_fact],
            '%Y-%m-%d %H:%M:%S'
        )
        facts['deployment_date'] = deployment_date

        # work out how long ago the deployment was
        deployment_days_ago = (current_date - deployment_date).days
        facts['deployment_days_ago'] = deployment_days_ago

        # If we have an mhs_webservers fact, then turn it into a list
        # as we do not want to play around with a csv
        if 'mhs_webservers' in facts:
            facts['mhs_webservers'] = facts['mhs_webservers'].split(',')

        nodes[environment_name] = facts

    return render_template(
        "home.html",
        {
            'nodes': nodes,
            'application_name': application_name,
            'deployment_date_fact': deployment_date_fact,
            'deployment_version_fact': deployment_version_fact
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
