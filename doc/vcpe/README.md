# Build vcpe (rpi) container image

```text
repo init -u https://code.rdkcentral.com/r/rdkcmf/manifests -m rdkb-nosrc.xml -b rdkb-2025q1-kirkstone  

repo sync --no-clone-bundle --no-tags

git clone https://github.com/robvogelaar/meta-cmf-raspberrypi-vcpe.git

cp meta-cmf-raspberrypi-vcpe/conf/machine/qemux86broadband.conf.sample meta-cmf-raspberrypi/conf/machine/qemux86broadband.conf

source meta-cmf-raspberrypi/setup-environment [1]

bitbake-layers add-layer ../meta-cmf-raspberrypi-vcpe

bitbake rdk-generic-broadband-image
```
