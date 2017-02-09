#!/usr/bin/env bash
export SPARK_CONF_DIR=/etc/spark/conf.cloudera.spark_on_yarn
export HADOOP_USER_NAME=tandem

/opt/cloudera/parcels/YSPARK/lib/spark/sbin/stop-thriftserver.sh
/opt/cloudera/parcels/YSPARK/lib/spark/sbin/start-thriftserver.sh     \
  --name spark-integration-testing-thriftserver                       \
  --queue tandem                                                      \
  --executor-memory 12g                                               \
  --total-executor-cores 500                                          \
  --driver-memory 8g                                                  \
  --executor-cores 5                                                  \
  --num-executors 130                                                 \
  --hiveconf hive.server2.thrift.bind.host=10.17.28.200               \
  --hiveconf hive.server2.thrift.port=30403                           \
  --conf spark.sql.codegen.wholeStage=true                            \
  --conf spark.scheduler.mode=FAIR                                    \
  --conf spark.dynamicAllocation.enabled=true                         \
  --conf spark.shuffle.service.enabled=true                           \
  --conf spark.dynamicAllocation.minExecutors=10                      \
  --conf spark.dynamicAllocation.maxExecutors=130                     \
  --conf spark.dynamicAllocation.executorIdleTimeout=200              \
  --conf spark.yarn.executor.memoryOverhead=4096                      \
  --conf "spark.executor.extraJavaOptions=-XX:+UseParallelGC -XX:+UseParallelOldGC -XX:+PrintFlagsFinal -XX:+PrintReferenceGC -verbose:gc -XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:+PrintAdaptiveSizePolicy -XX:+UnlockDiagnosticVMOptions"
