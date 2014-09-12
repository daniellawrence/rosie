#!/usr/bin/env python
"""
Upgrade the rosie

To deploy the rosie to the systest enviroment run:

 $ fab-rosie -R systest deploy

"""
from fabric.api import env, local, sudo, cd, settings, puts, task, lcd
from fabric.context_managers import show
from fabric.operations import put
from mhs.fab.virtualenv import virtualenv, mkvirtualenv
from mhs.fab.pip import pip_install
from mhs.fab import services
from mhs.fab import website
from mhs.fab.common import tell_hipchat

PROJECT_NAME = 'rosie'
FILE_FORMAT = "{1}-{0}"

env.roledefs.update({
    'systest': ['rosie.f2l.info'],
})

application_home = "/opt/rosie/current"
roles = None
env.sudo_user = "rosie"


def deploy_app(version=None):
    """Deploy then new version can take version number (default is latest git
    version)
    """
    if isinstance(version, list):
        version = version[0]

    version = release(version)
    filename = FILE_FORMAT.format(version, PROJECT_NAME) + '.tar.gz'
    assert len(env.roles) == 1

    sudo("mkdir -p /opt/rosie", user='root')
    with settings(sudo_user=None):
        sudo("chown rosie:rosie /opt/rosie")

    puts("sending '%s' to remote server" % filename)
    put(filename)

    with cd("/opt/rosie"):
        sudo("tar -xzf /home/$SUDO_USER/" + filename)
        sudo("ln -sfn " + FILE_FORMAT.format(
            version, PROJECT_NAME) + " current")
        with settings(sudo_user=None):
            sudo("chown -R rosie:rosie " +
                 FILE_FORMAT.format(version, PROJECT_NAME))


def release(version=None):
    """Create the tar file from the git, can take version number
    (default is latest git version) """
    # version = version or local('git describe --abbrev=1', capture=True)

    version = version or local('git rev-parse HEAD', capture=True)
    print("release version='%s'" % version)
    local(('git archive  --format=tar --prefix={1}-{0}/ {0} | gzip '
           ' >' + FILE_FORMAT + '.tar.gz').format(version, PROJECT_NAME))

    return version


def cleanup():
    """Delete local release tar files"""
    local('rm -rf {0}-*.tar.gz'.format(PROJECT_NAME))


@task
def deploy(version=''):
    "Deploy the application"
    if version == '':
        version = None

    # Deploy a new version of the application
    with show('debug'):
        deploy_app(version)

    # create the venv and install the neede pip libs
    with cd(application_home):
        puts("Create a new virtualenv at %s" % application_home)
        mkvirtualenv(application_home)
        with virtualenv(application_home):
            pip_install("%s/requirements.txt" % application_home)

    # Stop the service before trying to upgrade the service
    services.upstart_stop('rosie')
    # Start services
    services.upstart_start('rosie')

    # Check service
    website.check_host_website()

    # tell hipchat about this deploy
    tell_hipchat("rosie has been updated to version %s" % version)


def main():
    from common import main
    main(__file__)

if __name__ == '__main__':
    from fabric.main import main as fabric_main
    fabric_main(fabfile_locations=[__file__])
