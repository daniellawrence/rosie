# fqdn of the remote puppetdb server that we will be connecting
# to in order to gather data.
PUPPETDB_SERVER = 'puppet'

# Prefix of all your local facts, that contain the interesting information
# The facts we will be looking for will then be the following:
# - <FACT_PREFIX><APPLICATION_NAME>_deploy_date
# - <FACT_PREFIX><APPLICATION_NAME>_version
# - <FACT_PREFIX>environment
FACT_PREFIX = 'mhs_'
