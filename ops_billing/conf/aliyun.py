AccessKeyId = 'LTAIvjpauewMGGPa'
AccessKeySecret = 'KEIOPsuOVihcqd90ruKsSR1VJJQPav'
RegionId = ['cn-hangzhou', 'cn-beijing', 'us-west-1', 'cn-hongkong']

isIoOptimize = ['g5', 'ic5', 'c5', 'sn1ne', 'r5', 're4', 'se1ne', 'se1', 'd1ne''d1', 'i2', 'i1', 'hfc5',
        'hfg5', 'ce4','gn5', 'gn5i', 'gn4','ga1', 'f1', 'f2', 'ebmhfg5', 'ebmc4', 'ebmg5', 'scch5', 'sccg5']

Instance_ecs_Detail_Attributes = [
    'Description','HostName','InstanceName','ExpiredTime','ImageId','InstanceId','InstanceChargeType',
    'CreationTime','InstanceNetworkType','InstanceType','InternetChargeType','InternetMaxBandwidthIn',
    'SecurityGroupIds','InternetMaxBandwidthOut','IoOptimized','Cpu','Memory','OSName','OSType',
    'RegionId','StartTime','Status','ZoneId']

Instance_slb_Detail_Attributes = ['LoadBalancerName','LoadBalancerId', 'VSwitchId', 'VpcId','NetworkType','CreateTime',
                    'Address', 'RegionId','LoadBalancerStatus']

Instance_rds_Detail_Attributes = [
    'ConnectionString', 'AccountMaxQuantity', 'MasterInstanceId',
    'DBInstanceCPU', 'ZoneId', 'ReadOnlyDBInstanceIds', 'VSwitchId', 'VpcId','MaxConnections',
    'DBInstanceType', 'DBInstanceMemory', 'EngineVersion', 'DBInstanceStorageType',
    'DBInstanceStatus', 'PayType', 'MaxIOPS', 'DBInstanceNetType', 'DBInstanceClass',
    'ResourceGroupId', 'DBInstanceId', 'InstanceNetworkType', 'DBInstanceDescription',
    'DBInstanceStorage', 'SupportCreateSuperAccount', 'CreationTime', 'Category',
    'Port','RegionId','SecurityIPList']

Instance_kvstore_Detail_Attributes = [
    'Config','InstanceId', 'ZoneId', 'Engine','NetworkType', 'QPS','ConnectionDomain', 'EngineVersion',
    'InstanceName', 'Bandwidth','ChargeType', 'ReplicationMode', 'InstanceType', 'InstanceStatus', 'Port'
    'InstanceClass', 'RegionId','CreateTime', 'Capacity','LuaStatus', 'SecurityIPList','Connections']