check process node_exporter with pidfile /data/apps/var/node_exporter/node_exporter.pid
  start program "/data/apps/opt/node_exporter/bin/start.sh" as uid "easemob" and gid "easemob" 
  stop program "/data/apps/opt/node_exporter/bin/stop.sh" as uid "easemob" and gid "easemob" 
  if failed host 127.0.0.1 port 9100 type tcp then alert
  if 5 restarts within 5 cycles then timeout
