#!/usr/bin/env python
from flask import Flask, render_template, redirect
import pypuppetdb
import datetime
from settings import FACT_PREFIX, PUPPETDB_SERVER

app = Flask(__name__)
pdb = pypuppetdb.connect(host=PUPPETDB_SERVER)


@app.route("/")
def index():
    return redirect("/deployments/")


@app.route("/deployments/")
def application_list():
    application_list = []

    for factname in pdb.fact_names():

        # We are only interested in our apps
        if not factname.startswith(FACT_PREFIX):
            continue
        # Only care about facts that contain a deploy_date
        if not factname.endswith('_deploy_date'):
            continue

        app_name = factname.replace(FACT_PREFIX, '')
        app_name = app_name.replace('_deploy_date', '')
        application_list.append(app_name)

    return render_template(
        "application_list.html",
        application_list=application_list
    )


@app.route("/deployments/<application_name>/")
def deployment(application_name):
    deployment_date_fact = '%s%s_deploy_date' % (
        FACT_PREFIX, application_name
    )
    deployment_version_fact = '%s%s_version' % (
        FACT_PREFIX, application_name
    )
    nodes = {}
    current_date = datetime.datetime.now()

    clean_up_map = (
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

        # set the environment_name that will be used in templates
        if '%senvironment' % FACT_PREFIX in facts:
            environment_name = facts['%senvironment' % FACT_PREFIX]
        facts['environment'] = environment_name

        # clean up the facts to what we want to use.
        for dirty, clean in clean_up_map:
            facts[clean] = facts[dirty]

        # convert the deployment date into a timestamp for maths
        deployment_date = datetime.datetime.strptime(
            facts[deployment_date_fact],
            '%Y-%m-%d %H:%M:%S'
        )
        facts['deployment_date'] = deployment_date

        # work out how long ago the deployment was
        deployment_days_ago = (current_date - deployment_date).days
        facts['deployment_days_ago'] = deployment_days_ago

        # If we have an mhs_webservers fact, then turn it into a list
        # as we do not want to play around with a csv
        WEBSERVER_FACT = '%swebservers' % FACT_PREFIX
        node_uniq_key = environment_name
        if WEBSERVER_FACT in facts:
            node_uniq_key = facts[WEBSERVER_FACT]
            facts['webservers'] = facts[WEBSERVER_FACT].split(',')

            # Remove the fqdn from the webserver name, if we have another
            # name for the webserver
            if len(facts['webservers']) > 1 \
               and facts['fqdn'] in facts['webservers']:
                facts['webservers'].pop(
                    facts['webservers'].index(facts['fqdn'])
                )

        nodes[node_uniq_key] = facts

    return render_template(
        "deployment.html",
        nodes=nodes,
        application_name=application_name,
        deployment_date_fact=deployment_date_fact,
        deployment_version_fact=deployment_version_fact
    )


if __name__ == "__main__":
    app.run(debug=True)
