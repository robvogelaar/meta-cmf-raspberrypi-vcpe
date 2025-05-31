FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

# Remove wifi from device profile (wifi does not complete initialization)
# Add tr69 to device profile

SRC_URI_append = " \
    file://cr-deviceprofile_rpi.xml \
"

do_install_append() {
    # Config files and scripts
    install -m 644 ${WORKDIR}/cr-deviceprofile_rpi.xml ${D}/usr/ccsp/cr-deviceprofile.xml
    install -m 644 ${WORKDIR}/cr-deviceprofile_rpi.xml ${D}/usr/ccsp/cr-ethwan-deviceprofile.xml
}
