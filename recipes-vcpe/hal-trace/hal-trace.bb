SUMMARY = "Trace header files for all CCSP HAL components"
LICENSE = "CLOSED"

SRC_URI = " \
    file://configure.ac \
    file://Makefile.am \
    file://hal-trace.h \
"

SRCREV ?= "${AUTOREV}"

S = "${WORKDIR}"

inherit autotools
