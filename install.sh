#!/bin/bash
#get script path

scriptfile=$(readlink -f $0)
installpath=`dirname $scriptfile`

sudo apt-get update
sudo apt-get install omxplayer libjpeg8 imagemagick -y

cd $installpath

sudo rm -rf /opt/retropie/configs/all/PieMarquee2/
mkdir /opt/retropie/configs/all/PieMarquee2/
cp -f -r $installpath/PieMarquee2 /opt/retropie/configs/all/

chmod 755 /opt/retropie/configs/all/PieMarquee2/omxiv-marquee

sed -i '/PieMarquee2.py/d' /opt/retropie/configs/all/autostart.sh
sed -i '1i\\/usr/bin/python /opt/retropie/configs/all/PieMarquee2/PieMarquee2.py > /dev/null 2>&1 &' /opt/retropie/configs/all/autostart.sh

echo
echo "Setup Completed. Reboot in 3 Seconds."
sleep 3
sudo reboot
