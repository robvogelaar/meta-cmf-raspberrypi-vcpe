SUMMARY = "vCPE initialization and configuration"
DESCRIPTION = "Service and configuration files for vCPE initialization"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://10-custom-limits.conf \
    file://vcpe-init.service \
    file://vcpe-init.sh \
    file://vcpe-bash-history-backup.service \
    file://Blocklist_file.default \
    file://SaveConfigFile.sh \
    file://GetConfigFile.sh \
    file://rssfree.sh \
"

inherit systemd

SYSTEMD_SERVICE:${PN} = "vcpe-init.service vcpe-bash-history-backup.service"

SYSTEMD_AUTO_ENABLE = "enable"

do_install() {
    # Install systemd custom limits configuration
    install -d ${D}${sysconfdir}/systemd/system.conf.d/
    install -m 0644 ${WORKDIR}/10-custom-limits.conf ${D}${sysconfdir}/systemd/system.conf.d/

    # Install systemd service
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/vcpe-init.service ${D}${systemd_system_unitdir}

    # Create the symlink for auto-enabling the service
    install -d ${D}${sysconfdir}/systemd/system/multi-user.target.wants/
    ln -sf ${systemd_system_unitdir}/vcpe-init.service ${D}${sysconfdir}/systemd/system/multi-user.target.wants/vcpe-init.service

    # Install the service binary
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/vcpe-init.sh ${D}${bindir}/vcpe-init

    # Install systemd service
    install -m 0644 ${WORKDIR}/vcpe-bash-history-backup.service ${D}${systemd_system_unitdir}

    # Install default Blocklist file for CCSP components
    install -d ${D}/opt/secure
    install -m 0644 ${WORKDIR}/Blocklist_file.default ${D}/opt/secure/Blocklist_file.txt

    # Install the SaveConfigFile and GetConfigFile
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/SaveConfigFile.sh ${D}${bindir}/SaveConfigFile
    install -m 0755 ${WORKDIR}/GetConfigFile.sh ${D}${bindir}/GetConfigFile

    install -m 0755 ${WORKDIR}/rssfree.sh ${D}${bindir}/rssfree
}

FILES:${PN} += " \
    ${sysconfdir}/systemd/system.conf.d/10-custom-limits.conf \
    ${systemd_system_unitdir}/vcpe-init.service \
    ${sysconfdir}/systemd/system/multi-user.target.wants/vcpe-init.service \
    ${bindir}/vcpe-init \
    ${systemd_system_unitdir}/vcpe-bash-history-backup.service \
    /opt/secure/Blocklist_file.txt \
    ${bindir}/SaveConfigFile \
    ${bindir}/GetConfigFile \
    ${bindir}/rssfree \
"
