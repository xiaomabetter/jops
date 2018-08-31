#!/bin/bash

pid_path=/data/apps/var/node_exporter
pid_file=$pid_path/node_exporter.pid
config_file=/etc/sysconfig/node_exporter
exe_file=/usr/sbin/node_exporter

if [ ! -d "$pid_path" ]; then 
    mkdir -p $pid_path
fi

pid_nums=`ps -ef | grep -v grep | grep "$exe_file"|wc -l`
if [ $pid_nums -ge 1 ];then
    ps -ef | grep -v grep | grep "$exe_file" | awk '{print $2}' > $pid_file
    echo "Process has started already"
    exit 0
fi

OPTIONS=""
[ -r $config_file ] && . $config_file

nohup $exe_file $OPTIONS >> /dev/null 2>&1 &

pid_nums=`ps -ef | grep -v grep | grep "$exe_file"|wc -l`
if [ $pid_nums -ge 1 ];then
    ps -ef | grep -v grep | grep "$exe_file" | awk '{print $2}' > $pid_file
    echo "success to start node_exporter"
    exit 0
else
    echo "fail to start node_exporter"
    exit 1
fi
