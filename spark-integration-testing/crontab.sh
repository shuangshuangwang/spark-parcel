
# 1. Make spark parcel
# 2. Deplop spark parcel
# 3. Deploy spark on yarn config
# 4. Start thriftServer
# 5. Generate a success flag

spark_parcel_dir=`pwd`
source ${spark_parcel_dir}/make-parcel.sh && /opt/cloudera/parcels/Anaconda/bin/python ${spark_parcel_dir}/spark-integration-testing/deploy_parcel.py && ${spark_parcel_dir}/spark-integration-testing/start-thriftServer.sh
