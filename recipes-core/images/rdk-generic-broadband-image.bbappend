
IMAGE_INSTALL_append = " \
    vcpe-init \
"

IMAGE_INSTALL_append = " \
    tcpdump \
    strace \
    lsof \
    netcat-openbsd \
    iperf3 \
"

# procps provides an uptime which uses /proc/uptime and therefor
# reports container-uptime i.o host-uptime as per busybox uptime
# 

IMAGE_INSTALL_append = " \
    procps \
    procps-ps \
"
