#!/bin/bash

pid_path=/data/apps/var/node_exporter
pid_file=$pid_path/node_exporter.pid
exe_file=/usr/sbin/node_exporter


pid_nums=`ps -ef | grep -v grep | grep "$exe_file"|wc -l`
if [ $pid_nums -ge 1 ];then
    ps -ef | grep -v grep | grep "$exe_file"|awk '{print $2}'|xargs kill -9
else
    echo "no process to stop"
    rm $pid_file
    exit 0
fi

sleep 3

pid_nums=`ps -ef | grep -v grep | grep "$exe_file"|wc -l`

if [ $pid_nums -ge 1 ];then
    echo "fail to stop node_exporter"
    exit 1
else
    echo "success to stop node_exporter"
    rm $pid_file
    exit 0
fi
