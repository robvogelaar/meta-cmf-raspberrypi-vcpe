![Automatics Diagram](automatics.svg)

# Installation

## Run the automatics.sh script:

```text
automatics.sh

lxc list
+-----------------+---------+--------------------------------+-----------------------------+
| automatics      | RUNNING | 10.10.10.240 (eth0)            | 2001:dbf:0:1::240 (eth0)    |
+-----------------+---------+--------------------------------+-----------------------------+
```

## Enter automatics container (shell):

```text
$ lxc exec automatics bash
[root@automatics ~]# 
```

# Device Connection Test

Note: 10.107.200.100 is an example IP address. You must enter your actual device's WAN (erouter0) IP address.

This test connects to device, and runs a number of commands on the device.

## Verify ssh connection to device:

```text
[root@automatics ~]# ssh root@10.107.200.100
root@RaspberryPi-Gateway:~# 

ctrl-D or exit

[root@automatics ~]# 
```

## Configure device IP

```text
[root@automatics ~]# cd
[root@automatics ~]# NEW_IP="10.107.200.100"
[root@automatics ~]# sed -i "s/10\.107\.200\.110/$NEW_IP/g" /root/java-handler/src/test/java/com/connectionproviders/deviceconnectionprovider/DeviceConnectionProviderImplTest.java
[root@automatics ~]# sed -i "s/10\.107\.200\.110/$NEW_IP/g" /root/server-config.xml
```

## Run connection test:

```text
[root@automatics ~]# cd java-handler
[root@automatics java-handler]# mvn test -Dautomatics.properties.file=http://localhost:8080/automatics/automatics.properties
```

<details>
<summary>Click to expand test execution</summary>

```text
[INFO] Scanning for projects...
[INFO]
[INFO] -------------< com.automatics.providers:rpi-provider-impl >-------------
[INFO] Building RPIProviderImpl 0.0.1-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[WARNING] 1 problem was encountered while building the effective model for org.javassist:javassist:jar:3.21.0-GA during dependency collection step for project (use -X to see details)
[INFO]
[INFO] --- resources:3.1.0:resources (default-resources) @ rpi-provider-impl ---
[WARNING] Using platform encoding (UTF-8 actually) to copy filtered resources, i.e. build is platform dependent!
[INFO] Copying 1 resource
[INFO]
[INFO] --- compiler:3.11.0:compile (default-compile) @ rpi-provider-impl ---
[INFO] Nothing to compile - all classes are up to date
[INFO]
[INFO] --- resources:3.1.0:testResources (default-testResources) @ rpi-provider-impl ---
[WARNING] Using platform encoding (UTF-8 actually) to copy filtered resources, i.e. build is platform dependent!
[INFO] skip non existing resourceDirectory /root/java-handler/src/test/resources
[INFO]
[INFO] --- compiler:3.11.0:testCompile (default-testCompile) @ rpi-provider-impl ---
[INFO] Changes detected - recompiling the module! :source
[WARNING] File encoding has not been set, using platform encoding UTF-8, i.e. build is platform dependent!
[INFO] Compiling 1 source file with javac [debug target 11] to target/test-classes
[WARNING] system modules path not set in conjunction with -source 11
[INFO]
[INFO] --- surefire:3.2.5:test (default-test) @ rpi-provider-impl ---
[INFO] Using auto detected provider org.apache.maven.surefire.testng.TestNGProvider
[INFO]
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.connectionproviders.deviceconnectionprovider.DeviceConnectionProviderImplTest
21:04:48,809 |-INFO in ch.qos.logback.classic.LoggerContext[default] - Found resource [logback-test.xml] at [jar:file:/root/.m2/repository/com/automatics/apps/automatics-core/2.29.0-SNAPSHOT/automatics-core-2.29.0-SNAPSHOT.jar!/logback-test.xml]
21:04:48,817 |-INFO in ch.qos.logback.core.joran.spi.ConfigurationWatchList@272ed83b - URL [jar:file:/root/.m2/repository/com/automatics/apps/automatics-core/2.29.0-SNAPSHOT/automatics-core-2.29.0-SNAPSHOT.jar!/logback-test.xml] is not of type file
21:04:48,925 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.core.ConsoleAppender]
21:04:48,927 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [stdOutAppender]
21:04:48,932 |-ERROR in ch.qos.logback.core.joran.spi.Interpreter@7:13 - no applicable action for [onMatch], current ElementPath  is [[configuration][appender][filter][onMatch]]
21:04:48,932 |-ERROR in ch.qos.logback.core.joran.spi.Interpreter@8:16 - no applicable action for [onMismatch], current ElementPath  is [[configuration][appender][filter][onMismatch]]
21:04:48,933 |-INFO in ch.qos.logback.core.joran.action.NestedComplexPropertyIA - Assuming default type [ch.qos.logback.classic.encoder.PatternLayoutEncoder] for [encoder] property
21:04:48,945 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.classic.sift.SiftingAppender]
21:04:48,947 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [deviceSiftingAppender]
21:04:48,949 |-ERROR in ch.qos.logback.core.joran.spi.Interpreter@18:13 - no applicable action for [onMatch], current ElementPath  is [[configuration][appender][filter][onMatch]]
21:04:48,949 |-ERROR in ch.qos.logback.core.joran.spi.Interpreter@19:16 - no applicable action for [onMismatch], current ElementPath  is [[configuration][appender][filter][onMismatch]]
21:04:48,955 |-INFO in ch.qos.logback.core.joran.action.NestedComplexPropertyIA - Assuming default type [ch.qos.logback.classic.sift.MDCBasedDiscriminator] for [discriminator] property
21:04:48,957 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.classic.sift.SiftingAppender]
21:04:48,957 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [TraceLogger]
21:04:48,957 |-INFO in ch.qos.logback.core.joran.action.NestedComplexPropertyIA - Assuming default type [ch.qos.logback.classic.sift.MDCBasedDiscriminator] for [discriminator] property
21:04:48,958 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.classic.sift.SiftingAppender]
21:04:48,958 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [SerialTrace]
21:04:48,958 |-INFO in ch.qos.logback.core.joran.action.NestedComplexPropertyIA - Assuming default type [ch.qos.logback.classic.sift.MDCBasedDiscriminator] for [discriminator] property
21:04:48,959 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.classic.sift.SiftingAppender]
21:04:48,959 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [crash-analysis]
21:04:48,959 |-INFO in ch.qos.logback.core.joran.action.NestedComplexPropertyIA - Assuming default type [ch.qos.logback.classic.sift.MDCBasedDiscriminator] for [discriminator] property
21:04:48,960 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting additivity of logger [org.apache.http] to false
21:04:48,960 |-INFO in ch.qos.logback.classic.joran.action.LevelAction - org.apache.http level set to INFO
21:04:48,960 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [deviceSiftingAppender] to Logger[org.apache.http]
21:04:48,960 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting level of logger [ConnectionTrace] to TRACE
21:04:48,960 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting additivity of logger [ConnectionTrace] to false
21:04:48,960 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [TraceLogger] to Logger[ConnectionTrace]
21:04:48,960 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting level of logger [SerialTrace] to TRACE
21:04:48,960 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting additivity of logger [SerialTrace] to false
21:04:48,960 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [SerialTrace] to Logger[SerialTrace]
21:04:48,961 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting level of logger [crash-analysis] to DEBUG
21:04:48,961 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting additivity of logger [crash-analysis] to false
21:04:48,961 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [crash-analysis] to Logger[crash-analysis]
21:04:48,961 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [stdOutAppender] to Logger[ROOT]
21:04:48,961 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [deviceSiftingAppender] to Logger[ROOT]
21:04:48,961 |-INFO in ch.qos.logback.classic.joran.action.ConfigurationAction - End of configuration.
21:04:48,961 |-INFO in ch.qos.logback.classic.joran.JoranConfigurator@17f62e33 - Registering current configuration as safe fallback point
[INFO][2025-06-24 21:04:48,977][[main] - AutomaticsPropertyUtility: Reading automatics.properties file from http://localhost:8080/automatics/automatics.properties
21:04:48,978 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.core.FileAppender]
21:04:48,980 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [FILE-test-suite]
21:04:48,982 |-INFO in ch.qos.logback.core.FileAppender[FILE-test-suite] - File property is set to [target/logs/test-suite.log]
[INFO][2025-06-24 21:04:49,013][[main] - INIT- Requesting device config from http://localhost:8080/automatics/device_config.json
[INFO][2025-06-24 21:04:49,130][[main] - frameworkSupportedModels=,,,Rpi-RDKB,
[INFO][2025-06-24 21:04:49,131][[main] - rdkvGWModels=,
[INFO][2025-06-24 21:04:49,132][[main] - rdkvCLModels=,
[INFO][2025-06-24 21:04:49,132][[main] - rdkbModels=,Rpi-RDKB,
[INFO][2025-06-24 21:04:49,132][[main] - rdkcModels=
[INFO][2025-06-24 21:04:49,143][[main] - Reading server-config.xml from /root/server-config.xml
[ERROR][2025-06-24 21:04:49,167][[main] - ***** PRIVATE KEY LOCATION NOT DEFINED FOR 10.107.200.100  IN CONFIGURATION FILE *******
[INFO][2025-06-24 21:04:49,470][[main] - SSH port is set from Automatics property
[INFO][2025-06-24 21:04:49,623][[main] - Executing command: uname -a
[INFO][2025-06-24 21:04:49,652][[main] -
<===========================  RESPONSE =======================>
Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux

<=============================================================>
[INFO][2025-06-24 21:04:49,654][[main] - exe1: The return value is Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux
[INFO][2025-06-24 21:04:49,657][[main] - dev HostIpAddress 10.107.200.100
[INFO][2025-06-24 21:04:49,672][[main] - SSH port is set from Automatics property
[INFO][2025-06-24 21:04:49,746][[main] - Executing command: df
[INFO][2025-06-24 21:04:49,769][[main] -
<===========================  RESPONSE =======================>
Filesystem           1K-blocks      Used Available Use% Mounted on
default/containers/vcpe
                        604544     93696    510848  15% /
none                       492         4       488   1% /dev
udev                  32673196         0  32673196   0% /dev/fuse
udev                  32673196         0  32673196   0% /dev/net/tun
tmpfs                      100         0       100   0% /dev/lxd
default/custom/default_vcpe-nvram
                          3840       128      3712   3% /nvram
tmpfs                      100         0       100   0% /dev/.lxd-mounts
none                       492         4       488   1% /proc/sys/kernel/random/boot_id
tmpfs                 32774708         8  32774700   0% /dev/shm
tmpfs                 13109884     25124  13084760   0% /run
tmpfs                     4096         0      4096   0% /sys/fs/cgroup
tmpfs                 32774712      2612  32772100   0% /tmp
tmpfs                 32774708      1052  32773656   0% /var/volatile
tmpfs                   131072    131072         0 100% /rdklogs
/nvram/secure_path        3840       128      3712   3% /nvram/rdkssa

<=============================================================>
[INFO][2025-06-24 21:04:49,784][[main] - SSH port is set from Automatics property
[INFO][2025-06-24 21:04:49,855][[main] - Executing command: uname -a
[INFO][2025-06-24 21:04:49,877][[main] -
<===========================  RESPONSE =======================>
Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux

<=============================================================>
[INFO][2025-06-24 21:04:49,877][[main] - Executing command: cat /version.txt
[INFO][2025-06-24 21:04:49,899][[main] -
<===========================  RESPONSE =======================>
Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux
imagename:X86EMLTRBB_rdkb-2025q1-kirkstone_20250616213408
BRANCH=rdkb-2025q1-kirkstone
YOCTO_VERSION=kirkstone
VERSION=rdkb-2025q1-kirkstone.06.16.25
SPIN=0
BUILD_TIME="2025-06-16 21:34:08"
JENKINS_JOB=Default
JENKINS_BUILD_NUMBER=0
Generated on Mon Jun 16  21:34:08 UTC 2025

<=============================================================>
[INFO][2025-06-24 21:04:49,899][[main] - Executing command: ls -l
[INFO][2025-06-24 21:04:50,024][[main] -
<===========================  RESPONSE =======================>
Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux
imagename:X86EMLTRBB_rdkb-2025q1-kirkstone_20250616213408
BRANCH=rdkb-2025q1-kirkstone
YOCTO_VERSION=kirkstone
VERSION=rdkb-2025q1-kirkstone.06.16.25
SPIN=0
BUILD_TIME="2025-06-16 21:34:08"
JENKINS_JOB=Default
JENKINS_BUILD_NUMBER=0
Generated on Mon Jun 16  21:34:08 UTC 2025
total 9081
srwxr-xr-x    1 root     root             0 Jun 18 18:52 command.socket
drwxr-xr-x    2 root     root             2 Mar  9  2018 destination
-rw-r--r--    1 root     root        160325 Jun 18 18:49 plot5.svg
-rw-r--r--    1 root     root        156777 Jun 18 18:56 plot6.svg
-rw-r--r--    1 root     root      83307768 Jun 24 21:03 rssfree.log

<=============================================================>
[INFO][2025-06-24 21:04:50,025][[main] - Executing command: uptime
[INFO][2025-06-24 21:04:50,152][[main] -
<===========================  RESPONSE =======================>
Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux
imagename:X86EMLTRBB_rdkb-2025q1-kirkstone_20250616213408
BRANCH=rdkb-2025q1-kirkstone
YOCTO_VERSION=kirkstone
VERSION=rdkb-2025q1-kirkstone.06.16.25
SPIN=0
BUILD_TIME="2025-06-16 21:34:08"
JENKINS_JOB=Default
JENKINS_BUILD_NUMBER=0
Generated on Mon Jun 16  21:34:08 UTC 2025
total 9081
srwxr-xr-x    1 root     root             0 Jun 18 18:52 command.socket
drwxr-xr-x    2 root     root             2 Mar  9  2018 destination
-rw-r--r--    1 root     root        160325 Jun 18 18:49 plot5.svg
-rw-r--r--    1 root     root        156777 Jun 18 18:56 plot6.svg
-rw-r--r--    1 root     root      83307768 Jun 24 21:03 rssfree.log
 21:04:50 up 6 days,  2:12,  1 user,  load average: 1.72, 1.57, 1.56

<=============================================================>
[INFO][2025-06-24 21:04:50,156][[main] - Response with commandlist metnod is:  Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux
Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux
imagename:X86EMLTRBB_rdkb-2025q1-kirkstone_20250616213408
BRANCH=rdkb-2025q1-kirkstone
YOCTO_VERSION=kirkstone
VERSION=rdkb-2025q1-kirkstone.06.16.25
SPIN=0
BUILD_TIME="2025-06-16 21:34:08"
JENKINS_JOB=Default
JENKINS_BUILD_NUMBER=0
Generated on Mon Jun 16  21:34:08 UTC 2025
Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux
imagename:X86EMLTRBB_rdkb-2025q1-kirkstone_20250616213408
BRANCH=rdkb-2025q1-kirkstone
YOCTO_VERSION=kirkstone
VERSION=rdkb-2025q1-kirkstone.06.16.25
SPIN=0
BUILD_TIME="2025-06-16 21:34:08"
JENKINS_JOB=Default
JENKINS_BUILD_NUMBER=0
Generated on Mon Jun 16  21:34:08 UTC 2025
total 9081
srwxr-xr-x    1 root     root             0 Jun 18 18:52 command.socket
drwxr-xr-x    2 root     root             2 Mar  9  2018 destination
-rw-r--r--    1 root     root        160325 Jun 18 18:49 plot5.svg
-rw-r--r--    1 root     root        156777 Jun 18 18:56 plot6.svg
-rw-r--r--    1 root     root      83307768 Jun 24 21:03 rssfree.log
Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux
imagename:X86EMLTRBB_rdkb-2025q1-kirkstone_20250616213408
BRANCH=rdkb-2025q1-kirkstone
YOCTO_VERSION=kirkstone
VERSION=rdkb-2025q1-kirkstone.06.16.25
SPIN=0
BUILD_TIME="2025-06-16 21:34:08"
JENKINS_JOB=Default
JENKINS_BUILD_NUMBER=0
Generated on Mon Jun 16  21:34:08 UTC 2025
total 9081
srwxr-xr-x    1 root     root             0 Jun 18 18:52 command.socket
drwxr-xr-x    2 root     root             2 Mar  9  2018 destination
-rw-r--r--    1 root     root        160325 Jun 18 18:49 plot5.svg
-rw-r--r--    1 root     root        156777 Jun 18 18:56 plot6.svg
-rw-r--r--    1 root     root      83307768 Jun 24 21:03 rssfree.log
 21:04:50 up 6 days,  2:12,  1 user,  load average: 1.72, 1.57, 1.56

[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 1.573 s -- in com.connectionproviders.deviceconnectionprovider.DeviceConnectionProviderImplTest
[INFO]
[INFO] Results:
[INFO]
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO]
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  5.064 s
[INFO] Finished at: 2025-06-24T21:04:50Z
[INFO] ------------------------------------------------------------------------
[root@automatics java-handler]#
```
</details>


# RDKB Tests

## Configure device IP and MAC in server-config.xml

/root/server-config.xml

## Configure device IP and MAC in device manager UI

`http://10.10.10.240:8080/DeviceManagerUI/login.html`

username: admin

password: empty password

Self Authentication

Search by Group

Select All

Fetch/Refresh

change all instances of the DC:A6:32:CA:11:B6 with your MAC

change all instances of the 10.107.200.110 with your IP

## Run Test(s)

specify device:

-DsettopList=00:16:3E:20:79:68

specify test cases

-DfilterTestIds=TC-RDKB-WEBPA-1003



```text
[root@automatics ~]# cd rdkb-tests/
[root@automatics rdkb-tests]# export MAVEN_OPTS="--add-opens java.base/java.net=ALL-UNNAMED --add-opens java.base/java.time.format=ALL-UNNAMED --add-opens java.base/java.time=ALL-UNNAMED"
[root@automatics rdkb-tests]# mvn -U exec:java -DsettopList=00:16:3E:20:79:68 -DfilterTestType=GROUP_OR_AUTOID -DskipTests=true -DfilterTestIds=TC-RDKB-WEBPA-1003 -DexecutionMode=RDKB -DretryByDefault=false -DbuildType=RDK -Dhttps.protocols=TLSv1.1,TLSv1.2 -Dsun.security.ssl.allowUnsafeRenegotiation=true -Dautomatics.properties.file=http://localhost:8080/automatics/automatics.properties
```

<details>
<summary>Click to expand test execution</summary>

```text
[INFO] Scanning for projects...
[INFO]
[INFO] --------------< RDKMAutomationRDKBTests:rdkb-automation >---------------
[INFO] Building rdkb-automation 0.0.1-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[WARNING] Parameter 'classpath' is unknown for plugin 'exec-maven-plugin:1.2.1:java (default-cli)'
[INFO]
[INFO] >>> exec:1.2.1:java (default-cli) > validate @ rdkb-automation >>>
[INFO]
[INFO] <<< exec:1.2.1:java (default-cli) < validate @ rdkb-automation <<<
[INFO]
[WARNING] 1 problem was encountered while building the effective model for org.javassist:javassist:jar:3.21.0-GA during dependency collection step for project (use -X to see details)
[INFO]
[INFO] --- exec:1.2.1:java (default-cli) @ rdkb-automation ---
21:53:21,742 |-INFO in ch.qos.logback.classic.LoggerContext[default] - Found resource [logback-test.xml] at [jar:file:/root/.m2/repository/com/automatics/apps/automatics-core/2.29.0-SNAPSHOT/automatics-core-2.29.0-SNAPSHOT.jar!/logback-test.xml]
21:53:21,752 |-INFO in ch.qos.logback.core.joran.spi.ConfigurationWatchList@da020ca - URL [jar:file:/root/.m2/repository/com/automatics/apps/automatics-core/2.29.0-SNAPSHOT/automatics-core-2.29.0-SNAPSHOT.jar!/logback-test.xml] is not of type file
21:53:21,845 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.core.ConsoleAppender]
21:53:21,847 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [stdOutAppender]
21:53:21,853 |-ERROR in ch.qos.logback.core.joran.spi.Interpreter@7:13 - no applicable action for [onMatch], current ElementPath  is [[configuration][appender][filter][onMatch]]
21:53:21,853 |-ERROR in ch.qos.logback.core.joran.spi.Interpreter@8:16 - no applicable action for [onMismatch], current ElementPath  is [[configuration][appender][filter][onMismatch]]
21:53:21,854 |-INFO in ch.qos.logback.core.joran.action.NestedComplexPropertyIA - Assuming default type [ch.qos.logback.classic.encoder.PatternLayoutEncoder] for [encoder] property
21:53:21,866 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.classic.sift.SiftingAppender]
21:53:21,868 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [deviceSiftingAppender]
21:53:21,869 |-ERROR in ch.qos.logback.core.joran.spi.Interpreter@18:13 - no applicable action for [onMatch], current ElementPath  is [[configuration][appender][filter][onMatch]]
21:53:21,870 |-ERROR in ch.qos.logback.core.joran.spi.Interpreter@19:16 - no applicable action for [onMismatch], current ElementPath  is [[configuration][appender][filter][onMismatch]]
21:53:21,871 |-INFO in ch.qos.logback.core.joran.action.NestedComplexPropertyIA - Assuming default type [ch.qos.logback.classic.sift.MDCBasedDiscriminator] for [discriminator] property
21:53:21,873 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.classic.sift.SiftingAppender]
21:53:21,874 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [TraceLogger]
21:53:21,874 |-INFO in ch.qos.logback.core.joran.action.NestedComplexPropertyIA - Assuming default type [ch.qos.logback.classic.sift.MDCBasedDiscriminator] for [discriminator] property
21:53:21,874 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.classic.sift.SiftingAppender]
21:53:21,874 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [SerialTrace]
21:53:21,874 |-INFO in ch.qos.logback.core.joran.action.NestedComplexPropertyIA - Assuming default type [ch.qos.logback.classic.sift.MDCBasedDiscriminator] for [discriminator] property
21:53:21,875 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.classic.sift.SiftingAppender]
21:53:21,875 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [crash-analysis]
21:53:21,875 |-INFO in ch.qos.logback.core.joran.action.NestedComplexPropertyIA - Assuming default type [ch.qos.logback.classic.sift.MDCBasedDiscriminator] for [discriminator] property
21:53:21,876 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting additivity of logger [org.apache.http] to false
21:53:21,876 |-INFO in ch.qos.logback.classic.joran.action.LevelAction - org.apache.http level set to INFO
21:53:21,876 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [deviceSiftingAppender] to Logger[org.apache.http]
21:53:21,876 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting level of logger [ConnectionTrace] to TRACE
21:53:21,876 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting additivity of logger [ConnectionTrace] to false
21:53:21,876 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [TraceLogger] to Logger[ConnectionTrace]
21:53:21,877 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting level of logger [SerialTrace] to TRACE
21:53:21,877 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting additivity of logger [SerialTrace] to false
21:53:21,877 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [SerialTrace] to Logger[SerialTrace]
21:53:21,877 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting level of logger [crash-analysis] to DEBUG
21:53:21,877 |-INFO in ch.qos.logback.classic.joran.action.LoggerAction - Setting additivity of logger [crash-analysis] to false
21:53:21,877 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [crash-analysis] to Logger[crash-analysis]
21:53:21,877 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [stdOutAppender] to Logger[ROOT]
21:53:21,877 |-INFO in ch.qos.logback.core.joran.action.AppenderRefAction - Attaching appender named [deviceSiftingAppender] to Logger[ROOT]
21:53:21,877 |-INFO in ch.qos.logback.classic.joran.action.ConfigurationAction - End of configuration.
21:53:21,878 |-INFO in ch.qos.logback.classic.joran.JoranConfigurator@6268d908 - Registering current configuration as safe fallback point
[INFO][2025-06-24 21:53:21,879][[com.automatics.executor.Starter.main()] - Starting the execution process for the given test cases.
21:53:21,880 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.core.FileAppender]
21:53:21,881 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [FILE-test-suite]
21:53:21,882 |-INFO in ch.qos.logback.core.FileAppender[FILE-test-suite] - File property is set to [target/logs/test-suite.log]
[INFO][2025-06-24 21:53:21,890][[com.automatics.executor.Starter.main()] - Initializing application context partner-applicationContext.xml
[INFO][2025-06-24 21:53:22,128][[com.automatics.executor.Starter.main()] - Initializing application context applicationContext.xml
[INFO][2025-06-24 21:53:22,160][[com.automatics.executor.Starter.main()] - AutomaticsPropertyUtility: Reading automatics.properties file from http://localhost:8080/automatics/automatics.properties
[INFO][2025-06-24 21:53:22,188][[com.automatics.executor.Starter.main()] - Shut Down Hook Attached.
[INFO][2025-06-24 21:53:22,191][[com.automatics.executor.Starter.main()] - Start Execution Test Suite
[INFO][2025-06-24 21:53:22,191][[com.automatics.executor.Starter.main()] - Bean testInitializer is not configured.
[INFO][2025-06-24 21:53:22,191][[com.automatics.executor.Starter.main()] - Cleaning the trace log directory
[INFO][2025-06-24 21:53:22,199][[com.automatics.executor.Starter.main()] - AutomaticsPropertyUtility: Reading automatics.properties file from http://localhost:8080/automatics/automatics.properties
[INFO][2025-06-24 21:53:22,202][[com.automatics.executor.Starter.main()] - >>>[INIT]: Validating config files
[INFO][2025-06-24 21:53:22,203][[com.automatics.executor.Starter.main()] - INIT- Requesting device config from http://localhost:8080/automatics/device_config.json
[INFO][2025-06-24 21:53:22,308][[com.automatics.executor.Starter.main()] - INIT- Requesting device config from http://localhost:8080/automatics/device_config.json
[INFO][2025-06-24 21:53:22,312][[com.automatics.executor.Starter.main()] - frameworkSupportedModels=,,,Rpi-RDKB,
[INFO][2025-06-24 21:53:22,312][[com.automatics.executor.Starter.main()] - rdkvGWModels=,
[INFO][2025-06-24 21:53:22,313][[com.automatics.executor.Starter.main()] - rdkvCLModels=,
[INFO][2025-06-24 21:53:22,313][[com.automatics.executor.Starter.main()] - rdkbModels=,Rpi-RDKB,
[INFO][2025-06-24 21:53:22,313][[com.automatics.executor.Starter.main()] - rdkcModels=
[INFO][2025-06-24 21:53:22,328][[com.automatics.executor.Starter.main()] - Reading implementation from core for deviceProvider
[INFO][2025-06-24 21:53:22,339][[com.automatics.executor.Starter.main()] - Is Account based test: false
[INFO][2025-06-24 21:53:22,341][[com.automatics.executor.Starter.main()] - INIT-00:16:3E:20:79:68 Get device details
[INFO][2025-06-24 21:53:22,547][[com.automatics.executor.Starter.main()] - Fetching device details for 00:16:3E:20:79:68  Url Path: http://localhost:8080/DeviceManager/deviceManagement/getDeviceDetails
[INFO][2025-06-24 21:53:22,671][[com.automatics.executor.Starter.main()] - Response: {"devices":[{"id":"3841","name":"","hardwareRevision":"SLN567","hostMacAddress":"00:16:3E:20:79:68","hostIp4Address":"10.107.200.100","hostIp6Address":null,"clientIpAddress":"10.107.200.100","model":"Rpi-RDKB","manufacturer":"","serialNumber":"HYU890","unitAddress":null,"remoteType":"","estbMacAddress":"00:16:3E:20:79:68","mtaMacAddress":"00:16:3E:20:79:68","mtaIpAddress":"10.107.200.127","ecmMacAddress":"00:16:3E:20:79:68","ecmIpAddress":"10.107.200.100","headend":"HE","gatewayMac":"00:16:3E:20:79:68","extraProperties":{"deviceIp":"","password":"","ethernetMacAddress":"","osType":"","devicePort":"","wifiCapability":"","nodePort":"","connectionType":"","wifiMacAddress":"","username":""},"rackId":"","deviceType":"","rackName":"","slotName":"","slotNumber":"","settopGroupName":"","homeAccountName":"","homeAccountNumber":"123456","homeAccountGroupName":"","rackServerHost":"","rackServerPort":0,"status":"GOOD","rackGroups":null,"features":null,"components":null,"wanMacAddress":""}],"errorMsg":null,"remarks":null}
[INFO][2025-06-24 21:53:22,707][[com.automatics.executor.Starter.main()] - INIT-00:16:3E:20:79:68 Obtained device details
[INFO][2025-06-24 21:53:22,708][[com.automatics.executor.Starter.main()] - Found matching device object from config for rack model Rpi-RDKB
[INFO][2025-06-24 21:53:22,709][[com.automatics.executor.Starter.main()] - >>>[INIT]: Found device config mapped for rack model Rpi-RDKB
[INFO][2025-06-24 21:53:22,709][[com.automatics.executor.Starter.main()] - >>>[INIT]: Mapping rack model Rpi-RDKB to  automatics model Rpi-RDKB
[INFO][2025-06-24 21:53:22,709][[com.automatics.executor.Starter.main()] - [INIT LOG] : Non RDKV Client device
[INFO][2025-06-24 21:53:22,711][[pool-2-thread-1] - Desk Box Testing enabled
[INFO][2025-06-24 21:53:22,712][[pool-2-thread-1] - INIT-00:16:3E:20:79:68 Skipping locking device as Non-Rack device
[INFO][2025-06-24 21:53:22,712][[pool-2-thread-1] - Setting access mechanism for device 00:16:3E:20:79:68 SSH
[INFO][2025-06-24 21:53:22,712][[pool-2-thread-1] - INIT-00:16:3E:20:79:68 Setting access method SSH
[INFO][2025-06-24 21:53:22,712][[pool-2-thread-1] - INIT-00:16:3E:20:79:68 Checking if accessibility check required
[INFO][2025-06-24 21:53:22,712][[pool-2-thread-1] - Setting accessibility check required to false for device 00:16:3E:20:79:68 from device config
[INFO][2025-06-24 21:53:22,712][[pool-2-thread-1] - Accessibility check required for device 00:16:3E:20:79:68 false
[INFO][2025-06-24 21:53:22,713][[pool-2-thread-1] - INIT-00:16:3E:20:79:68 Checking if accessibility check required is false
[INFO][2025-06-24 21:53:22,713][[pool-2-thread-1] - INIT-00:16:3E:20:79:68 Assuming device is accessible
[INFO][2025-06-24 21:53:22,713][[pool-2-thread-1] - INIT-00:16:3E:20:79:68 Is device accessible true
[INFO][2025-06-24 21:53:22,713][[pool-2-thread-1] - Desk Box Testing enabled
[INFO][2025-06-24 21:53:22,713][[pool-2-thread-1] - INIT-00:16:3E:20:79:68 DeviceConfig Connection Based TraceProvider wiring
[INFO][2025-06-24 21:53:22,715][[pool-2-thread-1] - Reading implementation from partner for deviceConnectionProvider
[INFO][2025-06-24 21:53:22,716][[pool-2-thread-1] - Additional trace support : null
[INFO][2025-06-24 21:53:22,717][[pool-2-thread-1] - settopObj.getModel() = Rpi-RDKB
[INFO][2025-06-24 21:53:22,717][[pool-2-thread-1] - Additional logging requirement if any enabled will be skipped due to configuration issue
[INFO][2025-06-24 21:53:22,719][[pool-2-thread-1] - Trace Log File location /root/rdkb-tests/target/settoptrace/00163E207968settop_trace.log
[INFO][2025-06-24 21:53:22,719][[pool-2-thread-1] - Crash Analysis not enabled during trace monitoring
[INFO][2025-06-24 21:53:22,720][[pool-2-thread-1] - Serial based trace to be initialized: false
[INFO][2025-06-24 21:53:22,720][[pool-2-thread-1] - [INIT LOG] : Adding dut to locked list
[INFO][2025-06-24 21:53:22,720][[pool-2-thread-1] - DeviceConfig Macs 00:16:3E:20:79:68
[INFO][2025-06-24 21:53:22,720][[pool-2-thread-1] - Dut Added to locked list 00:16:3E:20:79:68
[INFO][2025-06-24 21:53:25,711][[com.automatics.executor.Starter.main()] - Finished Non-IP Initialization Threads
[INFO][2025-06-24 21:53:25,712][[com.automatics.executor.Starter.main()] - Collecting dut info
[INFO][2025-06-24 21:53:25,714][[com.automatics.executor.Starter.main()] - Requesting data from http://localhost:8084/api/rack/service/getmasterconfig?configName=TEST_TYPE_MAP
[INFO][2025-06-24 21:53:25,731][[com.automatics.executor.Starter.main()] - {"configName":"TEST_TYPE_MAP","configValue":"QUICK=qt,QUICK_CI=qt,FAST_QUICK=fast_qt,FAST_QUICK_CI=fast_qt,1HOUR=1h,2DAYS=2d,2DAYS_L2=2d_L2,2DAYS_L3=2d_L3,2DAYS_L4=2d_L4,4HOUR=4h,4HOUR_L2=4h_L2,4HOUR_L3=4h_L3,4HOUR_L4=4h_L4,CI=ci,COMPONENT=GROUP_OR_AUTOID,QT=qt,CI_QT=qt,1H=1h,4H=4h,2D=2d,PERFORMANCE=PERFORMANCE,SANITY=1h,SANITY_XI3=1h,SMOKE=4h,SMOKE_L2=4h_L2,SMOKE_L3=4h_L2,SMOKE_L4=4h_L2,SMOKE_XI3=4h,FUNCTIONAL=2d,FUNCTIONAL_L2=2d_L2,FUNCTIONAL_L3=2d_L3,FUNCTIONAL_L4=2d_L4,FUNCTIONAL_XI3=2d","isUserEditable":"Y","updatedDate":"2025-06-19T20:09:12.000+00:00","updatedUser":"root@localhost"}

...
... TestNG 7.0.1 by CÃ©dric Beust (cedric@beust.com)
...

[INFO][2025-06-24 21:53:26,148][[com.automatics.executor.Starter.main()] - AutomaticsTapApi instance not available. Creating new instance
[INFO][2025-06-24 21:53:26,149][[com.automatics.executor.Starter.main()] - Creating new instance for AutomaticsTapApi
[INFO][2025-06-24 21:53:26,149][[com.automatics.executor.Starter.main()] - Reading implementation from partner for deviceConnectionProvider
[INFO][2025-06-24 21:53:26,182][[com.automatics.executor.Starter.main()] - >>>[BEFORE_SUITE]: Perform before suite initialization
[INFO][2025-06-24 21:53:26,182][[com.automatics.executor.Starter.main()] - Bean testInitializer is not configured.
[INFO][2025-06-24 21:53:26,182][[com.automatics.executor.Starter.main()] - Adding locked devices to dut object in AutomaticsTestBase
[INFO][2025-06-24 21:53:26,182][[com.automatics.executor.Starter.main()] - Locked Settops: 1
[INFO][2025-06-24 21:53:26,183][[pool-4-thread-1] - >>>[BEFORE_SUITE]: Verifying if build loaded in device as expected
[INFO][2025-06-24 21:53:26,183][[pool-4-thread-1] - >>>[BEFORE_SUITE]: Build in device is as expected
[INFO][2025-06-24 21:53:26,183][[pool-4-thread-1] - >>>[BEFORE_SUITE]: Setting appropritate build appender based on executionMode
[INFO][2025-06-24 21:53:26,189][[pool-4-thread-1] - Skipping setting of execution mode in device as partner specific initialization is not configured.
[INFO][2025-06-24 21:53:26,189][[pool-4-thread-1] - INIT-00:16:3E:20:79:68 Perform before suite initialization
[INFO][2025-06-24 21:53:26,189][[pool-4-thread-1] - Skipping partner specific before suite initialization as it is not configured.
[INFO][2025-06-24 21:53:26,189][[pool-4-thread-1] - >>>[BEFORE_SUITE]: Starting device connection trace
[INFO][2025-06-24 21:53:26,189][[pool-4-thread-1] - Starting trace with command : tail -F -n 0  /rdklogs/logs/*
[INFO][2025-06-24 21:53:26,192][[ConnectionThread_34 (00:16:3E:20:79:68)] - Starting reading..00163E207968settop_trace.log,
21:53:26,193 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.core.FileAppender]
21:53:26,193 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [FILE-00163E207968settop_trace.log]
21:53:26,193 |-INFO in ch.qos.logback.core.FileAppender[FILE-00163E207968settop_trace.log] - File property is set to [target/settoptrace/00163E207968settop_trace.log]
[INFO][2025-06-24 21:53:26,194][[ConnectionThread_34 (00:16:3E:20:79:68)] - Going to connect device for trace monitoring .....!
[INFO][2025-06-24 21:53:26,194][[ConnectionThread_34 (00:16:3E:20:79:68)] - XX Host IP Address : 10.107.200.100
[INFO][2025-06-24 21:53:26,194][[ConnectionThread_34 (00:16:3E:20:79:68)] - XX Host IP6 Address : null
[INFO][2025-06-24 21:53:26,194][[ConnectionThread_34 (00:16:3E:20:79:68)] - XX Host MAC Address : 00:16:3E:20:79:68
[INFO][2025-06-24 21:53:26,194][[ConnectionThread_34 (00:16:3E:20:79:68)] - Settoptrace debugging:Inside Non RDKV client device
[INFO][2025-06-24 21:53:26,200][[ConnectionThread_34 (00:16:3E:20:79:68)] - Reading server-config.xml from /root/server-config.xml
[ERROR][2025-06-24 21:53:26,202][[ConnectionThread_34 (00:16:3E:20:79:68)] - ***** PRIVATE KEY LOCATION NOT DEFINED FOR 10.107.200.100  IN CONFIGURATION FILE *******
[INFO][2025-06-24 21:53:26,217][[ConnectionThread_34 (00:16:3E:20:79:68)] - SSH port is set from Automatics property
[INFO][2025-06-24 21:53:26,397][[ConnectionThread_34 (00:16:3E:20:79:68)] - SSH port is set from Automatics property
[INFO][2025-06-24 21:53:31,477][[ConnectionThread_34 (00:16:3E:20:79:68)] - Connectiongateway iscom.automatics.providers.connection.SshConnection@31a6ae7a
[INFO][2025-06-24 21:53:31,477][[ConnectionThread_34 (00:16:3E:20:79:68)] - inside null != connectionGateway condition
[INFO][2025-06-24 21:53:31,478][[ConnectionThread_34 (00:16:3E:20:79:68)] - gateWayDeviceInputStream iscom.jcraft.jsch.Channel$MyPipedInputStream@627797e7
[INFO][2025-06-24 21:53:31,482][[ConnectionThread_34 (00:16:3E:20:79:68)] - Settoptrace debugging:Inside else block
[INFO][2025-06-24 21:53:31,482][[ConnectionThread_34 (00:16:3E:20:79:68)] - Entered into readOutputFromChannel method
[INFO][2025-06-24 21:53:31,484][[ConnectionThread_34 (00:16:3E:20:79:68)] - Is RDKV Client trace false
[INFO][2025-06-24 21:53:31,503][[PollingThread_39_(00:16:3E:20:79:68)] - SSH port is set from Automatics property
[INFO][2025-06-24 21:53:31,574][[PollingThread_39_(00:16:3E:20:79:68)] - SSH port is set from Automatics property
[INFO][2025-06-24 21:53:56,193][[pool-4-thread-1] - Is trace required for connected gateway: false
[INFO][2025-06-24 21:53:56,193][[pool-4-thread-1] - Is trace required for connected gateway: false
[INFO][2025-06-24 21:53:59,187][[com.automatics.executor.Starter.main()] - Starting testing on class: org.testng.TestRunner
[INFO][2025-06-24 21:53:59,206][[com.automatics.executor.Starter.main()] - Doing initialization for 00:16:3E:20:79:68
[INFO][2025-06-24 21:53:59,217][[TestNG-PoolService-0] - >>>[BEFORE_METHOD]: Perform before method initialization 00:16:3E:20:79:68
[INFO][2025-06-24 21:53:59,217][[TestNG-PoolService-0] - Setting dattime in patter yyyy-MM-dd HH:mm:ss
[INFO][2025-06-24 21:53:59,219][[TestNG-PoolService-0] - startTime 2025-06-24 21:53:59
[INFO][2025-06-24 21:53:59,219][[TestNG-PoolService-0] - >>>[BEFORE_METHOD]: Sending test exection start time to Automatics 00:16:3E:20:79:68
[INFO][2025-06-24 21:53:59,220][[TestNG-PoolService-0] - http://localhost:8080/Automatics/captureTestTriggerTime.htm
[INFO][2025-06-24 21:53:59,221][[TestNG-PoolService-0] - {"jobId":0,"automationId":"TC-RDKB-WEBPA-1003","macAddress":"00:16:3E:20:79:68","startDateTimeEST":1750802039220,"endDateTimeEST":0}
[INFO][2025-06-24 21:53:59,434][[TestNG-PoolService-0] - Capture execution time - Response : HTTP/1.1 400
[INFO][2025-06-24 21:53:59,434][00:16:3E:20:79:68[TestNG-PoolService-0] - Skipping partner specific before method initialization as it is not configured.
21:53:59,434 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - About to instantiate appender of type [ch.qos.logback.core.FileAppender]
21:53:59,434 |-INFO in ch.qos.logback.core.joran.action.AppenderAction - Naming appender as [FILE-Rpi-RDKB-00163E207968]
21:53:59,435 |-INFO in ch.qos.logback.core.FileAppender[FILE-Rpi-RDKB-00163E207968] - File property is set to [target/logs/Rpi-RDKB-00163E207968.log]
[INFO][2025-06-24 21:53:59,435][00:16:3E:20:79:68[TestNG-PoolService-0] - >>>[BEFORE_METHOD]: Extending allocation before method for testType : GROUP_OR_AUTOID 00:16:3E:20:79:68
[INFO][2025-06-24 21:53:59,436][00:16:3E:20:79:68[TestNG-PoolService-0] -  Get the locked status: false
[INFO][2025-06-24 21:53:59,436][00:16:3E:20:79:68[TestNG-PoolService-0] - Is trace required for connected gateway: false
[INFO][2025-06-24 21:53:59,436][00:16:3E:20:79:68[TestNG-PoolService-0] - Is trace required for connected gateway: false
[INFO][2025-06-24 21:53:59,437][00:16:3E:20:79:68[TestNG-PoolService-0] - <a name="com.automatics.rdkb.tests.webpa.BroadBandWebPaTests.testVerifyWebPAVersion">STARTED - testVerifyWebPAVersion - com.automatics.device.Device@4b05e2da</a>
[INFO][2025-06-24 21:53:59,437][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Getting MDC = 00163E207968settop_trace.log
[INFO][2025-06-24 21:53:59,437][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Getting MDC = 00:16:3E:20:79:68
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - #######################################################################################
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - STARTING TEST CASE: TC-RDKB-WEBPA-1003
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - TEST DESCRIPTION: Verify the retrieval of webpa version from tr181 parameter
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - TEST STEPS :
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - 1. Verify WebPA version obtained using WebPA request.
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - #######################################################################################
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - *****************************************************************************************
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - STEP 1: DESCRIPTION : Verify WebPA version obtained using WebPA request.
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - STEP 1: ACTION : ACTION: Execute the TR-181 parameter-Device.X_RDKCENTRAL-COM_Webpa.Version.
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - STEP 1: EXPECTED : WebPA request response contains WebPA version.
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - *****************************************************************************************
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - TR181 Access Method configured in Automatics Props: null
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - TR181 Access Method going to use: DMCLI
[INFO][2025-06-24 21:53:59,440][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - TR181 Access Method: DMCLI
[INFO][2025-06-24 21:53:59,441][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Going to find protocol specific names
[INFO][2025-06-24 21:53:59,442][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Going to execute commands
[INFO][2025-06-24 21:53:59,451][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - SSH port is set from Automatics property
[INFO][2025-06-24 21:53:59,513][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Executing command: dmcli eRT getv Device.X_RDKCENTRAL-COM_Webpa.Version
[INFO][2025-06-24 21:53:59,637][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] -
<===========================  RESPONSE =======================>
CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.X_RDKCENTRAL-COM_Webpa.Version
               type:     string,    value: WEBPA-2.0-1.0.2-352-gba76ce8

<=============================================================>
[INFO][2025-06-24 21:53:59,639][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Dmcli response : CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.X_RDKCENTRAL-COM_Webpa.Version
               type:     string,    value: WEBPA-2.0-1.0.2-352-gba76ce8
[INFO][2025-06-24 21:53:59,640][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Dmcli param value : WEBPA-2.0-1.0.2-352-gba76ce8
[INFO][2025-06-24 21:53:59,641][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - TR181 Response : [tableName=null, index=null, name=Device.X_RDKCENTRAL-COM_Webpa.Version, protocolSpecificParamName=Device.X_RDKCENTRAL-COM_Webpa.Version, value=WEBPA-2.0-1.0.2-352-gba76ce8, datatype=null, statusCode=0]
[INFO][2025-06-24 21:53:59,642][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - STARTING METHOD: patternFinderToReturnAllMatchedString()
[INFO][2025-06-24 21:53:59,643][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - ENDING METHOD: patternFinderToReturnAllMatchedString()
[INFO][2025-06-24 21:53:59,644][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - STEP 1: ACTUAL : WebPA request response contains WebPA version: 2.0
[INFO][2025-06-24 21:53:59,645][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - **********************************************************************************
[INFO][2025-06-24 21:53:59,648][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - [STB MAC : 00:16:3E:20:79:68][ Manual test ID : TC-RDKB-WEBPA-003] [step Number : S1][ Execution status : PASS] [Error Message : ]
[INFO][2025-06-24 21:53:59,651][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Entered into updateExecutionStatus method
[INFO][2025-06-24 21:53:59,652][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Fetching device property: FIRMWARE_VERSION
[INFO][2025-06-24 21:53:59,659][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Fetching device props for 00:16:3E:20:79:68 for props [FIRMWARE_VERSION] Url Path: http://localhost:8080/DeviceManager/deviceManagement/getDeviceProps
[INFO][2025-06-24 21:53:59,672][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Response: {"mac":"00:16:3E:20:79:68","HEAD_END":null,"FIRMWARE_VERSION":"Rpi-RDKB","ECM_IP_ADDRESS":null,"ESTB_IP_ADDRESS":null}
[INFO][2025-06-24 21:53:59,672][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Getting value for property: FIRMWARE_VERSION
[INFO][2025-06-24 21:53:59,672][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Value: Rpi-RDKB
[INFO][2025-06-24 21:53:59,672][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Device property name: FIRMWARE_VERSION value obtained: Rpi-RDKB
[INFO][2025-06-24 21:53:59,675][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Result Details ->{"manualId":"TC-RDKB-WEBPA-003","stepNumber":"S1","testType":"GROUP_OR_AUTOID","buildName":"Rpi-RDKB","macAddress":"00:16:3E:20:79:68","remarks":"","executionStatus":"PASS","skipRemaining":true,"partnerName":"","automationId":"TC-RDKB-WEBPA-1003"}
[ERROR][2025-06-24 21:53:59,680][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - FAILED TO UPDATE EXECUTION RESULT.Kindly check if this manual id and step are added in Automatics - Manage scripts against the automation id
[INFO][2025-06-24 21:53:59,681][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Exited from updateExecutionStatus method
[INFO][2025-06-24 21:53:59,681][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - ENDING TEST CASE: TC-RDKB-WEBPA-1003
[INFO][2025-06-24 21:53:59,683][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - >>>[AFTER_METHOD]: Clear device trace buffer for 00:16:3E:20:79:68
[INFO][2025-06-24 21:53:59,683][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - NewLocation for log saving logs  /root/rdkb-tests/target/TC-RDKB-WEBPA-1003/00163E207968/settoptrace/
[INFO][2025-06-24 21:53:59,683][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - New trace location from the strings /root/rdkb-tests/target/settoptrace/00163E207968settop_trace.log
[INFO][2025-06-24 21:53:59,687][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Writing stated from line
[INFO][2025-06-24 21:53:59,763][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - [ HTML LOG PARSER ] : End of log parser Tue Jun 24 21:53:59 GMT 2025
[INFO][2025-06-24 21:53:59,763][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - NewLocation for log saving logs  /root/rdkb-tests/target/TC-RDKB-WEBPA-1003/00163E207968/logs/
[INFO][2025-06-24 21:53:59,764][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Writing stated from line
[INFO][2025-06-24 21:53:59,779][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - [ HTML LOG PARSER ] : End of log parser Tue Jun 24 21:53:59 GMT 2025
[INFO][2025-06-24 21:53:59,780][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - >>>[AFTER_METHOD]: Sending test execution completion time for 00:16:3E:20:79:68
[INFO][2025-06-24 21:53:59,780][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - http://localhost:8080/Automatics/captureTestTriggerTime.htm
[INFO][2025-06-24 21:53:59,780][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - {"jobId":0,"automationId":"TC-RDKB-WEBPA-1003","macAddress":"00:16:3E:20:79:68","startDateTimeEST":0,"endDateTimeEST":1750802039780}
[INFO][2025-06-24 21:53:59,782][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Capture execution time - Response : HTTP/1.1 400
[INFO][2025-06-24 21:53:59,782][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Restarting Trace in after method
[INFO][2025-06-24 21:53:59,782][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Is trace required for connected gateway: false
[INFO][2025-06-24 21:53:59,783][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Is trace required for connected gateway: false
[INFO][2025-06-24 21:53:59,783][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Going for if build changed : Test Type : GROUP_OR_AUTOID
[INFO][2025-06-24 21:53:59,783][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Skipping build change verification as partner specific initialization is not configured.
[INFO][2025-06-24 21:53:59,783][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - >>>[AFTER_METHOD]: Build Change Status: NO_CHANGE
[INFO][2025-06-24 21:53:59,783][00:16:3E:20:79:68[TC-RDKB-WEBPA-1003 : 00163E207968] - Skipping parter specific after method clean up as it is not configured.
===== Invoked methods
  AutomaticsTestBase.performBeforeSuiteInit(org.testng.ITestContext)[pri:0, instance:com.automatics.rdkb.tests.webpa.BroadBandWebPaTests@ea56bd5]org.testng.TestRunner@6f6f8534  245722069
  AutomaticsTestBase.performBeforeMethodInit([Ljava.lang.Object;, org.testng.ITestResult)[pri:0, instance:com.automatics.rdkb.tests.webpa.BroadBandWebPaTests@ea56bd5][Ljava.lang.Object;@120cd79e [TestResult name={null} status=CREATED method=BroadBandWebPaTests.testVerifyWebPAVersion(com.automatics.device.Dut)[pri:0, instance:com.automatics.rdkb.tests.webpa.BroadBandWebPaTests@ea56bd5] output={null}]  245722069
    BroadBandWebPaTests.testVerifyWebPAVersion(com.automatics.device.Dut)[pri:0, instance:com.automatics.rdkb.tests.webpa.BroadBandWebPaTests@ea56bd5]com.automatics.device.Device@4b05e2da  245722069
  AutomaticsTestBase.performAfterMethodCleanup([Ljava.lang.Object;, org.testng.ITestResult)[pri:0, instance:com.automatics.rdkb.tests.webpa.BroadBandWebPaTests@ea56bd5][Ljava.lang.Object;@120cd79e [TestResult name=testVerifyWebPAVersion status=SUCCESS method=BroadBandWebPaTests.testVerifyWebPAVersion(com.automatics.device.Dut)[pri:0, instance:com.automatics.rdkb.tests.webpa.BroadBandWebPaTests@ea56bd5] output={null}]  245722069
=====
PASSED: testVerifyWebPAVersion(com.automatics.device.Device@4b05e2da)

===============================================
    MyTest
    Tests run: 1, Failures: 0, Skips: 0
===============================================

[INFO][2025-06-24 21:53:59,794][[com.automatics.executor.Starter.main()] - Finished testing class: org.testng.TestRunner
[INFO][2025-06-24 21:53:59,795][[com.automatics.executor.Starter.main()] - >>>[AFTER-SUITE]: Performing after suite cleanup
[INFO][2025-06-24 21:53:59,795][[com.automatics.executor.Starter.main()] - Bean testInitializer is not configured.
[INFO][2025-06-24 21:53:59,795][[com.automatics.executor.Starter.main()] - >>>[AFTER-SUITE]: Locked devices after suite execution 1
[INFO][2025-06-24 21:53:59,796][[com.automatics.executor.Starter.main()] - Value of intial testType : QUICK
[INFO][2025-06-24 21:53:59,796][[com.automatics.executor.Starter.main()] - Value of TestType provided by job : GROUP_OR_AUTOID
[INFO][2025-06-24 21:53:59,796][[com.automatics.executor.Starter.main()] - >>>[AFTER-SUITE]: Verifying if build changed after test
[INFO][2025-06-24 21:53:59,796][[com.automatics.executor.Starter.main()] - Skipping build change verification as partner specific initialization is not configured.
[INFO][2025-06-24 21:53:59,796][[com.automatics.executor.Starter.main()] - >>>[AFTER-SUITE]: Build Change Status: NO_CHANGE
[INFO][2025-06-24 21:53:59,796][[com.automatics.executor.Starter.main()] - Is trace required for connected gateway: false
[ERROR][2025-06-24 21:53:59,796][[PollingThread_39_(00:16:3E:20:79:68)] - Sleep interrupted sleep interrupted
[INFO][2025-06-24 21:53:59,797][[com.automatics.executor.Starter.main()] - Connection instance is Null
[INFO][2025-06-24 21:53:59,797][[com.automatics.executor.Starter.main()] - Connection instance is Null
[INFO][2025-06-24 21:53:59,797][[com.automatics.executor.Starter.main()] - Is trace required for connected gateway: false
[INFO][2025-06-24 21:53:59,797][[com.automatics.executor.Starter.main()] - Skipping parter specific after suite clean up as it is not configured.
[ERROR][2025-06-24 21:53:59,797][[ConnectionThread_34 (00:16:3E:20:79:68)] - readOutputFromChannel - Exception Details ------
java.io.InterruptedIOException: null
        at java.base/java.io.PipedInputStream.read(PipedInputStream.java:328)
        at java.base/java.io.PipedInputStream.read(PipedInputStream.java:377)
        at java.base/sun.nio.cs.StreamDecoder.readBytes(StreamDecoder.java:287)
        at java.base/sun.nio.cs.StreamDecoder.implRead(StreamDecoder.java:330)
        at java.base/sun.nio.cs.StreamDecoder.read(StreamDecoder.java:190)
        at java.base/java.io.InputStreamReader.read(InputStreamReader.java:177)
        at java.base/java.io.BufferedReader.fill(BufferedReader.java:162)
        at java.base/java.io.BufferedReader.readLine(BufferedReader.java:329)
        at java.base/java.io.BufferedReader.readLine(BufferedReader.java:396)
        at com.automatics.providers.trace.AbstractTraceProviderImpl.readOutputFromChannel(AbstractTraceProviderImpl.java:820)
        at com.automatics.providers.trace.AbstractTraceProviderImpl.connectAndRead(AbstractTraceProviderImpl.java:734)
        at com.automatics.providers.trace.AbstractTraceProviderImpl$ConnectionThread.run(AbstractTraceProviderImpl.java:1135)
[INFO][2025-06-24 21:53:59,798][[ConnectionThread_34 (00:16:3E:20:79:68)] - Connection instance is Null
[INFO][2025-06-24 21:53:59,798][[ConnectionThread_34 (00:16:3E:20:79:68)] - Connection instance is Null
[INFO][2025-06-24 21:53:59,798][[ConnectionThread_34 (00:16:3E:20:79:68)] - Exited from readOutputFromChannel method
[INFO][2025-06-24 21:53:59,805][[com.automatics.executor.Starter.main()] - Releasing device 00:16:3E:20:79:68 Url Path: http://localhost:8080/DeviceManager/deviceManagement/device/release
[INFO][2025-06-24 21:53:59,854][[com.automatics.executor.Starter.main()] - Response: {"status":"SUCCESS","mac":"00:16:3E:20:79:68"}
[INFO][2025-06-24 21:53:59,858][[com.automatics.executor.Starter.main()] - Successfully unlocked RDKB (00:16:3E:20:79:68) mapped components -
[INFO][2025-06-24 21:53:59,858][[com.automatics.executor.Starter.main()] - SETTOP - 00:16:3E:20:79:68 RELEASED.
[INFO][2025-06-24 21:53:59,859][[com.automatics.executor.Starter.main()] - [AFTER-SUITE:]JSON message to Automatics: {"status":"COMPLETED","service":"","buildImageName":"Rpi-RDKB","settopList":["00:16:3E:20:79:68"],"startTime":1750802006182,"completionTime":1750802039858,"JMD_ID":0,"updateRdkPortal":false,"result":{"build_name":"Rpi-RDKB","type":"GROUP_OR_AUTOID","tests":[]}}
[INFO][2025-06-24 21:53:59,872][[com.automatics.executor.Starter.main()] - [ HTML LOG PARSER ] : line [INFO][2025-06-24 21:53:59,437][][00:16:3E:20:79:68|TestNG-PoolService-0|com.automatics.executor.AutomaticsTestListener:onTestStart:110] <a name="com.automatics.rdkb.tests.webpa.BroadBandWebPaTests.testVerifyWebPAVersion">STARTED - testVerifyWebPAVersion - com.automatics.device.Device@4b05e2da</a>
[INFO][2025-06-24 21:53:59,872][[com.automatics.executor.Starter.main()] - [ HTML LOG PARSER ] : line [DEBUG][2025-06-24 21:53:59,437][][00:16:3E:20:79:68|TC-RDKB-WEBPA-1003 : 00163E207968|com.automatics.executor.AutomaticsTestListener:onTestStart:150] Started appending log

===============================================
MySuite
Total tests run: 1, Passes: 1, Failures: 0, Skips: 0
===============================================

[INFO][2025-06-24 21:53:59,907][[com.automatics.executor.Starter.main()] - Updating final execution status to Automatics
[INFO][2025-06-24 21:53:59,908][[Thread-17] - ============= MESSAGE SEND TO AUTOMATICS ==============
[INFO][2025-06-24 21:53:59,908][[Thread-17] - Tested build name : Rpi-RDKB
[INFO][2025-06-24 21:53:59,908][[Thread-17] - Final execution status : COMPLETED
[INFO][2025-06-24 21:53:59,908][[Thread-17] - Final successful device list : ["00:16:3E:20:79:68"]
[INFO][2025-06-24 21:53:59,908][[Thread-17] - Job Id : 0
[INFO][2025-06-24 21:53:59,908][[Thread-17] - ==============================================================

[INFO][2025-06-24 21:53:59,909][[Thread-17] - >>>[INIT]: Automatics JSON ->
{"status":"COMPLETED","service":"","buildImageName":"Rpi-RDKB","settopList":["00:16:3E:20:79:68"],"startTime":1750802006182,"completionTime":1750802039858,"JMD_ID":0,"updateRdkPortal":false,"result":{"build_name":"Rpi-RDKB","type":"GROUP_OR_AUTOID","tests":[]}}
[INFO][2025-06-24 21:53:59,909][[Thread-17] - http://localhost:8080/Automatics/executionResponse.htm
[INFO][2025-06-24 21:53:59,912][[Thread-17] - HTTP STATUS LINE : HTTP/1.1 200
[INFO][2025-06-24 21:53:59,913][[Thread-17] - HTTP STATUS CODE : 200
[INFO][2025-06-24 21:53:59,913][[com.automatics.executor.Starter.main()] - ********  EXECUTION COMPLETED *********
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  39.413 s
[INFO] Finished at: 2025-06-24T21:53:59Z
[INFO] ------------------------------------------------------------------------
Inside Add Shutdown Hook
[INFO][2025-06-24 21:53:59,917][[Thread-2] - Bean testInitializer is not configured.
[INFO][2025-06-24 21:53:59,917][[Thread-2] - Closing partner application context
[INFO][2025-06-24 21:53:59,918][[Thread-2] - Closing core application context
```
</details>


# Automatics Test Case Extractor

browse, search, and inspect actual rdkb test case implementations

```text
git clone https://code.rdkcentral.com/r/rdk/tools/automatics/rdkb-tests
cd rdkb-tests
test-case-extractor.py -d src/test/java/com/automatics/rdkb/tests/
```

