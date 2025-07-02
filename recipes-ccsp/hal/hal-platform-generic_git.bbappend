
do_configure_append(){
    PATCH_FILE="${THISDIR}/files/0001-platform_hal-Switch-from-proc-cpuinfo-to-etc-vcpe-co.patch"
    if [ -f "${PATCH_FILE}" ] && [ -f ${S}/hal_platform.c ]; then
        echo "Applying 0001-platform_hal-Switch-from-proc-cpuinfo-to-etc-vcpe-co.patch to hal_platform.c"
        patch -p1 -d ${S} < "${PATCH_FILE}" || bbfatal "Failed to apply patch"
    fi
}
