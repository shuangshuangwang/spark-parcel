# https://cloudera.github.io/cm_api/docs/python-client/

import time
import os
import datetime

from cm_api.api_client import ApiResource
api = ApiResource('10.17.28.101', 7180, 'tandem', 'tandem')

parcel_repo = 'http://10.17.221.20/spark/deploy/'
# parcel_version='2.2.0-2.6.0.d20161221-21.43.18-5857b9ac2d9808d9b89a5b29620b5052e2beebf5'
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
time.sleep(60)

# replace cluster_name with the name of your cluster
cluster_name = 'cluster'
cluster = api.get_cluster(cluster_name)

# find the previously ACTIVATED YSPARK parcel
previously_activated_parcel = None
for p in cluster.get_all_parcels():
  if p.product == 'YSPARK' and (p.stage == 'ACTIVATED' or p.stage == 'ACTIVATING'):
    previously_activated_parcel = cluster.get_parcel('YSPARK', p.version)

print "previously ACTIVATED YSPARK version is %s" % (previously_activated_parcel.version)

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
time.sleep(10) # check again in 10 seconds

print "downloaded YSPARK parcel version %s on cluster %s" % (parcel_version, cluster_name)

parcel.start_distribution()
while True:
  parcel = cluster.get_parcel('YSPARK', parcel_version)
  if parcel.stage == 'DISTRIBUTED':
    break
  if parcel.state.errors:
    # raise Exception(str(parcel.state.errors))
    print(str(parcel.state.errors))
  print "progress: %s / %s" % (parcel.state.progress, parcel.state.totalProgress)
time.sleep(10) # check again in 10 seconds

print "distributed YSPARK parcel version %s on cluster %s" % (parcel_version, cluster_name)

parcel.activate()

while True:
  parcel = cluster.get_parcel('YSPARK', parcel_version)
  if (parcel.stage == 'ACTIVATED') or (parcel.stage == 'ACTIVATING' and parcel.state.progress >= 96):
    break
  if parcel.state.errors:
    # raise Exception(str(parcel.state.errors))
    print(str(parcel.state.errors))
  print "progress: %s / %s" % (parcel.state.progress, parcel.state.totalProgress)
time.sleep(10) # check again in 10 seconds

deploy_parcel=os.readlink('/opt/cloudera/parcels/YSPARK')
if "YSPARK-" + parcel_version == deploy_parcel:
  print "activated YSPARK parcel version %s on cluster %s" % (parcel_version, cluster_name)
else:
  print('no')

cluster.get_service('spark_on_yarn').deploy_client_config()
time.sleep(20)

os.system(os.getcwd() + '/start-thriftServer.sh')
time.sleep(20)

previously_activated_parcel.activate()
time.sleep(20)

hdfs_path='/tmp/tandem/spark/it/' + datetime.datetime.now().strftime('%Y-%m-%d')
os.system('hdfs dfs -mkdir -p ' + hdfs_path)
os.system('hdfs dfs -touchz ' + hdfs_path + '/_SUCCESS')

# http://10.17.28.101:7180/api/v5/clusters/cluster/parcels/