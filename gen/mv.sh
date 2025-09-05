#!/bin/bash

source gen-util.sh

usage() {
    local script_name=$(basename "$0")
    cat << EOF
Usage: ${script_name} <url/path/pattern to ofw_rootfs_image> <bng-id> [extra-id] [lan-p1|lan-p2|lan-p3|lan-p4=wanoe/mvx]

Examples:

   scp from remote directory:
   ${script_name} rev140:$HOME/yocto/mv1-lxd-r21-oe30-1120/build-exm-qemux86-mv1/tmp/deploy/images/exm-qemux86-mv1 7
   ${script_name} rev140:$HOME/yocto/mv2plus-lxd-r21-oe31-1120/brcm-openbfc-rdkm-scom/build-exm-qemux86-mv2plus/tmp/deploy/images/exm-qemux86-mv2plus 7
   ${script_name} rev140:$HOME/yocto/mv3-lxd-r21-oe31-1120/build-exm-qemux86-mv3/tmp/deploy/images/exm-qemux86-mv3 9

   scp from remote file:
   ${script_name} rev140:$HOME/yocto/mv1-lxd-r21-oe30-1120/build-exm-qemux86-mv1/tmp/deploy/images/exm-qemux86-mv1/ofw-exm-qemux86-mv1.tar.bz2 7
   ${script_name} rev140:$HOME/yocto/mv2plus-lxd-r21-oe31-1120/brcm-openbfc-rdkm-scom/build-exm-qemux86-mv2plus/tmp/deploy/images/exm-qemux86-mv2plus/ofw-exm-qemux86-mv2plus.tar.bz2 7
   ${script_name} rev140:$HOME/yocto/mv3-lxd-r21-oe31-1009/build-exm-qemux86-mv3/tmp/deploy/images/exm-qemux86-mv3/ofw-exm-qemux86-mv3.tar.bz2 9

   cp from local file:
   ${script_name} ofw-exm-qemux86-mv1.tar.bz2 7 001
   ${script_name} ofw-exm-qemux86-mv2plus.tar.bz2 7 001 lan-p1=mvx
   ${script_name} ofw-exm-qemux86-mv3.tar.bz2 9 001 lan-p2=custom

   https from image server:
   ${script_name} https://vcpe-images.vcpe.dev/mv1-r21.rootfs 7
   ${script_name} https://vcpe-images.vcpe.dev/mv2plus-r21.rootfs 7 lan-p3=special
   ${script_name} https://vcpe-images.vcpe.dev/mv3-r21.rootfs 9 lan-p4=test

   scp from remote directory using a directory pattern:
   ${script_name} mv1-r21-1120 7
   ${script_name} mv2plus-r21-1120 7
   ${script_name} mv3-r21-1120 9

Notes:

- bng-id must be 7, 8, 9, or 20
- If provided, extra-id must be a number between 001 and 099
- Optional lan port configuration:
    mv.sh mv2plus-r21-1126 7 lan-p4=wanoe               this lan port connects to wanoe-bridge with own vlan, there will be wan/cm, (managed bridge device)
    mv.sh mv2plus-r21-1126 7 001 lan-p1=mv2plus-r21-7   this lan port connects to wanoe-bridge with vlan of the mv specified, there will be no cm/wan, (wanoe mode connected via wanoe bridge to other cpe)
    mv.sh mv2plus-r21-1126 7 010 lan-p1=wan             this lan port connects to wan-bridge without a vlan, there will be no cm/wan, (wanoe mode connected to wan)

EOF
    exit 1
}

# Check minimum argument count
if [ $# -lt 2 ]; then
    usage
fi

# Get URL from first argument
url="$1"

# Validate second argument (bng-id)
case "$2" in
    7|8|9|20)
        bng_id="$2"
        ;;
    *)
        echo "Error: bng-id must be 7, 8, 9, or 20" >&2
        usage
        ;;
esac

# Initialize variables
extraindex=""
lan_p1=""
lan_p2=""
lan_p3=""
lan_p4=""

# Check maximum arguments
if [ $# -gt 4 ]; then
    echo "Error: Too many arguments" >&2
    usage
fi

# Parse optional arguments
if [ $# -ge 3 ]; then
    if [[ "${3}" =~ ^0[0-9][0-9]$ ]] && [ "${3}" != "000" ]; then
        extraindex="-${3}"
    elif [[ "${3}" =~ ^lan-p[1-4]=.+$ ]]; then
        port_num="${3:5:1}"
        value="${3#*=}"
        eval "lan_p${port_num}=\"$value\""
    else
        echo "Error: Invalid argument: ${3}" >&2
        usage
    fi
fi

if [ $# -eq 4 ]; then
    if [[ "${4}" =~ ^lan-p[1-4]=.+$ ]]; then
        port_num="${4:5:1}"
        value="${4#*=}"
        eval "lan_p${port_num}=\"$value\""
    else
        echo "Error: Invalid argument: ${4}" >&2
        usage
    fi
fi


# Validate first argument (url/path)
if [[ ! "$1" =~ (mv1|mng|mv2plus|mv3) ]]; then
    echo "Error: cannot determine mv1 or mv2plus or mv3" >&2
    exit 1
fi

if [[ ! "$1" =~ r(16|17|20|21|22) ]]; then
    echo "Error: cannot determine r16 or r17 or r20 or r21 or r22" >&2
    exit 1
fi

# Extract release version
rel=$(echo "$1" | grep -o 'r[0-9]\+')

# Set MV-specific variables
if [[ "$1" =~ (mng|mv1) ]]; then
    mv="mv1"
    rootsize=128MiB
    memorylimit=256MiB
    cpulimit="2"
elif [[ "$1" =~ mv2plus ]]; then
    mv="mv2plus"
    rootsize=256MiB
    memorylimit=512MiB
    cpulimit="2"
else
    mv="mv3"
    rootsize=256MiB
    memorylimit=512MiB
    cpulimit="2"
fi


base="${mv}-${rel}-$2"
imagename="ofw-${mv}-${rel}"

containername="${base}${extraindex}"
! validate_container_name "$containername" && echo "Invalid container name : $containername" && exit 1

profilename="${containername}"
volumename="${containername}-nvram"

vlan="$(validate_and_hash "${profilename}")"
[[ "$vlan" == "-1" ]] && { echo "cannot determine unique vlan"; exit 1; }


# Validate all four ports
for i in {1..4}; do
    validate_lan_port $i
done


mac1=$(generate_mac1 "$containername")
mac2=$(generate_mac2 "$containername")

if false; then
    echo imagename      = $imagename
    echo containername  = $containername
    echo profilename    = $profilename
    echo volumename     = $volumename
    echo mac1           = $mac1
    echo mac2           = $mac2
    echo lan_p1=$lan_p1
    echo lan_p2=$lan_p2
    echo lan_p3=$lan_p3
    echo lan_p4=$lan_p4
fi


mvrootfstarball="ofw-exm-qemux86-${mv}.tar.bz2"
mvdbgrootfstarball="ofw-exm-qemux86-${mv}-dbg.tar.bz2"

# Check if the path matches a simple pattern
#
if [[ $1 =~ ^(mv1|mv2plus|mv3)-(r21|r22)-(.+) ]]; then
    mv_part="${BASH_REMATCH[1]}"    # captures the mv part
    r_part="${BASH_REMATCH[2]}"     # captures the r part
    date="${BASH_REMATCH[3]}"       # captures everything after the second hyphen
    if [ "$r_part" == "r22" ]; then
        oe_part="oe40"
    else
        oe_part=$([ "$mv_part" == "mv1" ] && echo "oe30" || echo "oe31")
    fi
    subdir_part=$([ "$mv_part" == "mv2plus" ] && echo "brcm-openbfc-rdkm-scom" || echo "")

    url="rev140:/home/rev/yocto/${mv_part}-lxd-${r_part}-${oe_part}-${date}${subdir_part:+/}${subdir_part}/build-exm-qemux86-${mv_part}/tmp/deploy/images/exm-qemux86-${mv_part}/ofw-exm-qemux86-${mv_part}.tar.bz2"
    scp -p $url $M_ROOT/tmp

    exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "scp -p $1 $M_ROOT failed with exit status $exit_status"
        exit 1
    fi

# Check if the path matches https://
#
elif [[ "$1" =~ ^https://[^[:space:]]+ ]]; then
    if ! curl -f "$1" -o /dev/null 2>/dev/null; then
        echo "Error: Failed to download from $1" >&2
        exit 1
    fi

    curl --progress-bar "$1" | openssl aes-256-cbc -d -pass pass:"VeEp23!24" 2>/dev/null > "$M_ROOT/tmp/$mvrootfstarball" || {
        rm -f "$mvrootfstarball"
        echo "Error: Failed to decrypt content" >&2 
        exit 1
    }
    echo "Successfully downloaded and decrypted to $mvrootfstarball"

# Check if the path matches SCP syntax
#
elif [[ "$1" =~ ^([^@]+@)?[^:]+: ]]; then
    # Check if it ends with an extension, indicating it's likely a file
    if [[ "$1" =~ \.[^/]+$ ]]; then
        #echo "$1 is a remote file path."
        scp -p $1 $M_ROOT/tmp/${mvrootfstarball}
        exit_status=$?
        if [ $exit_status -ne 0 ]; then
            echo "scp -p $1 $M_ROOT failed with exit status $exit_status"
            exit 1
        fi
    else
        #echo "$1 is a remote directory path."
        scp -p $1/${mvrootfstarball} $M_ROOT/tmp/${mvrootfstarball}

        exit_status=$?
        if [ $exit_status -ne 0 ]; then
            echo "scp -p $1/${mvrootfstarball} $M_ROOT failed with exit status $exit_status"
            exit 1
        fi
    fi

# Check if the path matches a local path
#
elif [[ "$1" =~ \.[^/]+$ ]]; then
    # This is a local path
    cp -n $1 $M_ROOT/tmp/${mvrootfstarball}
    exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "cp $1 $M_ROOT failed with exit status $exit_status"
        exit 1
    fi

else
    usage
    exit 1
fi


lxc image delete ${imagename} 2> /dev/null

# Set the creation date to the current date and time in ISO 8601 format
creation_date=$(date +%s)
creation_stamp=$(date -r "$M_ROOT/tmp/${mvrootfstarball}" "+%Y%m%d_%H:%M")

# Create the metadata.yaml file with the desired content
cat > $M_ROOT/tmp/metadata.yaml << EOL
architecture: "i686"
creation_date: ${creation_date}
properties:
    description: "OFW LXD image (${creation_stamp})"
    os: ""
    release: ""
    version: ""
EOL

#echo "importing.."

tar czf $M_ROOT/tmp/metadata.tar.gz -C $M_ROOT/tmp metadata.yaml
lxc image import $M_ROOT/tmp/metadata.tar.gz $M_ROOT/tmp/${mvrootfstarball} --alias ${imagename}

echo "Configuring ${containername}"

lxc delete ${containername} -f > /dev/null 2>&1

lxc profile delete ${profilename} > /dev/null 2>&1

lxc profile copy default ${profilename} > /dev/null 2>&1


# https://documentation.ubuntu.com/lxd/en/stable-5.0/reference/instance_options/

##    lxc.cgroup.devices.allow = a
##    lxc.cgroup2.devices.allow = a
##    lxc.rootfs.options = rw
##    lxc.cap.drop =
##    lxc.cgroup.devices.allow =
##    lxc.cgroup.devices.deny =
##    lxc.mount.auto = proc:mixed sys:mixed cgroup:rw:force
##
##  security.nesting: "true"

##  devices:
##    loop-control:
##      path: /dev/loop-control
##      type: unix-char
##  
##    loop1:
##      path: /dev/loop1
##      type: unix-block
##    loop2:
##      path: /dev/loop2
##      type: unix-block
##    loop3:
##      path: /dev/loop3
##      type: unix-block
##    loop4:
##      path: /dev/loop4
##      type: unix-block
##    loop5:
##      path: /dev/loop5
##      type: unix-block



## config:
##  security.syscalls.intercept.netlink: "true"
##  raw.lxc: |
##    lxc.cap.drop=
##    lxc.cap.keep=CAP_NET_ADMIN CAP_SYS_PTRACE CAP_SYS_ADMIN
##    lxc.mount.auto=proc:rw sys:rw
##    lxc.apparmor.profile=unconfined
##    lxc.mount.auto=proc:rw sys:rw cgroup:rw
##    lxc.mount.entry=proc proc proc rw,nosuid,nodev,noexec,relatime 0 0

cat << EOF | lxc profile edit ${profilename}
name: ${containername}
description: "${containername}"
config:
    boot.autostart: "false"
    security.privileged: "true"
    security.nesting: "true"
    limits.memory: ${memorylimit}
    limits.memory.swap: "false"
    limits.cpu: "${cpulimit}"
devices:
    root:
        path: /
        pool: default
        type: disk
        size: ${rootsize}
EOF

# out of the box
# /proc/sys/fs/mqueue/msg_default         10
# /proc/sys/fs/mqueue/msg_max             100
# /proc/sys/fs/mqueue/msgsize_default     8192
# /proc/sys/fs/mqueue/msgsize_max         8192
# /proc/sys/fs/mqueue/queues_max          256

# sudo sysctl -w fs.mqueue.msg_max=1024
# sudo sysctl -w fs.mqueue.msgsize_max=4096
# sudo sysctl -w fs.mqueue.queues_max=1024


if [[ "$containername" == *"mv1"* ]]; then

    # Create lan/cm if all ports empty OR if any non-empty port is wanoe
    if [[ -z "${lan_p1}" && -z "${lan_p2}" && -z "${lan_p3}" && -z "${lan_p4}" ]] || \
       [[ -n "${lan_p1}" && "${lan_p1}" == "wanoe" ]] || \
       [[ -n "${lan_p2}" && "${lan_p2}" == "wanoe" ]] || \
       [[ -n "${lan_p3}" && "${lan_p3}" == "wanoe" ]] || \
       [[ -n "${lan_p4}" && "${lan_p4}" == "wanoe" ]]; then
        lxc profile device add ${profilename} wan0 nic nictype=bridged parent=cm name=wan0 1>/dev/null
        # erouter0
        lxc profile device add ${profilename} erouter0 nic nictype=bridged parent=wan name=erouter0 1>/dev/null
    else
        echo "Not creating cm and wan (wanoe mode)"
    fi

    # add vlan to lan-bridges or wanoe-bridge or wan-bridge

    if [[ -z "${lan_p1}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p1 self
    else
        if [[ "${lan_p1}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p1}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p1_vlan dev wanoe self
        fi
    fi

    if [[ -z "${lan_p2}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p2 self
    else
        if [[ "${lan_p2}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p2}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p2_vlan dev wanoe self
        fi
    fi

    if [[ -z "${lan_p3}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p3 self
    else
        if [[ "${lan_p3}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p3}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p3_vlan dev wanoe self
        fi
    fi

    if [[ -z "${lan_p4}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p4 self
    else
        if [[ "${lan_p4}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p4}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p4_vlan dev wanoe self
        fi
    fi


    # lan, 4 ports : eth0..3

    if [[ -z "${lan_p1}" ]]; then
       lxc profile device add ${profilename} eth0 nic nictype=bridged parent=lan-p1 name=eth0 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p1}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth0 nic nictype=bridged parent=wanoe name=eth0 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p1}" == "wan" ]]; then
           lxc profile device add ${profilename} eth0 nic nictype=bridged parent=wan name=eth0 1>/dev/null
       else
           lxc profile device add ${profilename} eth0 nic nictype=bridged parent=wanoe name=eth0 vlan=${lan_p1_vlan} 1>/dev/null
       fi
    fi

    if [[ -z "${lan_p2}" ]]; then
       lxc profile device add ${profilename} eth1 nic nictype=bridged parent=lan-p2 name=eth1 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p2}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth1 nic nictype=bridged parent=wanoe name=eth1 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p2}" == "wan" ]]; then
           lxc profile device add ${profilename} eth1 nic nictype=bridged parent=wan name=eth1 1>/dev/null
       else
           lxc profile device add ${profilename} eth1 nic nictype=bridged parent=wanoe name=eth1 vlan=${lan_p2_vlan} 1>/dev/null
       fi
    fi

    if [[ -z "${lan_p3}" ]]; then
       lxc profile device add ${profilename} eth2 nic nictype=bridged parent=lan-p3 name=eth2 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p3}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth2 nic nictype=bridged parent=wanoe name=eth2 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p3}" == "wan" ]]; then
           lxc profile device add ${profilename} eth2 nic nictype=bridged parent=wan name=eth2 1>/dev/null
       else
           lxc profile device add ${profilename} eth2 nic nictype=bridged parent=wanoe name=eth2 vlan=${lan_p3_vlan} 1>/dev/null
       fi
    fi

    if [[ -z "${lan_p4}" ]]; then
       lxc profile device add ${profilename} eth3 nic nictype=bridged parent=lan-p4 name=eth3 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p4}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth3 nic nictype=bridged parent=wanoe name=eth3 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p4}" == "wan" ]]; then
           lxc profile device add ${profilename} eth3 nic nictype=bridged parent=wan name=eth3 1>/dev/null
       else
           lxc profile device add ${profilename} eth3 nic nictype=bridged parent=wanoe name=eth3 vlan=${lan_p4_vlan} 1>/dev/null
       fi
    fi

    # nvram
    if ! lxc storage volume show default $volumename > /dev/null 2>&1; then
        lxc storage volume create default $volumename size=4MiB
    else
        :
        #echo "Volume $volumename exists, reusing"
    fi
    lxc profile device add $containername nvram disk pool=default source=$volumename path=/data/rdkb_nvram 1>/dev/null

    ## # share
    ## lxc profile device add $containername share disk source=$M_ROOT path=/share


elif [[ "$containername" == *"mv2plus"* ]]; then

    # Create lan/cm if all ports empty OR if any non-empty port is wanoe
    if [[ -z "${lan_p1}" && -z "${lan_p2}" && -z "${lan_p3}" && -z "${lan_p4}" ]] || \
       [[ -n "${lan_p1}" && "${lan_p1}" == "wanoe" ]] || \
       [[ -n "${lan_p2}" && "${lan_p2}" == "wanoe" ]] || \
       [[ -n "${lan_p3}" && "${lan_p3}" == "wanoe" ]] || \
       [[ -n "${lan_p4}" && "${lan_p4}" == "wanoe" ]]; then
        # cm, bcm0 is the cm interface in the cm
        lxc profile device add ${profilename} bcm0 nic nictype=bridged parent=cm name=bcm0 1>/dev/null
        # wan, cm0 is the wan interface in the rg
        lxc profile device add ${profilename} cm0 nic nictype=bridged parent=wan name=cm0 1>/dev/null
    else
        echo "Not creating cm and wan (wanoe mode)"
    fi

    # add vlan to lan-bridges or wanoe-bridge

    if [[ -z "${lan_p1}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p1 self
    else
        if [[ "${lan_p1}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p1}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p1_vlan dev wanoe self
        fi
    fi

    if [[ -z "${lan_p2}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p2 self
    else
        if [[ "${lan_p2}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p2}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p2_vlan dev wanoe self
        fi
    fi

    if [[ -z "${lan_p3}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p3 self
    else
        if [[ "${lan_p3}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p3}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p3_vlan dev wanoe self
        fi
    fi

    if [[ -z "${lan_p4}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p4 self
    else
        if [[ "${lan_p4}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p4}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p4_vlan dev wanoe self
        fi
    fi


    # lan, 4 ports : eth0..3

    if [[ -z "${lan_p1}" ]]; then
       lxc profile device add ${profilename} eth0 nic nictype=bridged parent=lan-p1 name=eth0 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p1}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth0 nic nictype=bridged parent=wanoe name=eth0 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p1}" == "wan" ]]; then
           lxc profile device add ${profilename} eth0 nic nictype=bridged parent=wan name=eth0 1>/dev/null
       else
           lxc profile device add ${profilename} eth0 nic nictype=bridged parent=wanoe name=eth0 vlan=${lan_p1_vlan} 1>/dev/null
       fi
    fi

    if [[ -z "${lan_p2}" ]]; then
       lxc profile device add ${profilename} eth1 nic nictype=bridged parent=lan-p2 name=eth1 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p2}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth1 nic nictype=bridged parent=wanoe name=eth1 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p2}" == "wan" ]]; then
           lxc profile device add ${profilename} eth1 nic nictype=bridged parent=wan name=eth1 1>/dev/null
       else
           lxc profile device add ${profilename} eth1 nic nictype=bridged parent=wanoe name=eth1 vlan=${lan_p2_vlan} 1>/dev/null
       fi
    fi

    if [[ -z "${lan_p3}" ]]; then
       lxc profile device add ${profilename} eth2 nic nictype=bridged parent=lan-p3 name=eth2 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p3}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth2 nic nictype=bridged parent=wanoe name=eth2 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p3}" == "wan" ]]; then
           lxc profile device add ${profilename} eth2 nic nictype=bridged parent=wan name=eth2 1>/dev/null
       else
           lxc profile device add ${profilename} eth2 nic nictype=bridged parent=wanoe name=eth2 vlan=${lan_p3_vlan} 1>/dev/null
       fi
    fi

    if [[ -z "${lan_p4}" ]]; then
       lxc profile device add ${profilename} eth3 nic nictype=bridged parent=lan-p4 name=eth3 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p4}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth3 nic nictype=bridged parent=wanoe name=eth3 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p4}" == "wan" ]]; then
           lxc profile device add ${profilename} eth3 nic nictype=bridged parent=wan name=eth3 1>/dev/null
       else
           lxc profile device add ${profilename} eth3 nic nictype=bridged parent=wanoe name=eth3 vlan=${lan_p4_vlan} 1>/dev/null
       fi
    fi


    #### # wlan
    #### lxc profile device add ${profilename} wl0 nic nictype=bridged parent=br-wlan0 name=wl0 vlan=${vlan} 1>/dev/null
    #### lxc profile device add ${profilename} wl1 nic nictype=bridged parent=br-wlan1 name=wl1 vlan=${vlan} 1>/dev/null

    # nvram
    if ! lxc storage volume show default $volumename > /dev/null 2>&1; then
        lxc storage volume create default $volumename size=4MiB 1>/dev/null
    else
        :
        #echo "Volume $volumename exists, reusing"
    fi
    lxc profile device add $containername nvram disk pool=default source=$volumename path=/data/rdkb_nvram 1>/dev/null

    ## # share
    ## lxc profile device add $containername share disk source=$M_ROOT path=/share


elif [[ "$containername" == *"mv3"* ]]; then

    #lxc profile device add ${profilename} veip0 nic nictype=bridged parent=wan name=veip0

    # Create lan/cm if all ports empty OR if any non-empty port is wanoe
    if [[ -z "${lan_p1}" && -z "${lan_p2}" && -z "${lan_p3}" && -z "${lan_p4}" ]] || \
       [[ -n "${lan_p1}" && "${lan_p1}" == "wanoe" ]] || \
       [[ -n "${lan_p2}" && "${lan_p2}" == "wanoe" ]] || \
       [[ -n "${lan_p3}" && "${lan_p3}" == "wanoe" ]] || \
       [[ -n "${lan_p4}" && "${lan_p4}" == "wanoe" ]]; then
        # eth0
        lxc profile device add ${profilename} eth0 nic nictype=bridged parent=wan name=eth0 1>/dev/null
    else
        echo "Not creating wan (wanoe mode)"
    fi

    # add vlan to lan-bridges or wanoe-bridge


    if [[ -z "${lan_p1}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p1 self
    else
        if [[ "${lan_p1}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p1}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p1_vlan dev wanoe self
        fi
    fi

    if [[ -z "${lan_p2}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p2 self
    else
        if [[ "${lan_p2}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p2}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p2_vlan dev wanoe self
        fi
    fi

    if [[ -z "${lan_p3}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p3 self
    else
        if [[ "${lan_p3}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p3}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p3_vlan dev wanoe self
        fi
    fi

    if [[ -z "${lan_p4}" ]]; then
        sudo bridge vlan add vid ${vlan} dev lan-p4 self
    else
        if [[ "${lan_p4}" == "wanoe" ]]; then
            sudo bridge vlan add vid ${vlan} dev wanoe self
        elif [[ "${lan_p4}" == "wan" ]]; then
            : # do nothing
        else
            sudo bridge vlan add vid $lan_p4_vlan dev wanoe self
        fi
    fi


    # lan, 4 ports : eth1..4

    if [[ -z "${lan_p1}" ]]; then
       lxc profile device add ${profilename} eth1 nic nictype=bridged parent=lan-p1 name=eth1 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p1}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth1 nic nictype=bridged parent=wanoe name=eth1 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p1}" == "wan" ]]; then
           lxc profile device add ${profilename} eth1 nic nictype=bridged parent=wan name=eth1 1>/dev/null
       else
           lxc profile device add ${profilename} eth1 nic nictype=bridged parent=wanoe name=eth1 vlan=${lan_p1_vlan} 1>/dev/null
       fi
    fi

    if [[ -z "${lan_p2}" ]]; then
       lxc profile device add ${profilename} eth2 nic nictype=bridged parent=lan-p2 name=eth2 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p2}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth2 nic nictype=bridged parent=wanoe name=eth2 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p2}" == "wan" ]]; then
           lxc profile device add ${profilename} eth2 nic nictype=bridged parent=wan name=eth2 1>/dev/null
       else
           lxc profile device add ${profilename} eth2 nic nictype=bridged parent=wanoe name=eth2 vlan=${lan_p2_vlan} 1>/dev/null
       fi
    fi

    if [[ -z "${lan_p3}" ]]; then
       lxc profile device add ${profilename} eth3 nic nictype=bridged parent=lan-p3 name=eth3 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p3}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth3 nic nictype=bridged parent=wanoe name=eth3 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p3}" == "wan" ]]; then
           lxc profile device add ${profilename} eth3 nic nictype=bridged parent=wan name=eth3 1>/dev/null
       else
           lxc profile device add ${profilename} eth3 nic nictype=bridged parent=wanoe name=eth3 vlan=${lan_p3_vlan} 1>/dev/null
       fi
    fi

    if [[ -z "${lan_p4}" ]]; then
       lxc profile device add ${profilename} eth4 nic nictype=bridged parent=lan-p4 name=eth4 vlan=${vlan} 1>/dev/null
    else
       if [[ "${lan_p4}" == "wanoe" ]]; then
           lxc profile device add ${profilename} eth4 nic nictype=bridged parent=wanoe name=eth4 vlan=${vlan} 1>/dev/null
       elif [[ "${lan_p4}" == "wan" ]]; then
           lxc profile device add ${profilename} eth4 nic nictype=bridged parent=wan name=eth4 1>/dev/null
       else
           lxc profile device add ${profilename} eth4 nic nictype=bridged parent=wanoe name=eth4 vlan=${lan_p4_vlan} 1>/dev/null
       fi
    fi

    #### # wlan
    #### lxc profile device add ${profilename} wl0 nic nictype=bridged parent=br-wlan0 name=wl0 vlan=${vlan} 1>/dev/null
    #### lxc profile device add ${profilename} wl1 nic nictype=bridged parent=br-wlan1 name=wl1 vlan=${vlan} 1>/dev/null

    # nvram
    if ! lxc storage volume show default $volumename > /dev/null 2>&1; then
        lxc storage volume create default $volumename size=4MiB 1>/dev/null
    else
        :
        #echo "Volume $volumename exists, reusing"
    fi
    lxc profile device add $containername nvram disk pool=default source=$volumename path=/data/rdkb_nvram 1>/dev/null

    ## # share
    ## lxc profile device add $containername share disk source=$M_ROOT path=/share
fi


lxc profile set ${profilename} environment.TZ $(date +%z | awk '{printf("PST8PDT,M3.2.0,M11.1.0")}')
lxc profile set ${profilename} environment.HOME /home/root

lxc profile set ${profilename} environment.CONTAINER_NAME ${containername}
lxc profile set ${profilename} environment.BNG_ID ${bng_id}
lxc profile set ${profilename} environment.SERIAL_NUMBER ${containername}
lxc profile set ${profilename} environment.STORED_MAC1 ${mac1}
lxc profile set ${profilename} environment.STORED_MAC2 ${mac2}

# disable expanded logging
lxc profile set ${profilename} environment.rssfree_logging false
lxc profile set ${profilename} environment.syscfg_logging false
lxc profile set ${profilename} environment.sysevent_logging false
lxc profile set ${profilename} environment.rbus_logging false
lxc profile set ${profilename} environment.logmaxsize "" #150000000
lxc profile set ${profilename} environment.haltrace false
lxc profile set ${profilename} environment.halbacktrace false

lxc profile set ${profilename} environment.dbg_rootfs_url $1/${mvdbgrootfstarball}
lxc profile set ${profilename} environment.dbg_rootfs_user ${USER}


if false; then
    lxc profile set ${profilename} environment.runner "" # comma separated commands
    lxc profile set ${profilename} environment.runner_delay "" # in seconds (default = 1)
    lxc profile set ${profilename} environment.runner_interval "" # in seconds (default = 1)
    lxc profile set ${profilename} environment.pcap "" #"eth0"
    lxc profile set ${profilename} environment.sniff "" #"eth0"
    lxc profile set ${profilename} environment.interfacesv4 false # true
    lxc profile set ${profilename} environment.interfacesv6 false # true
    lxc profile set ${profilename} environment.routesv4 "" # "255,254,100,200"
    lxc profile set ${profilename} environment.routesv6 "" # "255,254,100,200"
    lxc profile set ${profilename} environment.rulesv4 false #true
    lxc profile set ${profilename} environment.rulesv6 false #true
    lxc profile set ${profilename} environment.files "" #"/etc/resolv.conf"
    lxc profile set ${profilename} environment.bindmounts false
fi

lxc launch ${imagename} ${containername} -p ${profilename}
