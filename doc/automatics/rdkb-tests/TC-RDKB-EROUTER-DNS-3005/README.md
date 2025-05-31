# Test Case: TC-RDKB-EROUTER-DNS-3005

## Test Name
IPv4 DNS Query from LAN IPv4 Host

## Test Description
Verify IPv4 DNS query from LAN IPv4 host. The eRouter must be able to respond to an A DNS queries with its own IPv4 address.

## Test Category
System Test

## Prerequisites
- Device under test (DUT) available
- TFTP server configured and accessible
- Ethernet client device available for connection

## Test Steps

### 1. Configure TFTP Server
- **Action**: Get TFTP server details and add device config file
- **Configure**: Device to operate in IPv4 mode using config file
- **Expected**: Files should be added successfully and device configured for IPv4 mode

### 2. Device Mode Configuration
- **Action**: Reboot the device and verify device mode
- **Wait**: For device to come up in IPv4 operational mode
- **Expected**: The DUT should be in IPv4 operational mode

### 3. Client Device Setup
- **Action**: Retrieve ethernet client device from device manager
- **Verify**: Client connectivity to the router
- **Expected**: LAN client should be retrieved successfully

### 4. DNS Configuration Verification
- **Check**: `/etc/resolv.conf` file on the device
- **Verify**: It's NOT configured with local DNS server (127.0.0.1)
- **Get**: Default DNS IP of the DUT
- **Expected**: Should be able to get file contents and verify local DNS server is not present

### 5. DNS Query Functionality Test
- **Execute**: DNS query using `dig google.com` command on DUT
- **Verify**: DNS server in DUT responds to DNS query from LAN client
- **Check**: If entries are present in DNS cache or forwarded to upstream DNS server
- **Extract**: And verify DNS server address from response
- **Expected**: DNS server in DUT responds to DNS query successfully

## Post-Conditions
- Change device mode back to dual stack
- Reboot device and verify dual stack mode operation

## Pass/Fail Criteria
- ✅ All test steps must pass for overall test case to pass
- ✅ Device must successfully operate in IPv4 mode
- ✅ DNS queries must be resolved properly through the eRouter
- ✅ eRouter must respond with appropriate DNS information

## Test Data
- Uses Google DNS (google.com) for DNS resolution testing
- Validates A record queries specifically
- Checks DNS server address extraction from dig command output

---

## Test Primitives Used

### Test Framework Primitives

#### TestNG Framework
- `@Test` annotation with parameters (enabled, dataProvider, alwaysRun, groups)
- `@TestDetails` annotation for test metadata

### Device Communication Primitives

#### WebPA/DMCLI Operations
- `BroadBandWebPaUtils.getParameterValuesUsingWebPaOrDmcli()` - Parameter retrieval
- `BroadBandWebPaUtils.getParameterValuesUsingWebPaOrDmcliAndVerify()` - Parameter verification

#### SSH Command Execution
- `tapEnv.executeCommandUsingSsh()` - Execute shell commands on device

### Device Management Primitives

#### Device Configuration
- `BroadBandConnectedClientUtils.getTFTPServerDetails()` - TFTP server setup
- `BroadBandConnectedClientUtils.setDeviceModeUsingConfigFile()` - Device mode configuration
- `BroadBandConnectedClientUtils.rebootTheDeviceUsingDMCLIAndWaitForEstbIpAcquisition()` - Device reboot

#### Client Device Management
- `BroadBandConnectedClientUtils.getEthernetConnectedClient()` - Ethernet client retrieval

### Test Execution Primitives

#### Status Tracking
- `tapEnv.updateExecutionStatus()` - Update test step status
- Boolean status flags for pass/fail tracking

#### Timing Controls
- `tapEnv.waitTill()` - Wait/delay operations
- Loop constructs with retry logic

### Logging Primitives

#### Test Logging
- `LOGGER.info()` - Information logging
- `LOGGER.error()` - Error logging
- Structured step logging with descriptions, actions, and expected results

### Data Validation Primitives

#### String Operations
- `CommonMethods.isNotNull()` - Null checking
- `CommonMethods.patternFinder()` - Pattern extraction from text
- `String.contains()` - String containment checks
- `String.equalsIgnoreCase()` - Case-insensitive comparison

### Network Testing Primitives

#### DNS Testing
- `dig` command execution for DNS queries
- DNS server address extraction from command output
- DNS configuration file analysis (`/etc/resolv.conf`)

### Test Constants

#### Configuration Constants
- `BroadBandTestConstants.DMCLI_PARAMETER_DEVICE_MODE` - Device mode parameter
- `BroadBandTestConstants.COMMAND_TO_GET_DEVICE_DNS_CONFIG` - DNS config command
- `BroadBandTestConstants.COMMAND_DIG_QUERIE_USING_GOOGLE_ADDRESS` - DNS query command
- Various timeout constants (`THIRTY_SECOND_IN_MILLIS`, etc.)

### Error Handling Primitives

#### Exception Management
- Try-catch blocks around critical operations
- Exception message logging
- Graceful failure handling with error messages

### Test Lifecycle Primitives

#### Setup/Teardown
- Pre-condition checks
- Post-condition cleanup (device mode restoration)
- Finally blocks for cleanup operations

> **Note**: These primitives provide a comprehensive test automation framework for RDK-B device testing, covering device communication, configuration management, network testing, and result validation.
