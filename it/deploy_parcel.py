# https://cloudera.github.io/cm_api/docs/python-client/

import time

from cm_api.api_client import ApiResource
api = ApiResource('10.17.28.101', 7180, 'tandem', 'tandem')

parcel_repo = 'http://10.17.221.20/spark/deploy/'
cm_config = api.get_cloudera_manager().get_config(view='full')
repo_config = cm_config['REMOTE_PARCEL_REPO_URLS']
value = repo_config.value or repo_config.default
# value is a comma-separated list
value += ',' + parcel_repo
api.get_cloudera_manager().update_config({
  'REMOTE_PARCEL_REPO_URLS': value})
# wait to make sure parcels are refreshed
time.sleep(10)

# replace cluster_name with the name of your cluster
cluster_name = 'cluster'
cluster = api.get_cluster(cluster_name)
# replace parcel_version with the specific parcel version you want to install
# After adding your parcel repository to CM, you can use the API to list all parcels and get the precise version string by inspecting:
# cluster.get_all_parcels() or looking at the URL http://<cm_host>:7180/api/v5/clusters/<cluster_name>/parcels/
parcel_version = '2.1.0-cdh5.4.3.d20161220-10.41.53-550d4e9e1eae5de500651761ea3b89ec1be54b1a'
parcel = cluster.get_parcel('YSPARK', parcel_version)
parcel.start_download()
# unlike other commands, check progress by looking at parcel stage and status
while True:
  parcel = cluster.get_parcel('YSPARK', parcel_version)
  if parcel.stage == 'DOWNLOADED':
    break
  if parcel.state.errors:
    # raise Exception(str(parcel.state.errors))
    print(str(parcel.state.errors))
  print "progress: %s / %s" % (parcel.state.progress, parcel.state.totalProgress)
  time.sleep(15) # check again in 15 seconds

print "downloaded CDH parcel version %s on cluster %s" % (parcel_version, cluster_name)

parcel.start_distribution()
while True:
  parcel = cluster.get_parcel('YSPARK', parcel_version)
  if parcel.stage == 'DISTRIBUTED':
    break
  if parcel.state.errors:
    # raise Exception(str(parcel.state.errors))
    print(str(parcel.state.errors))
  print "progress: %s / %s" % (parcel.state.progress, parcel.state.totalProgress)
  time.sleep(15) # check again in 15 seconds

print "distributed CDH parcel version %s on cluster %s" % (parcel_version, cluster_name)

parcel.activate()

# http://10.17.28.101:7180/api/v5/clusters/cluster/parcels/
