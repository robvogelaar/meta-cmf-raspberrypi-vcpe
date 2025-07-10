do_configure_append(){
    PATCH_DIR="${TOPDIR}/../meta-cmf-raspberrypi-vcpe/recipes-ccsp/hal/${PN}"
    cd ${S}/devices_rpi
    patch -p1 < "${PATCH_DIR}/0001-platform_hal-Switch-from-proc-cpuinfo-to-etc-vcpe-co.patch"
}
