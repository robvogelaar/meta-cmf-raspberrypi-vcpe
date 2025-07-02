# DAC, using dsmcli, dobby, and crun

```text
root@RaspberryPi-Gateway:~$ export DSM_CONFIG_FILE=/etc/dsm.config
```

```text
root@RaspberryPi-Gateway:~$ dsmcli du.install default http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz
  DSMCLI Loaded command.socket file from : command.socket
Command: {"id":1,"method":"du.install","params":{"ee_name":"default","uri":"http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz"}}
Response: {"id":1,"result":{"response":"Installation Started"}}
```

```text
root@RaspberryPi-Gateway:~$ dsmcli du.detail http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz
  DSMCLI Loaded command.socket file from : command.socket
Command: {"id":1,"method":"du.detail","params":{"uuid":"http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz"}}
Response: {"id":1,"result":{"URI":"http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz","UUID":"http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz","eu":"Kn","eu.path":"/home/root/destination/dac-image-webui-v3.1-i686","parent-ee":"default","state":"Installed"}}
```

```text
root@RaspberryPi-Gateway:~$ dsmcli eu.list
  DSMCLI Loaded command.socket file from : command.socket
Command: {"id":1,"method":"eu.list"}
Response: {"id":1,"result":["Kn"]}
```

### the containerized app is using lighttpd ports, kill the host lighttpd first:

```text
root@RaspberryPi-Gateway:~$ killall lighttpd
```

```text
root@RaspberryPi-Gateway:~$ dsmcli eu.start Kn
  DSMCLI Loaded command.socket file from : command.socket
Command: {"id":1,"method":"eu.start","params":{"uid":"Kn"}}
Response: {"id":1,"result":"Starting EU"}
```

```text
root@RaspberryPi-Gateway:~$ DobbyTool list
 descriptor | id                               | state
------------|----------------------------------|-------------
        734 | Kn                               | running
```

```text
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

```text
dsmcli eu.stop Kn
  DSMCLI Loaded command.socket file from : command.socket
Command: {"id":1,"method":"eu.stop","params":{"uid":"Kn"}}
Response: {"id":1,"result":"Stopping EU"}
```

```text
dsmcli du.uninstall http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz
  DSMCLI Loaded command.socket file from : command.socket
Command: {"id":1,"method":"du.uninstall","params":{"uuid":"http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz"}}
Response: {"id":1,"result":"Uninstallation started"}
```


# DAC, using UspPa -c


```text
UspPa -c get Device.DeviceInfo.ModelName
Device.DeviceInfo.ModelName => RPI
```

```text
UspPa -c operate "Device.SoftwareModules.InstallDU(ExecutionEnvRef=default,UUID=sleepy,URL=http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz)"
UspPa -c operate "Device.SoftwareModules.InstallDU(URL=http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz)"
```

```text
UspPa -c get Device.SoftwareModules.DeploymentUnit.
Device.SoftwareModules.DeploymentUnit.1.URL => http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz
Device.SoftwareModules.DeploymentUnit.1.Status => Installed
```

```text
UspPa -c get Device.SoftwareModules.ExecutionUnit.
Device.SoftwareModules.ExecutionUnit.1.Name => Kn
Device.SoftwareModules.ExecutionUnit.1.Status => Idle
```

```text
UspPa -c operate "Device.SoftwareModules.ExecutionUnit.1.SetRequestedState(RequestedState=Active)"
Synchronous Operation (Device.SoftwareModules.ExecutionUnit.1.SetRequestedState()) completed successfully.
Output Arguments:-
   Ret => "Starting EU"
```

# DAC, using oktopus controller

obtain session token using browser developer tools

```text
export sessionToken=''

curl -w "HTTP Status: %{http_code}\n" --location -g --request PUT 'http://192.168.2.120:7777/api/device/oktopus-0-mqtt/any/operate' \
--header 'Content-Type: application/json' \
--header 'Authorization: $sessionToken' \
--data '{
    "command": "Device.SoftwareModules.InstallDU()",
    "send_resp": true,
    "URL": "http://192.168.2.120/dac-image-webui-v3.1-i686.tar.gz"
}'
```



errors observed:

USP_SIGNAL_OperationComplete: Mismatch in calling arguments err_code=7022, but err_msg='(null)'
