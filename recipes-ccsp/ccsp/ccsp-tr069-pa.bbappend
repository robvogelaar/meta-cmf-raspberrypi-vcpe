FILESEXTRAPATHS:prepend := "${THISDIR}/${BPN}:"

SRC_URI += "file://0001-fixup-prompt-system-ready-event-retrieval.patch"

CFLAGS:append = " -D_SUPPORT_HTTP"
