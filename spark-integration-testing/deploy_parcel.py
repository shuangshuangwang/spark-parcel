# https://cloudera.github.io/cm_api/docs/python-client/

import time
import os
import datetime


from cm_api.api_client import ApiResource
api = ApiResource('10.17.28.101', 7180, 'tandem', 'tandem')

parcel_repo = 'http://10.17.221.20/spark/deploy/'
# parcel_version='2.1.0-cdh5.4.3.d20161221-14.28.51-550d4e9e1eae5de500651761ea3b89ec1be54b1a'
parcel_version = os.environ["PARCEL_VERSION"]
if '' == parcel_version:
  exit()

cm_config = api.get_cloudera_manager().get_config(view='full')
repo_config = cm_config['REMOTE_PARCEL_REPO_URLS']
value = repo_config.value or repo_config.default
# value is a comma-separated list
value += ',' + parcel_repo
api.get_cloudera_manager().update_config({'REMOTE_PARCEL_REPO_URLS': value})
# wait to make sure parcels are refreshed
time.sleep(10)

# replace cluster_name with the name of your cluster
cluster_name = 'cluster'
cluster = api.get_cluster(cluster_name)
# replace parcel_version with the specific parcel version you want to install
# After adding your parcel repository to CM, you can use the API to list all parcels and get the precise version string by inspecting:
# cluster.get_all_parcels() or looking at the URL http://<cm_host>:7180/api/v5/clusters/<cluster_name>/parcels/
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
  time.sleep(20) # check again in 15 seconds

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
  time.sleep(70) # check again in 15 seconds

print "distributed CDH parcel version %s on cluster %s" % (parcel_version, cluster_name)

parcel.activate()

while True:
  parcel = cluster.get_parcel('YSPARK', parcel_version)
  if parcel.stage == 'ACTIVATED':
    break
  if parcel.state.errors:
    # raise Exception(str(parcel.state.errors))
    print(str(parcel.state.errors))
  print "progress: %s / %s" % (parcel.state.progress, parcel.state.totalProgress)
  time.sleep(100) # check again in 15 seconds

deploy_parcel=os.readlink('/opt/cloudera/parcels/YSPARK')
if "YSPARK-" + parcel_version == deploy_parcel:
  print "activated YSPARK parcel version %s on cluster %s" % (parcel_version, cluster_name)
else:
  print('no')

cluster.get_service('spark_on_yarn').deploy_client_config()
if not cmd.wait(100).success:
  print "Failed to deploy client configs for {0}".format(cluster.name)

os.system('hdfs dfs -touchz /tmp/tandem/spark/it/' + datetime.datetime.now().strftime('%Y-%m-%d') + '/_SUCCESS')

# http://10.17.28.101:7180/api/v5/clusters/cluster/parcels/
