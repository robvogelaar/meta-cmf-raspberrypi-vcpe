
do_configure_append(){
    PATCH_FILE="${THISDIR}/files/0001-Add-missing-pclose.patch"
    if [ -f "${PATCH_FILE}" ] && [ -f ${S}/ccsp_hal_ethsw.c ]; then
        echo "Applying 0001-Add-missing-pclose.patch to ccsp_hal_ethsw.c"
        patch -p1 -d ${S} < "${PATCH_FILE}" || bbfatal "Failed to apply patch"
    fi
}
