check process cron with pidfile /var/run/crond.pid
  group system
  start program = "/etc/init.d/crond start"
  stop  program = "/etc/init.d/crond stop"
  if 5 restarts within 5 cycles then timeout
