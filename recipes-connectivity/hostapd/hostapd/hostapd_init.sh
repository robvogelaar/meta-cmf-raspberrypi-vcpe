#!/bin/sh

# Get actual PHY numbers instead of assuming sequential numbering
PHY_LIST=`iw dev | grep "phy#" | sed 's/phy#//' | sort -n`
PHY_COUNT=`echo "$PHY_LIST" | wc -w`

n_d_cc=0
NETGEAR_DONGLE=0
TP_LINK_OR_INBUILT=0

for phy_num in $PHY_LIST; do
    # Check the actual iw phy info output format
    VALID_INTERFACE_COMBINATIONS_COUNT=`iw phy$phy_num info | grep -E "(managed|AP|mesh)" | wc -l`
    echo "valid phy$phy_num : $VALID_INTERFACE_COMBINATIONS_COUNT"
    
    if [ $VALID_INTERFACE_COMBINATIONS_COUNT -eq 3 ]; then
        NETGEAR_DONGLE=1
        n_d_cc=$((n_d_cc+1))  
    else
        TP_LINK_OR_INBUILT=1
    fi
done

if [ $NETGEAR_DONGLE -eq 1 ]; then
    echo "Netgear Dongle Scenario $n_d_cc"
    sh /usr/hostapd/hostapd_opensync.sh $n_d_cc
else
    echo "TP-link/In-built scenario"
    sh /usr/hostapd/hostapd_start.sh    
fi
