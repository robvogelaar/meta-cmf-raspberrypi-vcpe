# Devices

Device will be found in genie acs as:  FFFFFF-ER-00163E207968

## GetParameterValues

```text
curl -i 'http://localhost:7557/devices/FFFFFF-ER-00163E207968/tasks?timeout=3000&connection_request' \
-X POST \
--data '{"name": "getParameterValues", "parameterNames": ["Device.DeviceInfo.SerialNumber"] }'
```


```text
curl -i 'http://localhost:7557/devices?query=%7B%22_id%22%3A%22FFFFFF-ER-00163E207968%22%7D&projection=Device.DeviceInfo.SerialNumber'
HTTP/1.1 200 OK
GenieACS-Version: 1.2.13+240606fc80
Content-Type: application/json
total: 1
Date: Wed, 02 Jul 2025 21:35:22 GMT
Connection: keep-alive
Keep-Alive: timeout=5
Transfer-Encoding: chunked

[
{"_id":"FFFFFF-ER-00163E207968","Device":{"DeviceInfo":{"SerialNumber":{"_object":false,"_timestamp":"2025-07-02T21:31:36.756Z","_type":"xsd:string","_value":"00163E207968","_writable":false}}}}
]root@genieacs:~#
```
