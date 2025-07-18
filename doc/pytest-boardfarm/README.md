![Pytest Boardfarm Diagram](pytest-boardfarm.svg)

# Installation

## Run the boardfarm.sh script:

```text
boardfarm.sh

lxc list
+-----------------+---------+--------------------------------+-----------------------------+
| boardfarm       | RUNNING | 10.0.3.84 (eth0)               | fd42:4c81:5770:1762::84 (eth0) |
+-----------------+---------+--------------------------------+-----------------------------+
```

## Enter boardfarm container (shell):

```text
$ lxc exec boardfarm bash
[root@boardfarm ~]# 
```

# LXD Certificate Setup

The boardfarm container is automatically configured with LXD client certificates for API access to test containers.

## Verify LXD API Connection:

```text
[root@boardfarm ~]# curl -s -k --cert /root/.config/lxc/client.crt --key /root/.config/lxc/client.key https://192.168.2.120:8443/1.0/containers
{
  "type": "sync",
  "status": "Success",
  "status_code": 200,
  "operation": "",
  "error_code": 0,
  "error": "",
  "metadata": [
    "/1.0/containers/acs",
    "/1.0/containers/automatics",
    "/1.0/containers/bng-7",
    "/1.0/containers/boardfarm",
    "/1.0/containers/vcpe",
    "/1.0/containers/genieacs",
    "/1.0/containers/oktopus",
    "/1.0/containers/webpa",
    "/1.0/containers/xconf",
    "/1.0/containers/telemetry"
  ]
}
```

# Device Testing with Pytest

This test environment connects to LXD containers and runs automated tests on virtual devices.

## Verify boardfarm installation:

```text
[root@boardfarm ~]# cd boardfarm
[root@boardfarm boardfarm]# python3 -c "import boardfarm; print('Boardfarm installed successfully')"
Boardfarm installed successfully
```

## Configure test environment:

The container comes pre-configured with:
- Boardfarm 3.x framework
- pytest-boardfarm plugin
- LXD device configurations for VCPE testing
- Certificate-based authentication to LXD API

## Run basic device tests:

```text
[root@boardfarm boardfarm]# pytest -c boardfarm/vcpe/vcpe_only_pytest.ini boardfarm/vcpe/tests/vcpe_only_tests/
```

<details>
<summary>Click to expand test execution</summary>

```text
root@boardfarm:~# pytest -c boardfarm/vcpe/vcpe_only_pytest.ini boardfarm/vcpe/tests/vcpe_only_tests/
=============================================================================================================================== test session starts ================================================================================================================================
platform linux -- Python 3.11.13, pytest-8.4.1, pluggy-1.6.0 -- /usr/bin/python3.11
cachedir: .pytest_cache
metadata: {'Python': '3.11.13', 'Platform': 'Linux-6.8.0-64-generic-x86_64-with-glibc2.35', 'Packages': {'pytest': '8.4.1', 'pluggy': '1.6.0'}, 'Plugins': {'instafail': '0.5.0', 'cov': '6.2.1', 'metadata': '3.1.1', 'html': '4.1.1', 'mock': '3.14.1', 'pytest_boardfarm3': '2025.7.10a0', 'randomly': '3.16.0', 'anyio': '4.9.0'}}
Using --randomly-seed=739018461
rootdir: /root/boardfarm/vcpe
configfile: vcpe_only_pytest.ini
plugins: instafail-0.5.0, cov-6.2.1, metadata-3.1.1, html-4.1.1, mock-3.14.1, pytest_boardfarm3-2025.7.10a0, randomly-3.16.0, anyio-4.9.0
collected 28 items
2025-07-18 22:00:36,430 DEBUG   - Using selector: EpollSelector                                                                         (asyncio:__init__:54)
2025-07-18 22:00:36,431 DEBUG   - boardfarm_skip_boot ran for 5.14089997523115e-05s.                                                    (boardfarm3.plugins.setup_environment:_run_hook_async:68)

boardfarm/vcpe/tests/vcpe_only_tests/test_lxd_power_cycle.py::TestLXDPowerCycle::test_lxd_console_reconnection_logic 2025-07-18 22:00:36,437 INFO    - Starting LXD console reconnection logic test                                                          (vcpe_only_tests.test_lxd_power_cycle:test_lxd_console_reconnection_logic:236)
2025-07-18 22:00:36,437 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_lxd_power_cycle:test_lxd_console_reconnection_logic:239)
2025-07-18 22:00:36,438 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:00:36,438 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:36,893 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:36,894 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:00:37,079 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:00:37,079 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:00:37,255 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:00:37,432 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:00:37,601 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:00:37,601 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:00:37,946 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:00:37,947 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:00:37,947 INFO    - VCPE device booted successfully                                                                       (vcpe_only_tests.test_lxd_power_cycle:test_lxd_console_reconnection_logic:244)
2025-07-18 22:00:37,948 INFO    - Testing console disconnect and reconnect logic                                                        (vcpe_only_tests.test_lxd_power_cycle:test_lxd_console_reconnection_logic:253)
2025-07-18 22:00:38,122 INFO    - ✓ Console responsive before disconnect                                                                (vcpe_only_tests.test_lxd_power_cycle:test_lxd_console_reconnection_logic:262)
2025-07-18 22:00:38,224 INFO    - ✓ Console disconnected                                                                                (vcpe_only_tests.test_lxd_power_cycle:test_lxd_console_reconnection_logic:266)
2025-07-18 22:00:38,225 WARNING - Console still accessible after disconnect (may be cached)                                             (vcpe_only_tests.test_lxd_power_cycle:test_lxd_console_reconnection_logic:272)
2025-07-18 22:00:38,225 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:38,496 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:38,497 INFO    - ✓ Console reconnected                                                                                 (vcpe_only_tests.test_lxd_power_cycle:test_lxd_console_reconnection_logic:278)
2025-07-18 22:00:38,680 INFO    - ✓ Console responsive after reconnect                                                                  (vcpe_only_tests.test_lxd_power_cycle:test_lxd_console_reconnection_logic:284)
2025-07-18 22:00:38,681 INFO    - LXD console reconnection logic test completed successfully                                            (vcpe_only_tests.test_lxd_power_cycle:test_lxd_console_reconnection_logic:286)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_lxd_power_cycle.py::TestLXDPowerCycle::test_lxd_power_cycle_method_availability 2025-07-18 22:00:38,694 INFO    - Starting LXD power cycle method availability test                                                     (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_method_availability:27)
2025-07-18 22:00:38,695 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_method_availability:30)
2025-07-18 22:00:38,696 INFO    - Checking power_cycle method availability                                                              (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_method_availability:33)
2025-07-18 22:00:38,696 INFO    - ✓ power_cycle method is available on hardware component                                               (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_method_availability:38)
2025-07-18 22:00:38,697 INFO    - Container name for power cycle: vcpe                                                                  (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_method_availability:42)
2025-07-18 22:00:38,697 INFO    - LXD power cycle method availability test completed successfully                                       (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_method_availability:45)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_lxd_power_cycle.py::TestLXDPowerCycle::test_lxd_power_cycle_prerequisites 2025-07-18 22:00:38,706 INFO    - Starting LXD power cycle prerequisites test                                                           (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_prerequisites:113)
2025-07-18 22:00:38,707 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_prerequisites:116)
2025-07-18 22:00:38,707 INFO    - Checking LXD REST API prerequisites                                                                   (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_prerequisites:119)
2025-07-18 22:00:38,708 INFO    - LXD endpoint configured: https://192.168.2.120:8443                                                   (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_prerequisites:123)
2025-07-18 22:00:38,708 INFO    - ✓ Client certificate authentication configured: cert=.config/lxc/client.crt, key=.config/lxc/client.key  (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_prerequisites:135)
2025-07-18 22:00:38,709 INFO    - Container name configured: vcpe                                                                       (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_prerequisites:144)
2025-07-18 22:00:38,709 INFO    - Expected power cycle API URL: https://192.168.2.120:8443/1.0/containers/vcpe/state                    (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_prerequisites:152)
2025-07-18 22:00:38,710 INFO    - ✓ LXD REST API configuration appears valid                                                            (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_prerequisites:161)
2025-07-18 22:00:38,711 INFO    - LXD power cycle prerequisites test completed successfully                                             (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_prerequisites:162)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_lxd_power_cycle.py::TestLXDPowerCycle::test_lxd_device_uptime_before_after_concept 2025-07-18 22:00:38,719 INFO    - Starting LXD device uptime concept test                                                               (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:57)
2025-07-18 22:00:38,720 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:60)
2025-07-18 22:00:38,720 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:00:38,721 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:39,089 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:39,090 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:00:39,269 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:00:39,270 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:00:39,446 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:00:39,621 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:00:39,792 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:00:39,793 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:00:40,143 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:00:40,144 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:00:40,144 INFO    - VCPE device booted successfully                                                                       (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:65)
2025-07-18 22:00:40,144 INFO    - Getting initial device uptime                                                                         (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:74)
2025-07-18 22:00:40,310 INFO    - Current device uptime: 92125.84 seconds (25.59 hours)                                                 (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:82)
2025-07-18 22:00:40,480 INFO    - System boot time: STDERR: who: invalid option -- 'b'
BusyBox v1.35.0 () multi-call binary.

Usage: who [-aH]  (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:90)
2025-07-18 22:00:40,481 INFO    - NOTE: In a real power cycle test, we would:                                                           (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:94)
2025-07-18 22:00:40,481 INFO    - 1. Record current uptime                                                                              (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:95)
2025-07-18 22:00:40,481 INFO    - 2. Call vcpe_device.hw.power_cycle()                                                                  (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:96)
2025-07-18 22:00:40,482 INFO    - 3. Wait for device to come back online                                                                (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:97)
2025-07-18 22:00:40,482 INFO    - 4. Verify new uptime is less than original uptime                                                     (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:98)
2025-07-18 22:00:40,482 INFO    - LXD device uptime concept test completed successfully                                                 (vcpe_only_tests.test_lxd_power_cycle:test_lxd_device_uptime_before_after_concept:104)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_lxd_power_cycle.py::TestLXDPowerCycle::test_lxd_power_cycle_error_handling 2025-07-18 22:00:40,491 INFO    - Starting LXD power cycle error handling test                                                          (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_error_handling:171)
2025-07-18 22:00:40,491 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_error_handling:174)
2025-07-18 22:00:40,492 INFO    - Testing power cycle error handling with invalid container name                                        (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_error_handling:177)
2025-07-18 22:00:40,492 INFO    - Testing power cycle with invalid container name: non-existent-container-12345                         (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_error_handling:188)
2025-07-18 22:00:40,493 INFO    - Power cycling LXD container: non-existent-container-12345 via REST API                                (boardfarm.vcpe.devices.lxd_device:power_cycle:169)
2025-07-18 22:00:40,493 INFO    - Disconnecting from console before restart                                                             (boardfarm.vcpe.devices.lxd_device:power_cycle:174)
2025-07-18 22:00:40,605 INFO    - Sending restart request to: https://192.168.2.120:8443/1.0/containers/non-existent-container-12345/state  (boardfarm.vcpe.devices.lxd_device:power_cycle:195)
2025-07-18 22:00:40,623 ERROR   - LXD API connection error for non-existent-container-12345: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate (_ssl.c:1016)  (boardfarm.vcpe.devices.lxd_device:power_cycle:255)
2025-07-18 22:00:40,624 INFO    - ✓ Power cycle correctly raised exception: LXD API connection error for non-existent-container-12345: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate (_ssl.c:1016)  (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_error_handling:194)
2025-07-18 22:00:40,624 INFO    - Testing power cycle error handling with invalid endpoint                                              (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_error_handling:199)
2025-07-18 22:00:40,625 INFO    - Power cycling LXD container: vcpe via REST API                                                        (boardfarm.vcpe.devices.lxd_device:power_cycle:169)
2025-07-18 22:00:40,625 INFO    - Disconnecting from console before restart                                                             (boardfarm.vcpe.devices.lxd_device:power_cycle:174)
2025-07-18 22:00:40,636 INFO    - Sending restart request to: https://invalid-host:8443/1.0/containers/vcpe/state                       (boardfarm.vcpe.devices.lxd_device:power_cycle:195)
2025-07-18 22:00:40,643 ERROR   - LXD API connection error for vcpe: [Errno -3] Temporary failure in name resolution                    (boardfarm.vcpe.devices.lxd_device:power_cycle:255)
2025-07-18 22:00:40,643 INFO    - ✓ Power cycle correctly raised exception for invalid endpoint: LXD API connection error for vcpe: [Errno -3] Temporary failure in name resolution  (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_error_handling:211)
2025-07-18 22:00:40,644 INFO    - LXD power cycle error handling test completed successfully                                            (vcpe_only_tests.test_lxd_power_cycle:test_lxd_power_cycle_error_handling:227)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_operations.py::TestDMCLIOperations::test_dmcli_parameter_attributes 2025-07-18 22:00:40,653 INFO    - Starting DMCLI parameter attributes test                                                              (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_attributes:238)
2025-07-18 22:00:40,654 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_attributes:241)
2025-07-18 22:00:40,654 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:00:40,655 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:40,910 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:40,911 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:00:41,088 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:00:41,089 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:00:41,267 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:00:41,438 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:00:41,618 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:00:41,619 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:00:41,964 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:00:41,965 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:00:41,965 INFO    - Testing DMCLI getattributes for parameter attributes                                                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_attributes:258)
2025-07-18 22:00:41,966 DEBUG   - Executing dmcli command: dmcli eRT getattributes Device.DeviceInfo.SoftwareVersion                    (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:42,176 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
getattributes from/to component(eRT.com.cisco.spvtg.ccsp.pam): Device.DeviceInfo.SoftwareVersion
Execution succeed.
Parameter    1 name: Device.DeviceInfo.SoftwareVersion
        notification:off, accessControlChanged:anybody.

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:42,177 INFO    - getattributes(Device.DeviceInfo.SoftwareVersion) = {'\x1b[0;32mCR component name is': 'eRT.com.cisco.spvtg.ccsp.CR', '\x1b[0;32mgetattributes from/to component(eRT.com.cisco.spvtg.ccsp.pam)': 'Device.DeviceInfo.SoftwareVersion', '\x1b[0;32mParameter    1 name': 'Device.DeviceInfo.SoftwareVersion\x1b[0;33m', 'notification': 'off, accessControlChanged:anybody.'}  (boardfarm.vcpe.lib.dmcli_command:getattributes:205)
2025-07-18 22:00:42,178 INFO    - ✓ Attributes for Device.DeviceInfo.SoftwareVersion: {'\x1b[0;32mCR component name is': 'eRT.com.cisco.spvtg.ccsp.CR', '\x1b[0;32mgetattributes from/to component(eRT.com.cisco.spvtg.ccsp.pam)': 'Device.DeviceInfo.SoftwareVersion', '\x1b[0;32mParameter    1 name': 'Device.DeviceInfo.SoftwareVersion\x1b[0;33m', 'notification': 'off, accessControlChanged:anybody.'}  (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_attributes:272)
2025-07-18 22:00:42,178 DEBUG   - Executing dmcli command: dmcli eRT getattributes Device.DeviceInfo.SerialNumber                       (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:42,354 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
getattributes from/to component(eRT.com.cisco.spvtg.ccsp.pam): Device.DeviceInfo.SerialNumber
Execution succeed.
Parameter    1 name: Device.DeviceInfo.SerialNumber
        notification:off, accessControlChanged:anybody.

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:42,355 INFO    - getattributes(Device.DeviceInfo.SerialNumber) = {'\x1b[0;32mCR component name is': 'eRT.com.cisco.spvtg.ccsp.CR', '\x1b[0;32mgetattributes from/to component(eRT.com.cisco.spvtg.ccsp.pam)': 'Device.DeviceInfo.SerialNumber', '\x1b[0;32mParameter    1 name': 'Device.DeviceInfo.SerialNumber\x1b[0;33m', 'notification': 'off, accessControlChanged:anybody.'}  (boardfarm.vcpe.lib.dmcli_command:getattributes:205)
2025-07-18 22:00:42,355 INFO    - ✓ Attributes for Device.DeviceInfo.SerialNumber: {'\x1b[0;32mCR component name is': 'eRT.com.cisco.spvtg.ccsp.CR', '\x1b[0;32mgetattributes from/to component(eRT.com.cisco.spvtg.ccsp.pam)': 'Device.DeviceInfo.SerialNumber', '\x1b[0;32mParameter    1 name': 'Device.DeviceInfo.SerialNumber\x1b[0;33m', 'notification': 'off, accessControlChanged:anybody.'}  (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_attributes:272)
2025-07-18 22:00:42,356 DEBUG   - Executing dmcli command: dmcli eRT getattributes Device.DeviceInfo.Description                        (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:42,526 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
getattributes from/to component(eRT.com.cisco.spvtg.ccsp.pam): Device.DeviceInfo.Description
Execution succeed.
Parameter    1 name: Device.DeviceInfo.Description
        notification:off, accessControlChanged:anybody.

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:42,527 INFO    - getattributes(Device.DeviceInfo.Description) = {'\x1b[0;32mCR component name is': 'eRT.com.cisco.spvtg.ccsp.CR', '\x1b[0;32mgetattributes from/to component(eRT.com.cisco.spvtg.ccsp.pam)': 'Device.DeviceInfo.Description', '\x1b[0;32mParameter    1 name': 'Device.DeviceInfo.Description\x1b[0;33m', 'notification': 'off, accessControlChanged:anybody.'}  (boardfarm.vcpe.lib.dmcli_command:getattributes:205)
2025-07-18 22:00:42,527 INFO    - ✓ Attributes for Device.DeviceInfo.Description: {'\x1b[0;32mCR component name is': 'eRT.com.cisco.spvtg.ccsp.CR', '\x1b[0;32mgetattributes from/to component(eRT.com.cisco.spvtg.ccsp.pam)': 'Device.DeviceInfo.Description', '\x1b[0;32mParameter    1 name': 'Device.DeviceInfo.Description\x1b[0;33m', 'notification': 'off, accessControlChanged:anybody.'}  (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_attributes:272)
2025-07-18 22:00:42,528 INFO    - Successfully retrieved attributes for 3/3 parameters                                                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_attributes:292)
2025-07-18 22:00:42,528 INFO    - DMCLI parameter attributes test completed successfully                                                (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_attributes:293)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_operations.py::TestDMCLIOperations::test_dmcli_parameter_discovery 2025-07-18 22:00:42,539 INFO    - Starting DMCLI parameter discovery test                                                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:166)
2025-07-18 22:00:42,540 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:169)
2025-07-18 22:00:42,540 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:00:42,541 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:42,927 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:42,928 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:00:43,116 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:00:43,116 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:00:43,296 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:00:43,475 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:00:43,653 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:00:43,654 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:00:43,992 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:00:43,993 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:00:43,993 INFO    - Testing DMCLI getnames for parameter discovery                                                        (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:186)
2025-07-18 22:00:43,994 DEBUG   - Executing dmcli command: dmcli eRT getnames Device. true                                              (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:44,195 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.SoftwareModules.
        writable:ReadOnly.
Parameter    2 name: Device.CR.
        writable:ReadOnly.
Parameter    3 name: Device.DeviceInfo.
        writable:ReadOnly.
Parameter    4 name: Device.X_RDK_Ethernet.
        writable:ReadOnly.
Parameter    5 name: Device.X_RDK_WanManager.
        writable:ReadOnly.
Parameter    6 name: Device.X_RDK_WanManager.
        writable:ReadOnly.
Parameter    7 name: Device.DHCPv4.
        writable:ReadOnly.
Parameter    8 name: Device.DHCPv6.
        writable:ReadOnly.
Parameter    9 name: Device.X_RDKCENTRAL-COM_DeviceControl.
        writable:ReadOnly.
Parameter   10 name: Device.DeviceInfo.
        writable:ReadOnly.
Parameter   11 name: Device.X_RDKCENTRAL-COM_XPC.
        writable:ReadOnly.
Parameter   12 name: Device.DSLite.
        writable:ReadOnly.
Parameter   13 name: Device.DeviceInfo.
        writable:ReadOnly.
Parameter   14 name: Device.GatewayInfo.
        writable:ReadOnly.
Parameter   15 name: Device.Time.
        writable:ReadOnly.
Parameter   16 name: Device.GRE.
        writable:ReadOnly.
Parameter   17 name: Device.X_RDK_WebUI.
        writable:ReadOnly.
Parameter   18 name: Device.UserInterface.
        writable:ReadOnly.
Parameter   19 name: Device.InterfaceStack.
        writable:ReadOnly.
Parameter   20 name: Device.Ethernet.
        writable:ReadOnly.
Parameter   21 name: Device.PPP.
        writable:ReadOnly.
Parameter   22 name: Device.IP.
        writable:ReadOnly.
Parameter   23 name: Device.Routing.
        writable:ReadOnly.
Parameter   24 name: Device.DNS.
        writable:ReadOnly.
Parameter   25 name: Device.Firewall.
        writable:ReadOnly.
Parameter   26 name: Device.NAT.
        writable:ReadOnly.
Parameter   27 name: Device.DHCPv4.
        writable:ReadOnly.
Parameter   28 name: Device.DHCPv6.
        writable:ReadOnly.
Parameter   29 name: Device.Users.
        writable:ReadOnly.
Parameter   30 name: Device.UPnP.
        writable:ReadOnly.
Parameter   31 name: Device.X_CISCO_COM_DDNS.
        writable:ReadOnly.
Parameter   32 name: Device.DynamicDNS.
        writable:ReadOnly.
Parameter   33 name: Device.X_CISCO_COM_Security.
        writable:ReadOnly.
Parameter   34 name: Device.X_CISCO_COM_DeviceControl.
        writable:ReadOnly.
Parameter   35 name: Device.Bridging.
        writable:ReadOnly.
Parameter   36 name: Device.RouterAdvertisement.
        writable:ReadOnly.
Parameter   37 name: Device.NeighborDiscovery.
        writable:ReadOnly.
Parameter   38 name: Device.IPv6rd.
        writable:ReadOnly.
Parameter   39 name: Device.X_CISCO_COM_MLD.
        writable:ReadOnly.
Parameter   40 name: Device.X_CISCO_COM_Diagnostics.
        writable:ReadOnly.
Parameter   41 name: Device.X_Comcast_com_ParentalControl.
        writable:ReadOnly.
Parameter   42 name: Device.X_CISCO_COM_MultiLAN.
        writable:ReadOnly.
Parameter   43 name: Device.X_COMCAST_COM_GRE.
        writable:ReadOnly.
Parameter   44 name: Device.X_COMCAST-COM_GRE.
        writable:ReadOnly.
Parameter   45 name: Device.X_CISCO_COM_GRE.
        writable:ReadOnly.
Parameter   46 name: Device.X_COMCAST-COM_Xcalibur.
        writable:ReadOnly.
Parameter   47 name: Device.X_RDKCENTRAL-COM_VideoService.
        writable:ReadOnly.
Parameter   48 name: Device.InterfaceStackNumberOfEntries
        writable:ReadOnly.
Parameter   49 name: Device.Hosts.
        writable:ReadOnly.
Parameter   50 name: Device.XHosts.
        writable:ReadOnly.
Parameter   51 name: Device.X_RDKCENTRAL-COM_Report.
        writable:ReadOnly.
Parameter   52 name: Device.ManagementServer.
        writable:ReadOnly.
Parameter   53 name: Device.X_RDK_Xmidt.
        writable:ReadOnly.
Parameter   54 name: Device.ManagementServer.
        writable:ReadOnly.
Parameter   55 name: Device.DeviceInfo.
        writable:ReadOnly.
Parameter   56 name: Device.X_RDKCENTRAL-COM_EthernetWAN.
        writable:ReadOnly.
Parameter   57 name: Device.NotifyComponent.
        writable:ReadOnly.
Parameter   58 name: Device.Diagnostics.
        writable:ReadOnly.
Parameter   59 name: Device.Diagnostics.
        writable:ReadOnly.
Parameter   60 name: Device.X_RDK_DNSInternet.
        writable:ReadOnly.
Parameter   61 name: Device.IP.
        writable:ReadOnly.
Parameter   62 name: Device.DNS.
        writable:ReadOnly.
Parameter   63 name: Device.SelfHeal.
        writable:ReadOnly.
Parameter   64 name: Device.LogBackup.
        writable:ReadOnly.
Parameter   65 name: Device.PowerManagement.
        writable:ReadOnly.
Parameter   66 name: Device.Thermal.
        writable:ReadOnly.
Parameter   67 name: Device.X_RDK_hwHealthTest.
        writable:ReadOnly.
Parameter   68 name: Device.QOS.
        writable:ReadOnly.
Parameter   69 name: Device.DeviceInfo.
        writable:ReadOnly.
Parameter   70 name: Device.Ethernet.
        writable:ReadOnly.
Parameter   71 name: Device.DeviceInfo.
        writable:ReadOnly.
Parameter   72 name: Device.X_RDKCENTRAL-COM_XDNS.
        writable:ReadOnly.
Parameter   73 name: Device.X_RDKCENTRAL-COM_T2.
        writable:ReadOnly.
Parameter   74 name: Device.X_RDK_T2.
        writable:ReadOnly.
Parameter   75 name: Device.X_RDKCENTRAL-COM_Privacy.
        writable:ReadOnly.
Parameter   76 name: Device.X_RDK_WebConfig.
        writable:ReadOnly.
Parameter   77 name: Device.EasyMeshController.
        writable:ReadOnly.
Parameter   78 name: Device.WiFi.
        writable:ReadOnly.
Parameter   79 name: Device.X_RDK_MeshAgent.
        writable:ReadOnly.
Parameter   80 name: Device.DeviceInfo.
        writable:ReadOnly.
Parameter   81 name: Device.Webpa.
        writable:ReadOnly.
Parameter   82 name: Device.X_RDK_Webpa.
        writable:ReadOnly.
Parameter   83 name: Device.X_RDKCENTRAL-COM_Webpa.
        writable:ReadOnly.
Parameter   84 name: Device.DeviceInfo.
        writable:ReadOnly.
Parameter   85 name: Device.WiFi.
        writable:ReadOnly.
Parameter   86 name: Device.Logging.
        writable:ReadOnly.
Parameter   87 name: Device.Cellular.
        writable:ReadOnly.

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:44,197 INFO    - getnames(Device., next_level=True) found 177 parameters                                               (boardfarm.vcpe.lib.dmcli_command:getnames:327)
2025-07-18 22:00:44,197 INFO    - Found 177 top-level Device parameters                                                                 (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:191)
2025-07-18 22:00:44,198 INFO    -   1: CR component name is: eRT.com.cisco.spvtg.ccsp.CR                                         (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:195)
2025-07-18 22:00:44,198 INFO    -   2: subsystem_prefix eRT.                                                                     (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:195)
2025-07-18 22:00:44,198 INFO    -   3: Execution succeed.                                                                        (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:195)
2025-07-18 22:00:44,199 INFO    -   4: Parameter    1 name: Device.SoftwareModules.                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:195)
2025-07-18 22:00:44,199 INFO    -   5: writable:ReadOnly.                                                                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:195)
2025-07-18 22:00:44,200 INFO    -   6: Parameter    2 name: Device.CR.                                                    (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:195)
2025-07-18 22:00:44,200 INFO    -   7: writable:ReadOnly.                                                                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:195)
2025-07-18 22:00:44,201 INFO    -   8: Parameter    3 name: Device.DeviceInfo.                                            (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:195)
2025-07-18 22:00:44,201 INFO    -   9: writable:ReadOnly.                                                                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:195)
2025-07-18 22:00:44,201 INFO    -   10: Parameter    4 name: Device.X_RDK_Ethernet.                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:195)
2025-07-18 22:00:44,202 INFO    - Found common objects: ['DeviceInfo', 'Ethernet', 'WiFi', 'IP']                                        (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:206)
2025-07-18 22:00:44,202 DEBUG   - Executing dmcli command: dmcli eRT getnames Device.DeviceInfo. true                                   (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:44,386 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.X_RDKCENTRAL-COM_xOpsDeviceMgmt.
        writable:ReadOnly.
Parameter    2 name: Device.DeviceInfo.X_RDKCENTRAL-COM_FirmwareDownloadStatus
        writable:ReadOnly.
Parameter    3 name: Device.DeviceInfo.X_RDKCENTRAL-COM_FirmwareDownloadProtocol
        writable:Writable.
Parameter    4 name: Device.DeviceInfo.X_RDKCENTRAL-COM_FirmwareDownloadURL
        writable:Writable.
Parameter    5 name: Device.DeviceInfo.X_RDKCENTRAL-COM_FirmwareToDownload
        writable:Writable.
Parameter    6 name: Device.DeviceInfo.X_RDKCENTRAL-COM_FirmwareDownloadNow
        writable:Writable.
Parameter    7 name: Device.DeviceInfo.X_RDKCENTRAL-COM_FirmwareDownloadAndFactoryReset
        writable:Writable.
Parameter    8 name: Device.DeviceInfo.X_COMCAST-COM_WAN_IP
        writable:ReadOnly.
Parameter    9 name: Device.DeviceInfo.X_COMCAST-COM_WAN_IPv6
        writable:ReadOnly.
Parameter   10 name: Device.DeviceInfo.X_RDKCENTRAL-COM_Syndication.
        writable:ReadOnly.
Parameter   11 name: Device.DeviceInfo.X_RDKCENTRAL-COM_xOpsDeviceMgmt.
        writable:ReadOnly.
Parameter   12 name: Device.DeviceInfo.X_RDKCENTRAL-COM_RFC.
        writable:ReadOnly.
Parameter   13 name: Device.DeviceInfo.X_RDKCENTRAL-COM_EthernetWAN.
        writable:ReadOnly.
Parameter   14 name: Device.DeviceInfo.X_RDKCENTRAL-COM_xBlueTooth.
        writable:ReadOnly.
Parameter   15 name: Device.DeviceInfo.X_RDKCENTRAL-COM_MaintenanceWindow.
        writable:ReadOnly.
Parameter   16 name: Device.DeviceInfo.Iot.
        writable:ReadOnly.
Parameter   17 name: Device.DeviceInfo.VendorConfigFile.
        writable:ReadOnly.
Parameter   18 name: Device.DeviceInfo.MemoryStatus.
        writable:ReadOnly.
Parameter   19 name: Device.DeviceInfo.X_RDKCENTRAL-COM.
        writable:ReadOnly.
Parameter   20 name: Device.DeviceInfo.ProcessStatus.
        writable:ReadOnly.
Parameter   21 name: Device.DeviceInfo.NetworkProperties.
        writable:ReadOnly.
Parameter   22 name: Device.DeviceInfo.X_RDKCENTRAL-COM_WIFI_TELEMETRY.
        writable:ReadOnly.
Parameter   23 name: Device.DeviceInfo.X_CISCO_COM_BootloaderVersion
        writable:ReadOnly.
Parameter   24 name: Device.DeviceInfo.X_CISCO_COM_FirmwareName
        writable:ReadOnly.
Parameter   25 name: Device.DeviceInfo.X_RDK_FirmwareName
        writable:ReadOnly.
Parameter   26 name: Device.DeviceInfo.X_CISCO_COM_FirmwareBuildTime
        writable:ReadOnly.
Parameter   27 name: Device.DeviceInfo.X_RDKCENTRAL-COM_ConfigureWiFi
        writable:Writable.
Parameter   28 name: Device.DeviceInfo.X_RDKCENTRAL-COM_CaptivePortalEnable
        writable:Writable.
Parameter   29 name: Device.DeviceInfo.X_RDKCENTRAL-COM_WiFiNeedsPersonalization
        writable:ReadOnly.
Parameter   30 name: Device.DeviceInfo.X_RDKCENTRAL-COM_CloudUICapable
        writable:Writable.
Parameter   31 name: Device.DeviceInfo.X_RDKCENTRAL-COM_CloudUIEnable
        writable:Writable.
Parameter   32 name: Device.DeviceInfo.X_RDKCENTRAL-COM_CloudPersonalizationURL
        writable:Writable.
Parameter   33 name: Device.DeviceInfo.X_RDKCENTRAL-COM_UI_ACCESS
        writable:Writable.
Parameter   34 name: Device.DeviceInfo.X_RDKCENTRAL-COM_CloudUIWebURL
        writable:Writable.
Parameter   35 name: Device.DeviceInfo.X_RDK_RDKProfileName
        writable:ReadOnly.
Parameter   36 name: Device.DeviceInfo.X_COMCAST-COM_CM_MAC
        writable:ReadOnly.
Parameter   37 name: Device.DeviceInfo.X_COMCAST-COM_CM_IP
        writable:ReadOnly.
Parameter   38 name: Device.DeviceInfo.X_COMCAST-COM_WAN_MAC
        writable:ReadOnly.
Parameter   39 name: Device.DeviceInfo.X_COMCAST-COM_WAN_IP
        writable:ReadOnly.
Parameter   40 name: Device.DeviceInfo.X_COMCAST-COM_WAN_IPv6
        writable:ReadOnly.
Parameter   41 name: Device.DeviceInfo.X_COMCAST-COM_MTA_MAC
        writable:ReadOnly.
Parameter   42 name: Device.DeviceInfo.X_COMCAST-COM_MTA_IP
        writable:ReadOnly.
Parameter   43 name: Device.DeviceInfo.X_COMCAST-COM_MTA_IPV6
        writable:ReadOnly.
Parameter   44 name: Device.DeviceInfo.X_COMCAST-COM_AP_MAC
        writable:ReadOnly.
Parameter   45 name: Device.DeviceInfo.X_COMCAST-COM_EMS_MobileNumber
        writable:Writable.
Parameter   46 name: Device.DeviceInfo.X_COMCAST-COM_EMS_ServerURL
        writable:Writable.
Parameter   47 name: Device.DeviceInfo.X_RDKCENTRAL-COM_CMTS_MAC
        writable:ReadOnly.
Parameter   48 name: Device.DeviceInfo.X_CISCO_COM_BaseMacAddress
        writable:ReadOnly.
Parameter   49 name: Device.DeviceInfo.DeviceCategory
        writable:ReadOnly.
Parameter   50 name: Device.DeviceInfo.Manufacturer
        writable:ReadOnly.
Parameter   51 name: Device.DeviceInfo.ManufacturerOUI
        writable:ReadOnly.
Parameter   52 name: Device.DeviceInfo.X_CISCO_COM_AdvancedServices
        writable:ReadOnly.
Parameter   53 name: Device.DeviceInfo.X_CISCO_COM_ProcessorSpeed
        writable:ReadOnly.
Parameter   54 name: Device.DeviceInfo.Hardware
        writable:ReadOnly.
Parameter   55 name: Device.DeviceInfo.Hardware_MemUsed
        writable:ReadOnly.
Parameter   56 name: Device.DeviceInfo.Hardware_MemFree
        writable:ReadOnly.
Parameter   57 name: Device.DeviceInfo.ModelName
        writable:ReadOnly.
Parameter   58 name: Device.DeviceInfo.Description
        writable:ReadOnly.
Parameter   59 name: Device.DeviceInfo.ProductClass
        writable:ReadOnly.
Parameter   60 name: Device.DeviceInfo.SerialNumber
        writable:ReadOnly.
Parameter   61 name: Device.DeviceInfo.HardwareVersion
        writable:ReadOnly.
Parameter   62 name: Device.DeviceInfo.SoftwareVersion
        writable:ReadOnly.
Parameter   63 name: Device.DeviceInfo.AdditionalHardwareVersion
        writable:ReadOnly.
Parameter   64 name: Device.DeviceInfo.AdditionalSoftwareVersion
        writable:ReadOnly.
Parameter   65 name: Device.DeviceInfo.ProvisioningCode
        writable:Writable.
Parameter   66 name: Device.DeviceInfo.UpTime
        writable:ReadOnly.
Parameter   67 name: Device.DeviceInfo.X_RDKCENTRAL-COM_BootTime
        writable:ReadOnly.
Parameter   68 name: Device.DeviceInfo.X_RDKCENTRAL-COM_SystemTime
        writable:ReadOnly.
Parameter   69 name: Device.DeviceInfo.X_RDKCENTRAL-COM_LastRebootReason
        writable:Writable.
Parameter   70 name: Device.DeviceInfo.X_RDKCENTRAL-COM_InActiveFirmware
        writable:ReadOnly.
Parameter   71 name: Device.DeviceInfo.FirstUseDate
        writable:ReadOnly.
Parameter   72 name: Device.DeviceInfo.VendorConfigFileNumberOfEntries
        writable:ReadOnly.
Parameter   73 name: Device.DeviceInfo.X_COMCAST-COM_xfinitywifiCapableCPE
        writable:ReadOnly.
Parameter   74 name: Device.DeviceInfo.X_COMCAST_COM_xfinitywifiEnable
        writable:Writable.
Parameter   75 name: Device.DeviceInfo.X_COMCAST-COM_rdkbPlatformCapable
        writable:ReadOnly.
Parameter   76 name: Device.DeviceInfo.X_RDKCENTRAL-COM_ConfigureDocsicPollTime
        writable:Writable.
Parameter   77 name: Device.DeviceInfo.FactoryResetCount
        writable:ReadOnly.
Parameter   78 name: Device.DeviceInfo.ClearResetCount
        writable:Writable.
Parameter   79 name: Device.DeviceInfo.X_RDKCENTRAL-COM_AkerEnable
        writable:Writable.
Parameter   80 name: Device.DeviceInfo.X_RDKCENTRAL-COM_IsCloudReachable
        writable:ReadOnly.
Parameter   81 name: Device.DeviceInfo.X_RDKCENTRAL-COM_OnBoarding_State
        writable:ReadOnly.
Parameter   82 name: Device.DeviceInfo.X_RDKCENTRAL-COM_OnBoarding_DeleteLogs
        writable:Writable.
Parameter   83 name: Device.DeviceInfo.CustomDataModelEnabled
        writable:Writable.
Parameter   84 name: Device.DeviceInfo.X_RDKCENTRAL-COM_EnableMoCAforXi5
        writable:Writable.
Parameter   85 name: Device.DeviceInfo.SupportedDataModel.
        writable:ReadOnly.
Parameter   86 name: Device.DeviceInfo.X_RDKCENTRAL-COM_xOpsDeviceMgmt.
        writable:ReadOnly.
Parameter   87 name: Device.DeviceInfo.X_RDKCENTRAL-COM_AutowanFeatureSupport
        writable:ReadOnly.
Parameter   88 name: Device.DeviceInfo.X_RDKCENTRAL-COM_RFC.
        writable:ReadOnly.
Parameter   89 name: Device.DeviceInfo.X_RDKCENTRAL-COM_EnableXDNS
        writable:Writable.
Parameter   90 name: Device.DeviceInfo.X_RDKCENTRAL-COM_RFC.
        writable:ReadOnly.
Parameter   91 name: Device.DeviceInfo.X_RDKCENTRAL-COM_xOpsDeviceMgmt.
        writable:ReadOnly.
Parameter   92 name: Device.DeviceInfo.Webpa.
        writable:ReadOnly.

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:44,387 INFO    - getnames(Device.DeviceInfo., next_level=True) found 187 parameters                                    (boardfarm.vcpe.lib.dmcli_command:getnames:327)
2025-07-18 22:00:44,388 INFO    - Found 187 DeviceInfo parameters                                                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:217)
2025-07-18 22:00:44,389 INFO    - Found expected DeviceInfo parameters: ['Manufacturer', 'ModelName', 'SerialNumber', 'SoftwareVersion']  (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:224)
2025-07-18 22:00:44,389 INFO    - DMCLI parameter discovery test completed successfully                                                 (vcpe_only_tests.test_dmcli_operations:test_dmcli_parameter_discovery:229)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_operations.py::TestDMCLIOperations::test_dmcli_get_ethernet_interface_parameters 2025-07-18 22:00:44,399 INFO    - Starting DMCLI ethernet interface parameters test                                                     (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:96)
2025-07-18 22:00:44,399 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:99)
2025-07-18 22:00:44,400 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:00:44,400 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:44,764 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:44,765 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:00:44,972 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:00:44,972 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:00:45,149 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:00:45,322 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:00:45,494 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:00:45,494 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:00:45,865 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:00:45,866 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:00:45,866 INFO    - Testing DMCLI GPV for ethernet interface parameters                                                   (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:116)
2025-07-18 22:00:45,867 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.Ethernet.InterfaceNumberOfEntries                 (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:46,038 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.Ethernet.InterfaceNumberOfEntries
               type:       uint,    value: 6

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:46,038 INFO    - GPV(Device.Ethernet.InterfaceNumberOfEntries) = Device.Ethernet.InterfaceNumberOfEntries              (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:46,039 INFO    - ✓ Device.Ethernet.InterfaceNumberOfEntries = Device.Ethernet.InterfaceNumberOfEntries                 (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:132)
2025-07-18 22:00:46,039 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.Ethernet.Interface.1.Name                         (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:46,213 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.Ethernet.Interface.1.Name
               type:     string,    value: sw_1

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:46,213 INFO    - GPV(Device.Ethernet.Interface.1.Name) = Device.Ethernet.Interface.1.Name                              (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:46,214 INFO    - ✓ Device.Ethernet.Interface.1.Name = Device.Ethernet.Interface.1.Name                                 (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:132)
2025-07-18 22:00:46,214 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.Ethernet.Interface.1.MACAddress                   (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:46,386 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.Ethernet.Interface.1.MACAddress
               type:     string,    value: 00:16:3e:16:5f:7c

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:46,387 INFO    - GPV(Device.Ethernet.Interface.1.MACAddress) = Device.Ethernet.Interface.1.MACAddress                  (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:46,387 INFO    - ✓ Device.Ethernet.Interface.1.MACAddress = Device.Ethernet.Interface.1.MACAddress                     (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:132)
2025-07-18 22:00:46,389 ERROR   - Unexpected error getting Device.Ethernet.Interface.1.MACAddress: MAC address Device.Ethernet.Interface.1.MACAddress should contain : or -
assert (':' in 'Device.Ethernet.Interface.1.MACAddress' or '-' in 'Device.Ethernet.Interface.1.MACAddress')  (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:151)
2025-07-18 22:00:46,390 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.Ethernet.Interface.1.Status                       (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:46,583 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.Ethernet.Interface.1.Status
               type:     string,    value: Up

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:46,583 INFO    - GPV(Device.Ethernet.Interface.1.Status) = Device.Ethernet.Interface.1.Status                          (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:46,584 INFO    - ✓ Device.Ethernet.Interface.1.Status = Device.Ethernet.Interface.1.Status                             (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:132)
2025-07-18 22:00:46,584 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.Ethernet.Interface.1.Enable                       (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:46,737 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.Ethernet.Interface.1.Enable
               type:       bool,    value: false

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:46,737 INFO    - GPV(Device.Ethernet.Interface.1.Enable) = Device.Ethernet.Interface.1.Enable                          (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:46,738 INFO    - ✓ Device.Ethernet.Interface.1.Enable = Device.Ethernet.Interface.1.Enable                             (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:132)
2025-07-18 22:00:46,738 INFO    - Successfully retrieved 5/5 ethernet parameters                                                        (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:156)
2025-07-18 22:00:46,739 INFO    - DMCLI ethernet interface parameters test completed successfully                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_ethernet_interface_parameters:157)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_operations.py::TestDMCLIOperations::test_dmcli_set_parameter_operations 2025-07-18 22:00:46,750 INFO    - Starting DMCLI set parameter operations test                                                          (vcpe_only_tests.test_dmcli_operations:test_dmcli_set_parameter_operations:302)
2025-07-18 22:00:46,751 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_set_parameter_operations:305)
2025-07-18 22:00:46,751 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:00:46,752 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:47,136 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:47,137 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:00:47,323 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:00:47,324 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:00:47,492 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:00:47,669 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:00:47,840 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:00:47,840 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:00:48,208 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:00:48,209 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:00:48,209 INFO    - Testing DMCLI SPV for safe parameter operations                                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_set_parameter_operations:322)
2025-07-18 22:00:48,210 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.Description                            (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:48,362 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.Description
               type:     string,    value: Raspberry Pi 3 device

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:48,362 INFO    - GPV(Device.DeviceInfo.Description) = Device.DeviceInfo.Description                                    (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:48,363 INFO    - Original Device.DeviceInfo.Description = Device.DeviceInfo.Description                                (vcpe_only_tests.test_dmcli_operations:test_dmcli_set_parameter_operations:332)
2025-07-18 22:00:48,363 INFO    - Attempting to set Device.DeviceInfo.Description = DMCLI Test Device - Automated Test                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_set_parameter_operations:337)
2025-07-18 22:00:48,363 DEBUG   - Executing dmcli command: dmcli eRT setvalues Device.DeviceInfo.Description string DMCLI Test Device - Automated Test  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:48,564 DEBUG   - dmcli command result: Syntax error. see help.
                                             (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:48,566 ERROR   - SPV(Device.DeviceInfo.Description, DMCLI Test Device - Automated Test, string) failed: Syntax error. see help.
  (boardfarm.vcpe.lib.dmcli_command:SPV:122)
2025-07-18 22:00:48,566 WARNING - SPV operation failed for Device.DeviceInfo.Description: Failed to set parameter Device.DeviceInfo.Description: Syntax error. see help.
  (vcpe_only_tests.test_dmcli_operations:test_dmcli_set_parameter_operations:371)
2025-07-18 22:00:48,567 INFO    - DMCLI set parameter operations test completed successfully                                            (vcpe_only_tests.test_dmcli_operations:test_dmcli_set_parameter_operations:376)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_operations.py::TestDMCLIOperations::test_dmcli_get_device_info_parameters 2025-07-18 22:00:48,578 INFO    - Starting DMCLI device info parameters test                                                            (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:27)
2025-07-18 22:00:48,579 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:30)
2025-07-18 22:00:48,579 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:00:48,580 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:48,960 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:48,961 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:00:49,138 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:00:49,139 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:00:49,371 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:00:49,541 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:00:49,745 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:00:49,745 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:00:50,085 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:00:50,085 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:00:50,086 INFO    - VCPE device booted successfully                                                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:35)
2025-07-18 22:00:50,086 INFO    - Testing DMCLI GPV for device information parameters                                                   (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:48)
2025-07-18 22:00:50,087 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.Manufacturer                           (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:50,260 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.Manufacturer
               type:     string,    value: Raspberry Pi Foundation

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:50,261 INFO    - GPV(Device.DeviceInfo.Manufacturer) = Device.DeviceInfo.Manufacturer                                  (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:50,261 INFO    - ✓ Device.DeviceInfo.Manufacturer = Device.DeviceInfo.Manufacturer                                     (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:69)
2025-07-18 22:00:50,262 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.ManufacturerOUI                        (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:50,440 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.ManufacturerOUI
               type:     string,    value: FFFFFF

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:50,440 INFO    - GPV(Device.DeviceInfo.ManufacturerOUI) = Device.DeviceInfo.ManufacturerOUI                            (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:50,441 INFO    - ✓ Device.DeviceInfo.ManufacturerOUI = Device.DeviceInfo.ManufacturerOUI                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:69)
2025-07-18 22:00:50,441 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.ModelName                              (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:50,615 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.ModelName
               type:     string,    value: RPI

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:50,615 INFO    - GPV(Device.DeviceInfo.ModelName) = Device.DeviceInfo.ModelName                                        (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:50,615 INFO    - ✓ Device.DeviceInfo.ModelName = Device.DeviceInfo.ModelName                                           (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:69)
2025-07-18 22:00:50,616 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.ProductClass                           (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:50,798 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.ProductClass
               type:     string,    value: ER

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:50,798 INFO    - GPV(Device.DeviceInfo.ProductClass) = Device.DeviceInfo.ProductClass                                  (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:50,799 INFO    - ✓ Device.DeviceInfo.ProductClass = Device.DeviceInfo.ProductClass                                     (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:69)
2025-07-18 22:00:50,799 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.SerialNumber                           (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:50,966 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.SerialNumber
               type:     string,    value: 00163E207968

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:50,966 INFO    - GPV(Device.DeviceInfo.SerialNumber) = Device.DeviceInfo.SerialNumber                                  (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:50,966 INFO    - ✓ Device.DeviceInfo.SerialNumber = Device.DeviceInfo.SerialNumber                                     (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:69)
2025-07-18 22:00:50,967 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.HardwareVersion                        (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:51,133 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.HardwareVersion
               type:     string,    value: 1.0

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:51,133 INFO    - GPV(Device.DeviceInfo.HardwareVersion) = Device.DeviceInfo.HardwareVersion                            (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:51,133 INFO    - ✓ Device.DeviceInfo.HardwareVersion = Device.DeviceInfo.HardwareVersion                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:69)
2025-07-18 22:00:51,133 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.SoftwareVersion                        (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:51,305 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.SoftwareVersion
               type:     string,    value: X86EMLTRBB_rdkb-2025q1-kirkstone_20250710065559

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:51,306 INFO    - GPV(Device.DeviceInfo.SoftwareVersion) = Device.DeviceInfo.SoftwareVersion                            (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:51,306 INFO    - ✓ Device.DeviceInfo.SoftwareVersion = Device.DeviceInfo.SoftwareVersion                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:69)
2025-07-18 22:00:51,307 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.Description                            (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:51,486 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.Description
               type:     string,    value: Raspberry Pi 3 device

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:51,487 INFO    - GPV(Device.DeviceInfo.Description) = Device.DeviceInfo.Description                                    (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:51,487 INFO    - ✓ Device.DeviceInfo.Description = Device.DeviceInfo.Description                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:69)
2025-07-18 22:00:51,487 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.UpTime                                 (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:51,656 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.UpTime
               type:       uint,    value: 1387164

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:51,657 INFO    - GPV(Device.DeviceInfo.UpTime) = Device.DeviceInfo.UpTime                                              (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:51,657 INFO    - ✓ Device.DeviceInfo.UpTime = Device.DeviceInfo.UpTime                                                 (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:69)
2025-07-18 22:00:51,658 INFO    - Successfully retrieved 9/9 device info parameters                                                     (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:86)
2025-07-18 22:00:51,658 INFO    - DMCLI device info parameters test completed successfully                                              (vcpe_only_tests.test_dmcli_operations:test_dmcli_get_device_info_parameters:87)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_operations.py::TestDMCLIOperations::test_dmcli_comprehensive_device_scan 2025-07-18 22:00:51,670 INFO    - Starting DMCLI comprehensive device scan test                                                         (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:385)
2025-07-18 22:00:51,670 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:388)
2025-07-18 22:00:51,671 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:00:51,671 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:52,064 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:52,065 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:00:52,234 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:00:52,234 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:00:52,389 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:00:52,599 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:00:52,785 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:00:52,786 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:00:53,134 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:00:53,135 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:00:53,136 INFO    - Performing comprehensive DMCLI device scan                                                            (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:405)
2025-07-18 22:00:53,136 INFO    -
=== Scanning Device Information ===                                                                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:446)
2025-07-18 22:00:53,137 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.Manufacturer                           (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:53,318 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.Manufacturer
               type:     string,    value: Raspberry Pi Foundation

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:53,319 INFO    - GPV(Device.DeviceInfo.Manufacturer) = Device.DeviceInfo.Manufacturer                                  (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:53,319 INFO    -   ✓ Device.DeviceInfo.Manufacturer = Device.DeviceInfo.Manufacturer                                   (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:53,320 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.ManufacturerOUI                        (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:53,485 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.ManufacturerOUI
               type:     string,    value: FFFFFF

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:53,485 INFO    - GPV(Device.DeviceInfo.ManufacturerOUI) = Device.DeviceInfo.ManufacturerOUI                            (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:53,486 INFO    -   ✓ Device.DeviceInfo.ManufacturerOUI = Device.DeviceInfo.ManufacturerOUI                             (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:53,486 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.ModelName                              (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:53,641 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.ModelName
               type:     string,    value: RPI

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:53,642 INFO    - GPV(Device.DeviceInfo.ModelName) = Device.DeviceInfo.ModelName                                        (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:53,642 INFO    -   ✓ Device.DeviceInfo.ModelName = Device.DeviceInfo.ModelName                                         (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:53,643 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.ProductClass                           (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:53,821 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.ProductClass
               type:     string,    value: ER

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:53,821 INFO    - GPV(Device.DeviceInfo.ProductClass) = Device.DeviceInfo.ProductClass                                  (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:53,822 INFO    -   ✓ Device.DeviceInfo.ProductClass = Device.DeviceInfo.ProductClass                                   (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:53,822 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.SerialNumber                           (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:53,992 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.SerialNumber
               type:     string,    value: 00163E207968

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:53,992 INFO    - GPV(Device.DeviceInfo.SerialNumber) = Device.DeviceInfo.SerialNumber                                  (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:53,993 INFO    -   ✓ Device.DeviceInfo.SerialNumber = Device.DeviceInfo.SerialNumber                                   (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:53,993 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.HardwareVersion                        (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:54,167 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.HardwareVersion
               type:     string,    value: 1.0

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:54,168 INFO    - GPV(Device.DeviceInfo.HardwareVersion) = Device.DeviceInfo.HardwareVersion                            (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:54,168 INFO    -   ✓ Device.DeviceInfo.HardwareVersion = Device.DeviceInfo.HardwareVersion                             (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:54,169 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.SoftwareVersion                        (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:54,344 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.SoftwareVersion
               type:     string,    value: X86EMLTRBB_rdkb-2025q1-kirkstone_20250710065559

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:54,344 INFO    - GPV(Device.DeviceInfo.SoftwareVersion) = Device.DeviceInfo.SoftwareVersion                            (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:54,345 INFO    -   ✓ Device.DeviceInfo.SoftwareVersion = Device.DeviceInfo.SoftwareVersion                             (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:54,345 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.Description                            (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:54,520 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.Description
               type:     string,    value: Raspberry Pi 3 device

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:54,520 INFO    - GPV(Device.DeviceInfo.Description) = Device.DeviceInfo.Description                                    (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:54,521 INFO    -   ✓ Device.DeviceInfo.Description = Device.DeviceInfo.Description                                     (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:54,521 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.UpTime                                 (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:54,683 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.UpTime
               type:       uint,    value: 1387167

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:54,683 INFO    - GPV(Device.DeviceInfo.UpTime) = Device.DeviceInfo.UpTime                                              (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:54,684 INFO    -   ✓ Device.DeviceInfo.UpTime = Device.DeviceInfo.UpTime                                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:54,684 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.BootloaderVersion                      (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:54,862 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Can't find destination component.

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:54,862 WARNING - Could not parse value for parameter Device.DeviceInfo.BootloaderVersion, returning raw result         (boardfarm.vcpe.lib.dmcli_command:GPV:83)
2025-07-18 22:00:54,862 INFO    -   ✓ Device.DeviceInfo.BootloaderVersion = CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Can't find destination component.

  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:54,863 INFO    -   Category summary: 10/10 successful                                                                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:467)
2025-07-18 22:00:54,863 INFO    -
=== Scanning Network Interfaces ===                                                                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:446)
2025-07-18 22:00:54,864 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.Ethernet.InterfaceNumberOfEntries                 (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:55,036 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.Ethernet.InterfaceNumberOfEntries
               type:       uint,    value: 6

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:55,036 INFO    - GPV(Device.Ethernet.InterfaceNumberOfEntries) = Device.Ethernet.InterfaceNumberOfEntries              (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:55,037 INFO    -   ✓ Device.Ethernet.InterfaceNumberOfEntries = Device.Ethernet.InterfaceNumberOfEntries               (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:55,037 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.Ethernet.Interface.1.Name                         (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:55,213 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.Ethernet.Interface.1.Name
               type:     string,    value: sw_1

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:55,213 INFO    - GPV(Device.Ethernet.Interface.1.Name) = Device.Ethernet.Interface.1.Name                              (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:55,214 INFO    -   ✓ Device.Ethernet.Interface.1.Name = Device.Ethernet.Interface.1.Name                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:55,214 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.Ethernet.Interface.1.MACAddress                   (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:55,384 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.Ethernet.Interface.1.MACAddress
               type:     string,    value: 00:16:3e:16:5f:7c

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:55,385 INFO    - GPV(Device.Ethernet.Interface.1.MACAddress) = Device.Ethernet.Interface.1.MACAddress                  (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:55,385 INFO    -   ✓ Device.Ethernet.Interface.1.MACAddress = Device.Ethernet.Interface.1.MACAddress                   (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:55,386 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.Ethernet.Interface.1.Status                       (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:55,552 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.Ethernet.Interface.1.Status
               type:     string,    value: Up

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:55,552 INFO    - GPV(Device.Ethernet.Interface.1.Status) = Device.Ethernet.Interface.1.Status                          (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:55,552 INFO    -   ✓ Device.Ethernet.Interface.1.Status = Device.Ethernet.Interface.1.Status                           (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:55,552 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.IP.InterfaceNumberOfEntries                       (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:55,713 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.IP.InterfaceNumberOfEntries
               type:       uint,    value: 5

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:55,713 INFO    - GPV(Device.IP.InterfaceNumberOfEntries) = Device.IP.InterfaceNumberOfEntries                          (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:55,713 INFO    -   ✓ Device.IP.InterfaceNumberOfEntries = Device.IP.InterfaceNumberOfEntries                           (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:55,713 INFO    -   Category summary: 5/5 successful                                                                    (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:467)
2025-07-18 22:00:55,714 INFO    -
=== Scanning WiFi Information ===                                                                    (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:446)
2025-07-18 22:00:55,714 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.WiFi.RadioNumberOfEntries                         (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:55,884 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.WiFi.RadioNumberOfEntries
               type:       uint,    value: 2

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:55,884 INFO    - GPV(Device.WiFi.RadioNumberOfEntries) = Device.WiFi.RadioNumberOfEntries                              (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:55,884 INFO    -   ✓ Device.WiFi.RadioNumberOfEntries = Device.WiFi.RadioNumberOfEntries                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:55,885 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.WiFi.SSIDNumberOfEntries                          (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:56,057 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.WiFi.SSIDNumberOfEntries
               type:       uint,    value: 16

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:56,058 INFO    - GPV(Device.WiFi.SSIDNumberOfEntries) = Device.WiFi.SSIDNumberOfEntries                                (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:56,058 INFO    -   ✓ Device.WiFi.SSIDNumberOfEntries = Device.WiFi.SSIDNumberOfEntries                                 (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:56,059 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.WiFi.Radio.1.Enable                               (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:56,233 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.WiFi.Radio.1.Enable
               type:       bool,    value: true

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:56,233 INFO    - GPV(Device.WiFi.Radio.1.Enable) = Device.WiFi.Radio.1.Enable                                          (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:56,233 INFO    -   ✓ Device.WiFi.Radio.1.Enable = Device.WiFi.Radio.1.Enable                                           (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:56,234 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.WiFi.Radio.1.Status                               (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:56,406 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.WiFi.Radio.1.Status
               type:     string,    value: Up

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:56,406 INFO    - GPV(Device.WiFi.Radio.1.Status) = Device.WiFi.Radio.1.Status                                          (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:56,406 INFO    -   ✓ Device.WiFi.Radio.1.Status = Device.WiFi.Radio.1.Status                                           (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:56,407 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.WiFi.Radio.1.Name                                 (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:56,570 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.WiFi.Radio.1.Name
               type:     string,    value: wlan0

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:56,570 INFO    - GPV(Device.WiFi.Radio.1.Name) = Device.WiFi.Radio.1.Name                                              (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:56,571 INFO    -   ✓ Device.WiFi.Radio.1.Name = Device.WiFi.Radio.1.Name                                               (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:56,571 INFO    -   Category summary: 5/5 successful                                                                    (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:467)
2025-07-18 22:00:56,572 INFO    -
=== Scanning Management ===                                                                          (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:446)
2025-07-18 22:00:56,572 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.ManagementServer.URL                              (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:56,734 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.ManagementServer.URL
               type:     string,    value: http://10.10.10.200:9675

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:56,735 INFO    - GPV(Device.ManagementServer.URL) = Device.ManagementServer.URL                                        (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:56,735 INFO    -   ✓ Device.ManagementServer.URL = Device.ManagementServer.URL                                         (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:56,735 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.ManagementServer.EnableCWMP                       (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:56,917 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.ManagementServer.EnableCWMP
               type:       bool,    value: true

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:56,917 INFO    - GPV(Device.ManagementServer.EnableCWMP) = Device.ManagementServer.EnableCWMP                          (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:56,917 INFO    -   ✓ Device.ManagementServer.EnableCWMP = Device.ManagementServer.EnableCWMP                           (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:56,918 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.ManagementServer.ConnectionRequestURL             (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:57,088 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.ManagementServer.ConnectionRequestURL
               type:     string,    value: http://10.107.200.100:7547/

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:57,089 INFO    - GPV(Device.ManagementServer.ConnectionRequestURL) = Device.ManagementServer.ConnectionRequestURL      (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:00:57,089 INFO    -   ✓ Device.ManagementServer.ConnectionRequestURL = Device.ManagementServer.ConnectionRequestURL       (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:454)
2025-07-18 22:00:57,090 INFO    -   Category summary: 3/3 successful                                                                    (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:467)
2025-07-18 22:00:57,090 INFO    -
============================================================                                         (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:470)
2025-07-18 22:00:57,091 INFO    - DMCLI COMPREHENSIVE DEVICE SCAN REPORT                                                                (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:471)
2025-07-18 22:00:57,091 INFO    - ============================================================                                          (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:472)
2025-07-18 22:00:57,091 INFO    - Total parameters tested: 23                                                                           (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:473)
2025-07-18 22:00:57,092 INFO    - Total successful queries: 23                                                                          (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:474)
2025-07-18 22:00:57,092 INFO    - Success rate: 100.0%                                                                                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:475)
2025-07-18 22:00:57,093 INFO    -
Device Information: 10/10 successful                                                                 (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:479)
2025-07-18 22:00:57,093 INFO    -   Device.DeviceInfo.Manufacturer: Device.DeviceInfo.Manufacturer                                      (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,093 INFO    -   Device.DeviceInfo.ManufacturerOUI: Device.DeviceInfo.ManufacturerOUI                                (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,094 INFO    -   Device.DeviceInfo.ModelName: Device.DeviceInfo.ModelName                                            (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,094 INFO    -   Device.DeviceInfo.ProductClass: Device.DeviceInfo.ProductClass                                      (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,094 INFO    -   Device.DeviceInfo.SerialNumber: Device.DeviceInfo.SerialNumber                                      (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,095 INFO    -   Device.DeviceInfo.HardwareVersion: Device.DeviceInfo.HardwareVersion                                (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,095 INFO    -   Device.DeviceInfo.SoftwareVersion: Device.DeviceInfo.SoftwareVersion                                (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,096 INFO    -   Device.DeviceInfo.Description: Device.DeviceInfo.Description                                        (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,096 INFO    -   Device.DeviceInfo.UpTime: Device.DeviceInfo.UpTime                                                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,096 INFO    -   Device.DeviceInfo.BootloaderVersion: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Can't find destination component.

  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,097 INFO    -
Network Interfaces: 5/5 successful                                                                   (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:479)
2025-07-18 22:00:57,097 INFO    -   Device.Ethernet.InterfaceNumberOfEntries: Device.Ethernet.InterfaceNumberOfEntries                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,098 INFO    -   Device.Ethernet.Interface.1.Name: Device.Ethernet.Interface.1.Name                                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,098 INFO    -   Device.Ethernet.Interface.1.MACAddress: Device.Ethernet.Interface.1.MACAddress                      (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,098 INFO    -   Device.Ethernet.Interface.1.Status: Device.Ethernet.Interface.1.Status                              (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,099 INFO    -   Device.IP.InterfaceNumberOfEntries: Device.IP.InterfaceNumberOfEntries                              (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,099 INFO    -
WiFi Information: 5/5 successful                                                                     (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:479)
2025-07-18 22:00:57,100 INFO    -   Device.WiFi.RadioNumberOfEntries: Device.WiFi.RadioNumberOfEntries                                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,100 INFO    -   Device.WiFi.SSIDNumberOfEntries: Device.WiFi.SSIDNumberOfEntries                                    (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,100 INFO    -   Device.WiFi.Radio.1.Enable: Device.WiFi.Radio.1.Enable                                              (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,101 INFO    -   Device.WiFi.Radio.1.Status: Device.WiFi.Radio.1.Status                                              (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,101 INFO    -   Device.WiFi.Radio.1.Name: Device.WiFi.Radio.1.Name                                                  (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,101 INFO    -
Management: 3/3 successful                                                                           (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:479)
2025-07-18 22:00:57,102 INFO    -   Device.ManagementServer.URL: Device.ManagementServer.URL                                            (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,102 INFO    -   Device.ManagementServer.EnableCWMP: Device.ManagementServer.EnableCWMP                              (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,103 INFO    -   Device.ManagementServer.ConnectionRequestURL: Device.ManagementServer.ConnectionRequestURL          (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:483)
2025-07-18 22:00:57,103 INFO    - ============================================================                                          (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:485)
2025-07-18 22:00:57,103 INFO    - DMCLI comprehensive device scan test completed successfully                                           (vcpe_only_tests.test_dmcli_operations:test_dmcli_comprehensive_device_scan:495)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_command.py::TestDMCLICommand::test_dmcli_command_execution_mock 2025-07-18 22:00:57,115 INFO    - Starting DMCLI command execution test                                                                 (vcpe_only_tests.test_dmcli_command:test_dmcli_command_execution_mock:64)
2025-07-18 22:00:57,116 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_command:test_dmcli_command_execution_mock:67)
2025-07-18 22:00:57,116 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:00:57,116 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:57,462 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:57,463 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:00:57,670 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:00:57,670 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:00:57,827 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:00:58,002 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:00:58,173 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:00:58,174 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:00:58,577 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:00:58,577 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:00:58,578 INFO    - Testing basic dmcli command execution                                                                 (vcpe_only_tests.test_dmcli_command:test_dmcli_command_execution_mock:84)
2025-07-18 22:00:58,578 DEBUG   - Executing dmcli command: dmcli eRT help                                                               (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:58,729 DEBUG   - dmcli command result: Commands supported:
        setvalues pathname type value [pathname type value] ... [commit]
        setcommit
        getvalues pathname [pathname] ...
        retv pathname [pathname]
        sgetvalues pathname [pathname] ...
        setattributes pathname notify accesslist [pathname notify accesslist ] ...
        getattributes pathname [pathname] ...
        addtable pathname
        deltable pathname
        getnames pathname [nextlevel]
        setsub set subsystem_prefix when call CcspBaseIf_discComponentSupportingNamespace
        psmget pathname
        psmset pathname type value
        psmdel pathname
        help
        exit
        -------------------------------------
        retv      : This cmd is used to return the value of parameter only.
        sgetvalues: This cmd is used to calculate GPV time.
        pathname  : It's a full name or partial name.
        type      : It is one of string/int/uint/bool/datetime/base64/float/double/byte.
        value     : It is a string for all types, even for int or enumeration.
                    If the string need to contain blank space, pls put value like "aa bb".
        commit    : It is true or false. It's true by default.
        notify    : It is one of unchange/off/passive/active.
        accesslist: It can be only one of unchange/acs/xmpp/cli/webgui/anybody.
        nextlevel : It is true or false. It's true by default.
  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:58,729 INFO    - dmcli help result: Commands supported:
        setvalues pathname type value [pathname type value] ... [commit]
        setcommit
        getvalues pathname [pathname] ...
        retv pathname [pathname]
        sgetvalues pathname [pathname] ...
        setattributes pathname notify accesslist [pathname notify accesslist ] ...
        getattributes pathname [pathname] ...
        addtable pathname
        deltable pathname
        getnames pathname [nextlevel]
        setsub set subsystem_prefix when call CcspBaseIf_discComponentSupportingNamespace
        psmget pathname
        psmset pathname type value
        psmdel pathname
        help
        exit
        -------------------------------------
        retv      : This cmd is used to return the value of parameter only.
        sgetvalues: This cmd is used to calculate GPV time.
        pathname  : It's a full name or partial name.
        type      : It is one of string/int/uint/bool/datetime/base64/float/double/byte.
        value     : It is a string for all types, even for int or enumeration.
                    If the string need to contain blank space, pls put value like "aa bb".
        commit    : It is true or false. It's true by default.
        notify    : It is one of unchange/off/passive/active.
        accesslist: It can be only one of unchange/acs/xmpp/cli/webgui/anybody.
        nextlevel : It is true or false. It's true by default.
  (vcpe_only_tests.test_dmcli_command:test_dmcli_command_execution_mock:89)
2025-07-18 22:00:58,730 DEBUG   - Executing dmcli command: dmcli eRT invalid_command_12345                                              (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:00:58,929 DEBUG   - dmcli command result: Syntax error. see help.
                                             (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:00:58,930 INFO    - Invalid command result: Syntax error. see help.
                                           (vcpe_only_tests.test_dmcli_command:test_dmcli_command_execution_mock:98)
2025-07-18 22:00:58,930 INFO    - DMCLI command execution test completed successfully                                                   (vcpe_only_tests.test_dmcli_command:test_dmcli_command_execution_mock:103)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_command.py::TestDMCLICommand::test_dmcli_command_initialization 2025-07-18 22:00:58,942 INFO    - Starting DMCLI command initialization test                                                            (vcpe_only_tests.test_dmcli_command:test_dmcli_command_initialization:27)
2025-07-18 22:00:58,943 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_command:test_dmcli_command_initialization:30)
2025-07-18 22:00:58,943 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:00:58,943 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:00:59,329 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:00:59,329 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:00:59,502 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:00:59,502 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:00:59,672 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:00:59,845 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:00,021 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:00,021 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:00,367 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:00,367 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:00,368 INFO    - VCPE device booted successfully                                                                       (vcpe_only_tests.test_dmcli_command:test_dmcli_command_initialization:35)
2025-07-18 22:01:00,368 INFO    - Initializing DMCLI command interface                                                                  (vcpe_only_tests.test_dmcli_command:test_dmcli_command_initialization:45)
2025-07-18 22:01:00,368 INFO    - DMCLI command initialization test completed successfully                                              (vcpe_only_tests.test_dmcli_command:test_dmcli_command_initialization:55)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_command.py::TestDMCLICommand::test_dmcli_error_handling 2025-07-18 22:01:00,380 INFO    - Starting DMCLI error handling test                                                                    (vcpe_only_tests.test_dmcli_command:test_dmcli_error_handling:203)
2025-07-18 22:01:00,380 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_command:test_dmcli_error_handling:206)
2025-07-18 22:01:00,381 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:00,381 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:00,709 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:00,710 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:00,899 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:00,899 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:01,070 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:01,245 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:01,426 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:01,427 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:01,781 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:01,781 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:01,782 INFO    - Testing DMCLI error handling                                                                          (vcpe_only_tests.test_dmcli_command:test_dmcli_error_handling:223)
2025-07-18 22:01:01,782 DEBUG   - Executing dmcli command: dmcli eRT getvalues Invalid.Parameter.That.Does.Not.Exist.12345              (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:01,952 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Can't find destination component.

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:01,953 WARNING - Could not parse value for parameter Invalid.Parameter.That.Does.Not.Exist.12345, returning raw result  (boardfarm.vcpe.lib.dmcli_command:GPV:83)
2025-07-18 22:01:01,953 INFO    - Invalid parameter result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Can't find destination component.

  (vcpe_only_tests.test_dmcli_command:test_dmcli_error_handling:228)
2025-07-18 22:01:01,953 DEBUG   - Executing dmcli command: dmcli eRT                                                                    (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:02,131 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
dmcli>main,2366: error in reading inputLine  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:02,131 INFO    - Empty command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
dmcli>main,2366: error in reading inputLine  (vcpe_only_tests.test_dmcli_command:test_dmcli_error_handling:240)
2025-07-18 22:01:02,132 INFO    - DMCLI error handling test completed successfully                                                      (vcpe_only_tests.test_dmcli_command:test_dmcli_error_handling:246)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_command.py::TestDMCLICommand::test_dmcli_library_api 2025-07-18 22:01:02,143 INFO    - Starting DMCLI library API test                                                                       (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:154)
2025-07-18 22:01:02,144 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:157)
2025-07-18 22:01:02,144 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:02,144 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:02,531 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:02,532 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:02,758 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:02,758 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:02,939 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:03,116 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:03,297 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:03,297 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:03,623 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:03,623 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:03,624 INFO    - Testing DMCLI library API methods                                                                     (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:174)
2025-07-18 22:01:03,624 INFO    - ✓ GPV method is available and callable                                                                (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:186)
2025-07-18 22:01:03,624 INFO    - ✓ SPV method is available and callable                                                                (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:186)
2025-07-18 22:01:03,624 INFO    - ✓ DelObject method is available and callable                                                          (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:186)
2025-07-18 22:01:03,624 INFO    - ✓ getattributes method is available and callable                                                      (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:186)
2025-07-18 22:01:03,625 INFO    - ✓ setattributes method is available and callable                                                      (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:186)
2025-07-18 22:01:03,625 INFO    - ✓ addtable method is available and callable                                                           (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:186)
2025-07-18 22:01:03,625 INFO    - ✓ getnames method is available and callable                                                           (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:186)
2025-07-18 22:01:03,625 INFO    - ✓ get_all_parameters method is available and callable                                                 (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:186)
2025-07-18 22:01:03,625 INFO    - All DMCLI library API methods are properly defined                                                    (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:193)
2025-07-18 22:01:03,626 INFO    - DMCLI library API test completed successfully                                                         (vcpe_only_tests.test_dmcli_command:test_dmcli_library_api:194)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_command.py::TestDMCLICommand::test_dmcli_gpv_method 2025-07-18 22:01:03,631 INFO    - Starting DMCLI GPV method test                                                                        (vcpe_only_tests.test_dmcli_command:test_dmcli_gpv_method:112)
2025-07-18 22:01:03,631 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_command:test_dmcli_gpv_method:115)
2025-07-18 22:01:03,631 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:03,631 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:03,962 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:03,962 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:04,205 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:04,205 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:04,379 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:04,558 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:04,767 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:04,768 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:05,113 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:05,113 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:05,114 INFO    - Testing DMCLI GPV method                                                                              (vcpe_only_tests.test_dmcli_command:test_dmcli_gpv_method:132)
2025-07-18 22:01:05,114 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.SoftwareVersion                        (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:05,314 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.SoftwareVersion
               type:     string,    value: X86EMLTRBB_rdkb-2025q1-kirkstone_20250710065559

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:05,314 INFO    - GPV(Device.DeviceInfo.SoftwareVersion) = Device.DeviceInfo.SoftwareVersion                            (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:01:05,315 INFO    - GPV(Device.DeviceInfo.SoftwareVersion) = Device.DeviceInfo.SoftwareVersion                            (vcpe_only_tests.test_dmcli_command:test_dmcli_gpv_method:138)
2025-07-18 22:01:05,315 INFO    - DMCLI GPV method test completed successfully                                                          (vcpe_only_tests.test_dmcli_command:test_dmcli_gpv_method:145)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_retv.py::TestDMCLIRetv::test_dmcli_retv_vs_gpv_comparison 2025-07-18 22:01:05,327 INFO    - Starting DMCLI retv vs GPV comparison test                                                            (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:156)
2025-07-18 22:01:05,327 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:159)
2025-07-18 22:01:05,328 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:05,328 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:05,717 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:05,718 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:05,906 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:05,906 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:06,082 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:06,257 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:06,432 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:06,433 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:06,783 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:06,783 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:06,784 INFO    - Comparing retv and GPV methods                                                                        (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:176)
2025-07-18 22:01:06,784 DEBUG   - Executing dmcli command: dmcli eRT retv Device.DeviceInfo.Description                                 (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:06,957 DEBUG   - dmcli command result: Raspberry Pi 3 device                                                           (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:06,958 INFO    - retv(Device.DeviceInfo.Description) = Raspberry Pi 3 device                                           (boardfarm.vcpe.lib.dmcli_command:retv:393)
2025-07-18 22:01:06,959 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.Description                            (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:07,131 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.Description
               type:     string,    value: Raspberry Pi 3 device

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:07,131 INFO    - GPV(Device.DeviceInfo.Description) = Device.DeviceInfo.Description                                    (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:01:07,132 INFO    - Parameter: Device.DeviceInfo.Description                                                              (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:191)
2025-07-18 22:01:07,132 INFO    -   retv result: 'Raspberry Pi 3 device'                                                                (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:192)
2025-07-18 22:01:07,132 INFO    -   GPV result:  'Device.DeviceInfo.Description'                                                        (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:193)
2025-07-18 22:01:07,133 INFO    -   Lengths: retv=21, GPV=29                                                                            (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:216)
2025-07-18 22:01:07,133 DEBUG   - Executing dmcli command: dmcli eRT retv Device.DeviceInfo.HardwareVersion                             (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:07,309 DEBUG   - dmcli command result: 1.0                                                                             (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:07,310 INFO    - retv(Device.DeviceInfo.HardwareVersion) = 1.0                                                         (boardfarm.vcpe.lib.dmcli_command:retv:393)
2025-07-18 22:01:07,310 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.HardwareVersion                        (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:07,507 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.HardwareVersion
               type:     string,    value: 1.0

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:07,507 INFO    - GPV(Device.DeviceInfo.HardwareVersion) = Device.DeviceInfo.HardwareVersion                            (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:01:07,507 INFO    - Parameter: Device.DeviceInfo.HardwareVersion                                                          (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:191)
2025-07-18 22:01:07,508 INFO    -   retv result: '1.0'                                                                                  (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:192)
2025-07-18 22:01:07,508 INFO    -   GPV result:  'Device.DeviceInfo.HardwareVersion'                                                    (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:193)
2025-07-18 22:01:07,509 INFO    -   Lengths: retv=3, GPV=33                                                                             (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:216)
2025-07-18 22:01:07,509 INFO    -
=== RETV vs GPV Comparison Results ===                                                               (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:226)
2025-07-18 22:01:07,510 INFO    - Parameter: Device.DeviceInfo.Description                                                              (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:228)
2025-07-18 22:01:07,510 INFO    -   retv: 'Raspberry Pi 3 device'                                                                       (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:229)
2025-07-18 22:01:07,510 INFO    -   GPV:  'Device.DeviceInfo.Description'                                                               (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:230)
2025-07-18 22:01:07,511 INFO    -   retv shorter/equal: True                                                                            (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:231)
2025-07-18 22:01:07,511 INFO    - Parameter: Device.DeviceInfo.HardwareVersion                                                          (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:228)
2025-07-18 22:01:07,512 INFO    -   retv: '1.0'                                                                                         (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:229)
2025-07-18 22:01:07,512 INFO    -   GPV:  'Device.DeviceInfo.HardwareVersion'                                                           (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:230)
2025-07-18 22:01:07,512 INFO    -   retv shorter/equal: True                                                                            (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:231)
2025-07-18 22:01:07,513 INFO    - DMCLI retv vs GPV comparison test completed successfully                                              (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_vs_gpv_comparison:233)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_retv.py::TestDMCLIRetv::test_dmcli_retv_api_methods 2025-07-18 22:01:07,524 INFO    - Starting DMCLI retv API methods test                                                                  (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_api_methods:242)
2025-07-18 22:01:07,525 INFO    - Checking retv and rValue API methods                                                                  (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_api_methods:251)
2025-07-18 22:01:07,525 INFO    - ✓ retv method is available and callable                                                               (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_api_methods:256)
2025-07-18 22:01:07,526 INFO    - ✓ rValue method is available and callable                                                             (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_api_methods:261)
2025-07-18 22:01:07,526 INFO    - ✓ Method signatures are correct                                                                       (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_api_methods:266)
2025-07-18 22:01:07,527 INFO    - ✓ retv and rValue are separate method objects                                                         (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_api_methods:274)
2025-07-18 22:01:07,527 INFO    - DMCLI retv API methods test completed successfully                                                    (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_api_methods:276)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_retv.py::TestDMCLIRetv::test_dmcli_retv_method 2025-07-18 22:01:07,535 INFO    - Starting DMCLI retv method test                                                                       (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:27)
2025-07-18 22:01:07,536 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:30)
2025-07-18 22:01:07,536 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:07,537 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:07,887 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:07,888 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:08,071 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:08,072 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:08,245 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:08,424 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:08,599 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:08,600 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:08,957 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:08,958 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:08,958 INFO    - VCPE device booted successfully                                                                       (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:35)
2025-07-18 22:01:08,958 INFO    - Testing DMCLI retv method                                                                             (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:48)
2025-07-18 22:01:08,959 DEBUG   - Executing dmcli command: dmcli eRT retv Device.DeviceInfo.SoftwareVersion                             (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:09,136 DEBUG   - dmcli command result: X86EMLTRBB_rdkb-2025q1-kirkstone_20250710065559                                 (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:09,136 INFO    - retv(Device.DeviceInfo.SoftwareVersion) = X86EMLTRBB_rdkb-2025q1-kirkstone_20250710065559             (boardfarm.vcpe.lib.dmcli_command:retv:393)
2025-07-18 22:01:09,137 INFO    - retv(Device.DeviceInfo.SoftwareVersion) = 'X86EMLTRBB_rdkb-2025q1-kirkstone_20250710065559'           (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:62)
2025-07-18 22:01:09,137 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.SoftwareVersion                        (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:09,320 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.SoftwareVersion
               type:     string,    value: X86EMLTRBB_rdkb-2025q1-kirkstone_20250710065559

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:09,320 INFO    - GPV(Device.DeviceInfo.SoftwareVersion) = Device.DeviceInfo.SoftwareVersion                            (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:01:09,321 INFO    - GPV(Device.DeviceInfo.SoftwareVersion) = 'Device.DeviceInfo.SoftwareVersion'                          (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:66)
2025-07-18 22:01:09,321 DEBUG   - Executing dmcli command: dmcli eRT retv Device.DeviceInfo.SerialNumber                                (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:09,503 DEBUG   - dmcli command result: 00163E207968                                                                    (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:09,503 INFO    - retv(Device.DeviceInfo.SerialNumber) = 00163E207968                                                   (boardfarm.vcpe.lib.dmcli_command:retv:393)
2025-07-18 22:01:09,504 INFO    - retv(Device.DeviceInfo.SerialNumber) = '00163E207968'                                                 (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:62)
2025-07-18 22:01:09,504 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.SerialNumber                           (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:09,665 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.SerialNumber
               type:     string,    value: 00163E207968

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:09,665 INFO    - GPV(Device.DeviceInfo.SerialNumber) = Device.DeviceInfo.SerialNumber                                  (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:01:09,666 INFO    - GPV(Device.DeviceInfo.SerialNumber) = 'Device.DeviceInfo.SerialNumber'                                (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:66)
2025-07-18 22:01:09,666 DEBUG   - Executing dmcli command: dmcli eRT retv Device.DeviceInfo.Manufacturer                                (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:09,828 DEBUG   - dmcli command result: Raspberry Pi Foundation                                                         (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:09,828 INFO    - retv(Device.DeviceInfo.Manufacturer) = Raspberry Pi Foundation                                        (boardfarm.vcpe.lib.dmcli_command:retv:393)
2025-07-18 22:01:09,829 INFO    - retv(Device.DeviceInfo.Manufacturer) = 'Raspberry Pi Foundation'                                      (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:62)
2025-07-18 22:01:09,829 DEBUG   - Executing dmcli command: dmcli eRT getvalues Device.DeviceInfo.Manufacturer                           (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:10,024 DEBUG   - dmcli command result: CR component name is: eRT.com.cisco.spvtg.ccsp.CR
subsystem_prefix eRT.
Execution succeed.
Parameter    1 name: Device.DeviceInfo.Manufacturer
               type:     string,    value: Raspberry Pi Foundation

  (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:10,025 INFO    - GPV(Device.DeviceInfo.Manufacturer) = Device.DeviceInfo.Manufacturer                                  (boardfarm.vcpe.lib.dmcli_command:GPV:79)
2025-07-18 22:01:10,025 INFO    - GPV(Device.DeviceInfo.Manufacturer) = 'Device.DeviceInfo.Manufacturer'                                (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:66)
2025-07-18 22:01:10,026 INFO    - Successfully retrieved 3/3 parameters using retv                                                      (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:87)
2025-07-18 22:01:10,026 INFO    - DMCLI retv method test completed successfully                                                         (vcpe_only_tests.test_dmcli_retv:test_dmcli_retv_method:88)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_retv.py::TestDMCLIRetv::test_dmcli_rvalue_alias 2025-07-18 22:01:10,038 INFO    - Starting DMCLI rValue alias test                                                                      (vcpe_only_tests.test_dmcli_retv:test_dmcli_rvalue_alias:97)
2025-07-18 22:01:10,038 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_dmcli_retv:test_dmcli_rvalue_alias:100)
2025-07-18 22:01:10,039 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:10,039 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:10,431 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:10,432 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:10,630 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:10,630 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:10,843 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:11,026 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:11,200 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:11,200 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:11,554 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:11,555 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:11,555 INFO    - Testing DMCLI rValue alias method                                                                     (vcpe_only_tests.test_dmcli_retv:test_dmcli_rvalue_alias:117)
2025-07-18 22:01:11,556 DEBUG   - Executing dmcli command: dmcli eRT retv Device.DeviceInfo.ModelName                                   (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:11,724 DEBUG   - dmcli command result: RPI                                                                             (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:11,724 INFO    - retv(Device.DeviceInfo.ModelName) = RPI                                                               (boardfarm.vcpe.lib.dmcli_command:retv:393)
2025-07-18 22:01:11,724 INFO    - rValue(Device.DeviceInfo.ModelName) = 'RPI'                                                           (vcpe_only_tests.test_dmcli_retv:test_dmcli_rvalue_alias:124)
2025-07-18 22:01:11,725 DEBUG   - Executing dmcli command: dmcli eRT retv Device.DeviceInfo.ModelName                                   (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:52)
2025-07-18 22:01:11,903 DEBUG   - dmcli command result: RPI                                                                             (boardfarm.vcpe.lib.dmcli_command:_execute_dmcli_command:54)
2025-07-18 22:01:11,904 INFO    - retv(Device.DeviceInfo.ModelName) = RPI                                                               (boardfarm.vcpe.lib.dmcli_command:retv:393)
2025-07-18 22:01:11,904 INFO    - retv(Device.DeviceInfo.ModelName) = 'RPI'                                                             (vcpe_only_tests.test_dmcli_retv:test_dmcli_rvalue_alias:128)
2025-07-18 22:01:11,905 INFO    - ✓ rValue alias works correctly and matches retv output                                                (vcpe_only_tests.test_dmcli_retv:test_dmcli_rvalue_alias:137)
2025-07-18 22:01:11,905 INFO    - DMCLI rValue alias test completed successfully                                                        (vcpe_only_tests.test_dmcli_retv:test_dmcli_rvalue_alias:147)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_vcpe_command.py::TestVCPECommand::test_vcpe_uptime_command 2025-07-18 22:01:11,917 INFO    - Starting VCPE uptime command test                                                                     (vcpe_only_tests.test_vcpe_command:test_vcpe_uptime_command:62)
2025-07-18 22:01:11,917 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_vcpe_command:test_vcpe_uptime_command:65)
2025-07-18 22:01:11,918 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:11,918 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:12,302 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:12,303 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:12,483 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:12,483 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:12,665 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:12,862 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:13,041 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:13,041 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:13,377 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:13,378 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:13,378 INFO    - VCPE device booted successfully                                                                       (vcpe_only_tests.test_vcpe_command:test_vcpe_uptime_command:70)
2025-07-18 22:01:13,379 INFO    - Sending 'uptime' command to VCPE device                                                               (vcpe_only_tests.test_vcpe_command:test_vcpe_uptime_command:80)
2025-07-18 22:01:13,549 INFO    - Uptime result: 15:01:13 up 1 day,  1:35,  0 users,  load average: 0.54, 0.37, 0.35                    (vcpe_only_tests.test_vcpe_command:test_vcpe_uptime_command:82)
2025-07-18 22:01:13,550 INFO    - VCPE uptime command test completed successfully                                                       (vcpe_only_tests.test_vcpe_command:test_vcpe_uptime_command:88)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_vcpe_command.py::TestVCPECommand::test_vcpe_basic_command 2025-07-18 22:01:13,561 INFO    - Starting VCPE basic command test                                                                      (vcpe_only_tests.test_vcpe_command:test_vcpe_basic_command:27)
2025-07-18 22:01:13,561 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_vcpe_command:test_vcpe_basic_command:30)
2025-07-18 22:01:13,562 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:13,562 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:13,909 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:13,910 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:14,076 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:14,077 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:14,219 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:14,420 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:14,602 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:14,603 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:14,934 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:14,935 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:14,935 INFO    - VCPE device booted successfully                                                                       (vcpe_only_tests.test_vcpe_command:test_vcpe_basic_command:35)
2025-07-18 22:01:14,936 INFO    - Sending 'uname -a' command to VCPE device                                                             (vcpe_only_tests.test_vcpe_command:test_vcpe_basic_command:45)
2025-07-18 22:01:15,089 INFO    - Command result: Linux RaspberryPi-Gateway 5.15.131 #1 SMP Thu Jan 4 14:06:24 PST 2024 i686 GNU/Linux  (vcpe_only_tests.test_vcpe_command:test_vcpe_basic_command:47)
2025-07-18 22:01:15,089 INFO    - VCPE basic command test completed successfully                                                        (vcpe_only_tests.test_vcpe_command:test_vcpe_basic_command:53)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_vcpe_system_monitoring.py::TestVCPESystemMonitoring::test_vcpe_comprehensive_health_check 2025-07-18 22:01:15,101 INFO    - Starting VCPE comprehensive health check test                                                         (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:293)
2025-07-18 22:01:15,101 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:296)
2025-07-18 22:01:15,102 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:15,102 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:15,494 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:15,495 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:15,681 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:15,682 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:15,852 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:16,032 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:16,207 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:16,208 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:16,566 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:16,567 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:16,567 INFO    - Collecting system uptime...                                                                           (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:312)
2025-07-18 22:01:16,745 INFO    - Collecting memory utilization...                                                                      (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:316)
2025-07-18 22:01:16,909 INFO    - Collecting load average...                                                                            (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:320)
2025-07-18 22:01:17,070 INFO    - Checking online status...                                                                             (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:324)
2025-07-18 22:01:17,428 INFO    - Counting running processes...                                                                         (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:328)
2025-07-18 22:01:17,605 INFO    - === VCPE DEVICE HEALTH REPORT ===                                                                     (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:333)
2025-07-18 22:01:17,606 INFO    - Uptime: 92162.3 seconds (25.60 hours)                                                                 (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:334)
2025-07-18 22:01:17,606 INFO    - Memory Total: 512 MB                                                                                  (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:335)
2025-07-18 22:01:17,607 INFO    - Memory Used: 162 MB (31.6%)                                                                           (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:336)
2025-07-18 22:01:17,607 INFO    - Memory Available: 274 MB                                                                              (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:337)
2025-07-18 22:01:17,608 INFO    - Load Average: 0.58                                                                                    (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:338)
2025-07-18 22:01:17,608 INFO    - Online Status: True                                                                                   (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:339)
2025-07-18 22:01:17,609 INFO    - Running Processes: 71                                                                                 (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:340)
2025-07-18 22:01:17,609 INFO    - === END HEALTH REPORT ===                                                                             (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:341)
2025-07-18 22:01:17,609 INFO    - Overall Health Score: 100/100                                                                         (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:372)
2025-07-18 22:01:17,610 INFO    - VCPE comprehensive health check completed successfully                                                (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_comprehensive_health_check:379)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_vcpe_system_monitoring.py::TestVCPESystemMonitoring::test_vcpe_running_processes 2025-07-18 22:01:17,621 INFO    - Starting VCPE running processes test                                                                  (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_running_processes:174)
2025-07-18 22:01:17,622 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_running_processes:177)
2025-07-18 22:01:17,622 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:17,623 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:17,930 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:17,930 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:18,128 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:18,129 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:18,304 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:18,478 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:18,634 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:18,634 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:19,014 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:19,015 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:19,015 INFO    - Getting running processes from VCPE device                                                            (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_running_processes:190)
2025-07-18 22:01:19,232 INFO    - Found 71 running processes                                                                            (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_running_processes:192)
2025-07-18 22:01:19,233 INFO    - Process 1: PID=1, CMD={systemd} /sbin/init                                                            (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_running_processes:201)
2025-07-18 22:01:19,233 INFO    - Process 2: PID=34, CMD=/lib/systemd/systemd-journald                                                  (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_running_processes:201)
2025-07-18 22:01:19,234 INFO    - Process 3: PID=70, CMD={rssfree} /bin/sh /usr/bin/rssfree                                             (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_running_processes:201)
2025-07-18 22:01:19,234 INFO    - Process 4: PID=79, CMD=/sbin/klogd -n                                                                 (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_running_processes:201)
2025-07-18 22:01:19,234 INFO    - Process 5: PID=80, CMD=/sbin/syslogd -n                                                               (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_running_processes:201)
2025-07-18 22:01:19,235 INFO    - VCPE running processes test completed successfully                                                    (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_running_processes:223)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_vcpe_system_monitoring.py::TestVCPESystemMonitoring::test_vcpe_memory_utilization 2025-07-18 22:01:19,247 INFO    - Starting VCPE memory utilization test                                                                 (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_memory_utilization:29)
2025-07-18 22:01:19,247 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_memory_utilization:32)
2025-07-18 22:01:19,248 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:19,248 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:19,632 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:19,633 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:19,840 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:19,841 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:20,037 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:20,189 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:20,370 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:20,371 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:20,710 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:20,711 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:20,711 INFO    - VCPE device booted successfully                                                                       (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_memory_utilization:37)
2025-07-18 22:01:20,711 INFO    - Getting memory utilization from VCPE device                                                           (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_memory_utilization:47)
2025-07-18 22:01:20,884 INFO    - Memory utilization: {'total': 512, 'used': 162, 'free': 243, 'shared': 74, 'cache': 105, 'available': 274}  (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_memory_utilization:49)
2025-07-18 22:01:20,884 INFO    - Memory usage: 31.6%                                                                                   (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_memory_utilization:68)
2025-07-18 22:01:20,885 INFO    - VCPE memory utilization test completed successfully                                                   (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_memory_utilization:73)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_vcpe_system_monitoring.py::TestVCPESystemMonitoring::test_vcpe_load_average 2025-07-18 22:01:20,897 INFO    - Starting VCPE load average test                                                                       (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_load_average:130)
2025-07-18 22:01:20,898 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_load_average:133)
2025-07-18 22:01:20,898 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:20,899 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:21,261 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:21,263 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:21,484 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:21,485 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:21,672 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:21,850 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:22,027 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:22,027 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:22,358 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:22,359 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:22,359 INFO    - Getting system load average from VCPE device                                                          (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_load_average:146)
2025-07-18 22:01:22,527 INFO    - System load average (1 min): 0.53                                                                     (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_load_average:148)
2025-07-18 22:01:22,528 INFO    - System load is light                                                                                  (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_load_average:159)
2025-07-18 22:01:22,528 INFO    - VCPE load average test completed successfully                                                         (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_load_average:165)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_vcpe_system_monitoring.py::TestVCPESystemMonitoring::test_vcpe_network_interface_status 2025-07-18 22:01:22,540 INFO    - Starting VCPE network interface status test                                                           (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:232)
2025-07-18 22:01:22,540 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:235)
2025-07-18 22:01:22,541 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:22,541 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:22,920 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:22,921 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:23,067 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:23,068 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:23,254 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:23,421 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:23,591 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:23,591 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:23,950 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:23,950 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:23,951 INFO    - Checking if VCPE device is online                                                                     (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:248)
2025-07-18 22:01:24,280 INFO    - Device online status: True                                                                            (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:250)
2025-07-18 22:01:24,281 INFO    - Checking interface: brlan0                                                                            (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:258)
2025-07-18 22:01:24,449 INFO    - Interface brlan0 link up: True                                                                        (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:263)
2025-07-18 22:01:24,622 INFO    - Interface brlan0 MAC: 00:16:3e:16:5f:7c                                                               (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:268)
2025-07-18 22:01:24,798 INFO    - Interface brlan0 IPv4: STDERR: head: invalid option -- '1'
BusyBox v1.35.0 () multi-call binary.

Usage: head [OPTIONS] [FILE]...  (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:275)
2025-07-18 22:01:24,799 INFO    - Checking interface: erouter0                                                                          (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:258)
2025-07-18 22:01:24,966 INFO    - Interface erouter0 link up: True                                                                      (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:263)
2025-07-18 22:01:25,138 INFO    - Interface erouter0 MAC: 00:16:3e:20:79:68                                                             (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:268)
2025-07-18 22:01:25,347 INFO    - Interface erouter0 IPv4: STDERR: head: invalid option -- '1'
BusyBox v1.35.0 () multi-call binary.

Usage: head [OPTIONS] [FILE]...  (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:275)
2025-07-18 22:01:25,348 INFO    - VCPE network interface status test completed successfully                                             (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_network_interface_status:284)
PASSED
boardfarm/vcpe/tests/vcpe_only_tests/test_vcpe_system_monitoring.py::TestVCPESystemMonitoring::test_vcpe_system_uptime 2025-07-18 22:01:25,359 INFO    - Starting VCPE system uptime test                                                                      (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_system_uptime:82)
2025-07-18 22:01:25,360 INFO    - Got VCPE device: vcpe(lxd_vcpe)                                                                       (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_system_uptime:85)
2025-07-18 22:01:25,360 INFO    - Booting vcpe(lxd_vcpe) device                                                                         (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:379)
2025-07-18 22:01:25,361 INFO    - Connecting to vcpe LXD container console                                                              (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:99)
2025-07-18 22:01:25,734 INFO    - Successfully connected to vcpe LXD container                                                          (boardfarm.vcpe.devices.lxd_device:connect_to_consoles:121)
2025-07-18 22:01:25,735 INFO    - Waiting for vcpe hardware to boot                                                                     (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:326)
2025-07-18 22:01:25,919 INFO    - vcpe hardware boot completed                                                                          (boardfarm.vcpe.devices.lxd_device:wait_for_hw_boot:335)
2025-07-18 22:01:25,919 INFO    - Verifying VCPE network interfaces                                                                     (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:121)
2025-07-18 22:01:26,084 INFO    - Available interfaces: ['lo', 'br403', 'brebhaul', 'br106', 'brlan0', 'brlan2', 'brlan3', 'br0', 'wlan0', 'wlan1', 'wlan2', 'wlan3']  (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:129)
2025-07-18 22:01:26,256 INFO    - vCPE configuration file found                                                                         (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:134)
2025-07-18 22:01:26,434 INFO    - NVRAM storage volume mounted                                                                          (boardfarm.vcpe.devices.lxd_vcpe:wait_for_hw_boot:141)
2025-07-18 22:01:26,434 INFO    - Waiting for vcpe to come online                                                                       (boardfarm.vcpe.devices.lxd_device:wait_device_online:392)
2025-07-18 22:01:26,808 INFO    - vcpe is online                                                                                        (boardfarm.vcpe.devices.lxd_device:wait_device_online:397)
2025-07-18 22:01:26,808 INFO    - VCPE device boot completed                                                                            (boardfarm.vcpe.devices.lxd_vcpe:boardfarm_device_boot:391)
2025-07-18 22:01:26,809 INFO    - Getting system uptime from VCPE device                                                                (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_system_uptime:98)
2025-07-18 22:01:26,982 INFO    - System uptime: 92172.5 seconds                                                                        (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_system_uptime:100)
2025-07-18 22:01:26,983 INFO    - System uptime: 1.07 days, 25.60 hours, 1536.21 minutes                                                (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_system_uptime:111)
2025-07-18 22:01:29,230 INFO    - VCPE system uptime test completed successfully                                                        (vcpe_only_tests.test_vcpe_system_monitoring:test_vcpe_system_uptime:121)
PASSED
Skipping device shutdown due to --skip-shutdown option


=============================================================================================================================== 28 passed in 52.92s ================================================================================================================================
root@boardfarm:~#
```
</details>

## Run specific test categories:

```text
# Test LXD device operations
[root@boardfarm boardfarm]# pytest boardfarm/vcpe/tests/vcpe_only_tests/test_lxd_power_cycle.py -v

# Test DMCLI command interface
[root@boardfarm boardfarm]# pytest boardfarm/vcpe/tests/vcpe_only_tests/test_dmcli_command.py -v

# Test device imports and configurations
[root@boardfarm boardfarm]# pytest boardfarm/vcpe/tests/test_misc_lxd_operations_simple.py -v
```

# Test Environment Configuration

## Device Inventory Structure:

The test framework uses JSON inventory files defining available test devices:

- **vcpe_only_inventory.json**: Single VCPE device configuration
- **vcpe_inventory.json**: Full testbed with multiple device types

## Supported Device Types:

- **lxd_vcpe**: Virtual CPE device for router/gateway testing
- **lxd_bng**: Broadband Network Gateway simulation
- **lxd_lan**: LAN client simulation
- **lxd_wlan**: Wireless LAN client simulation
- **lxd_genieacs**: TR-069 ACS server
- **lxd_oktopus**: USP controller
- **lxd_webpa**: WebPA protocol server
- **lxd_xconf**: Configuration management
- **lxd_telemetry**: Telemetry data collection

## Test Configuration Files:

```text
boardfarm/vcpe/
├── pytest.ini                    # Full testbed pytest configuration
├── vcpe_only_pytest.ini         # VCPE-only pytest configuration
├── vcpe_inventory.json           # All devices inventory
├── vcpe_only_inventory.json      # VCPE-only inventory
└── tests/
    ├── vcpe_only_tests/          # VCPE-specific tests
    ├── test_misc_lxd_operations_simple.py  # Device import/config tests
    ├── test_lxd_websocket_consolidated.py  # WebSocket connectivity tests
    └── test_websocket_command_execution.py # Command execution tests
```

# Network Architecture

## LXD Container Network:

- **LXD Host**: 192.168.2.120:8443 (API endpoint)
- **Container Network**: 10.0.3.x/24 (boardfarm container)
- **Device Network**: 10.10.10.x/24 (test device containers)

## Authentication:

- Client certificates: `/root/.config/lxc/client.crt` and `/root/.config/lxc/client.key`
- LXD API over HTTPS with certificate-based authentication
- Container-to-container communication via LXD REST API

# Advanced Testing

## Custom Test Development:

```python
import pytest
from boardfarm.vcpe.devices.lxd_vcpe import LXDVirtualCPE

def test_custom_vcpe_functionality():
    """Example custom test for VCPE device."""
    # Test implementation here
    pass
```

## WebSocket Testing:

```text
# Test LXD WebSocket connections
[root@boardfarm boardfarm]# cd boardfarm/vcpe/lxd-websocket
[root@boardfarm lxd-websocket]# ./lxd-websocket-shell-python.sh vcpe
```

## DMCLI Command Testing:

```python
# Test DMCLI parameter operations
from boardfarm.vcpe.lib.dmcli_command import DMCLICommand

dmcli = DMCLICommand(device)
result = dmcli.get_parameter("Device.DeviceInfo.ModelName")
```

# Troubleshooting

## Common Issues:

1. **LXD API Connection Failed**: Verify certificates and network connectivity
2. **Container Not Found**: Check container names in inventory configuration
3. **Test Timeouts**: Increase timeout values in device configurations

## Debug Mode:

```text
# Run tests with verbose output and debug logging
[root@boardfarm boardfarm]# pytest -v -s --log-cli-level=DEBUG boardfarm/vcpe/tests/vcpe_only_tests/
```

## Certificate Verification:

```text
# Verify LXD certificate authentication
[root@boardfarm ~]# openssl x509 -in /root/.config/lxc/client.crt -text -noout
```