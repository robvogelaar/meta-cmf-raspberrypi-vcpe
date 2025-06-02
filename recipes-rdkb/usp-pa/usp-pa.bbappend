FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI:append = " \
    file://oktopus-mqtt-obuspa.txt \
    file://oktopus-stomp-obuspa.txt \
    file://oktopus-websockets-obuspa.txt \
"


do_install:append() {
    # Install systemd custom limits configuration
    install -d ${D}${sysconfdir}/usp-pa
    install -m 0644 ${WORKDIR}/oktopus-mqtt-obuspa.txt ${D}${sysconfdir}/usp-pa
    install -m 0644 ${WORKDIR}/oktopus-stomp-obuspa.txt ${D}${sysconfdir}/usp-pa
    install -m 0644 ${WORKDIR}/oktopus-websockets-obuspa.txt ${D}${sysconfdir}/usp-pa
}

FILES:${PN} += " \
    ${sysconfdir}/usp-pa/ \
"
