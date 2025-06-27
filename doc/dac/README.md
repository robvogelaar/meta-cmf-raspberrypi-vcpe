# DAC, using dsmcli, dobby, and crun

```text
root@RaspberryPi-Gateway:~$ export DSM_CONFIG_FILE=/etc/dsm.config

root@RaspberryPi-Gateway:~$ dsmcli du.install default http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz
  DSMCLI Loaded command.socket file from : command.socket
Command: {"id":1,"method":"du.install","params":{"ee_name":"default","uri":"http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz"}}
Response: {"id":1,"result":{"response":"Installation Started"}}

root@RaspberryPi-Gateway:~$ dsmcli eu.list
  DSMCLI Loaded command.socket file from : command.socket
Command: {"id":1,"method":"eu.list"}
Response: {"id":1,"result":["Kn"]}

# the containerized app is using lighttpd ports, kill the host lighttpd first

root@RaspberryPi-Gateway:~$ killall lighttpd

root@RaspberryPi-Gateway:~$ dsmcli eu.start Kn
  DSMCLI Loaded command.socket file from : command.socket
Command: {"id":1,"method":"eu.start","params":{"uid":"Kn"}}
Response: {"id":1,"result":"Starting EU"}


root@RaspberryPi-Gateway:~$ DobbyTool list
 descriptor | id                               | state
------------|----------------------------------|-------------
        734 | Kn                               | running


root@RaspberryPi-Gateway:~$ crun --root /var/run/rdk/crun/ exec Kn sh


BusyBox v1.32.1 (2025-04-09 23:15:14 UTC) built-in shell (ash)

/ # ps
  PID USER       VSZ STAT COMMAND
    1 0         5384 S    /usr/libexec/DobbyInit /etc/init.d/lighttpd start
    9 0         9136 S    /usr/sbin/lighttpd -f /etc/lighttpd/lighttpd.conf
   10 0        14024 S    /usr/bin/jse
   11 0        14024 S    /usr/bin/jse
   12 0        14024 S    /usr/bin/jse
   13 0        14024 S    /usr/bin/jse
   15 0         3964 S    sh
   16 0         3968 R    ps

```

# DAC, using UspPa -c

# DAC, using oktopus controller

