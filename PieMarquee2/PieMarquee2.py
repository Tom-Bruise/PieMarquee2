#!/usr/bin/python3

import os
from subprocess import *
from time import *
import xml.etree.ElementTree as ET

# Config bits
INTRO = "/home/pi/PieMarquee2/intro.mp4"
VIEWER = "/opt/retropie/configs/all/PieMarquee2/omxiv-marquee /tmp/marquee.txt -f -b -d 7 -t 5 -T blend --duration 900 --aspect fill > /dev/null 2>&1 &"
PRIORITIZE_PIEMARQUEE_ASSETS = False
SLEEP_INTERVAL = 1 # how often the maibn cycle is called, in seconds
BURN_IN_PREVENTION_INTERVAL = 90 # When to display an alternate image to prevent burn-in, in seconds. 0 to disable
BURN_IN_PREVENTION_DURATION = 20 # For how long to display the alternate image, in seconds
# End of config bits

burn_in_secs_count = 0
burn_in_prevention_active = False
arcade = ['arcade', 'fba', 'mame-advmame', 'mame-libretro', 'mame-mame4all']

def run_cmd(cmd):
# runs whatever in the cmd variable
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode()

def kill_proc(name):
    ps_grep = run_cmd("ps -aux | grep " + name + "| grep -v 'grep'")
    if len(ps_grep) > 1: 
        os.system("killall " + name)
        
def is_running(pname):
    pid_of = run_cmd("pidof " + pname)
    if len(pid_of) > 1:
        return True
    else:
        return False

def get_publisher(romname):
    filename = romname+".zip"
    publisher = ""
    for item in root:
        if filename in item.findtext('path'):
            publisher = item.findtext('publisher')
            break
    if publisher == "":
        return ""
    words = publisher.split()
    return words[0].lower()

def get_piemarquee_match_for_romnames(romnames):
    # Check if there is a Piemarquee marquee file that contains the rom name.
    # This is to display the right marquue for different versions of the game
    # (e.g. US, JAP, bootlegs, hacks etc.)
    for f in os.listdir("/home/pi/PieMarquee2/marquee/arcade/"):
        for name in romnames:
            if name in f:
                yield f
                break

def update_burn_in_vars(): 
    if BURN_IN_PREVENTION_INTERVAL == 0:
        return
    
    global burn_in_secs_count,  burn_in_prevention_active
    burn_in_secs_count += SLEEP_INTERVAL

    if burn_in_prevention_active == False:
        if burn_in_secs_count == BURN_IN_PREVENTION_INTERVAL:
            set_burn_in_prevention(True)
    else:
        if burn_in_secs_count == BURN_IN_PREVENTION_DURATION:
            set_burn_in_prevention(False)
    
def set_burn_in_prevention(active):
     burn_in_prevention_active = active
     burn_in_secs_count = 0
    
if os.path.isfile(INTRO) == True:
    run_cmd("omxplayer --display 7 " + INTRO)

doc = ET.parse("/opt/retropie/configs/all/PieMarquee2/gamelist_short.xml")
root = doc.getroot()

if os.path.isfile("/home/pi/PieMarquee2/marquee/system/maintitle.mp4") == True:
    os.system("omxplayer --loop --no-osd --display 7 /home/pi/PieMarquee2/marquee/system/maintitle.mp4 &")
else:
    os.system("echo '/home/pi/PieMarquee2/marquee/system/maintitle.png' > /tmp/marquee.txt")
    os.system(VIEWER)

cur_imgname = "system/maintitle"

while True:
    update_burn_in_vars()

    ingame = ""
    romname = ""
    sysname = ""
    pubpath = ""
    instpath = ""
    imgpath = ""
    ps_grep = run_cmd("ps -aux | grep emulators | grep -v 'grep'")

    if is_running("retroarch"): # Ingame
        ingame="*"
        set_burn_in_prevention(False)

        if len(ps_grep) == 0:
            continue

        words = ps_grep.split()
        if 'advmame' in ps_grep:
            sysname = "arcade"
            romname = words[-1]
        else:
            pid = words[1]
            if os.path.isfile("/proc/"+pid+"/cmdline") == False:
                continue
            path = run_cmd("strings -n 1 /proc/"+pid+"/cmdline | grep roms")
            path = path.replace('/home/pi/RetroPie/roms/','')
            if len(path.replace('"','').split("/")) < 2:
                continue
            sysname = path.replace('"','').split("/")[0]

            romname = path.replace('"','').split("/")[-1].rsplit('.', 1)[0]

            # Remove .zip extension from romname if it exists
            # (Needed for arcade games)
            if romname.endswith(".zip"):
                romname = romname.replace(".zip","")

            if PRIORITIZE_PIEMARQUEE_ASSETS == True:
                if sysname in arcade:
                    sysname = "arcade"

                # If it's an arcade game, look for a match in the marquee files suppiled with PieMarquee2.
                # Many of them seem to have been generated procedurally (possibly with Skyscraper), but there
                # are some original scans as well (e.g. Golden Axe, Metal Slug etc.)

                # Just use the first matching file
                matching_marquees = list(get_piemarquee_match_for_romnames([romname]))
                if len(matching_marquees) > 0:
                    romname = matching_marquees[0].split('.')[0]
    else:
        sysname = "system"
         # Display alternate maintitle logo as alternate imaghe to prevent burn-in
        romname = "maintitle2" if burn_in_prevention_active else "maintitle"

    if os.path.isfile("/home/pi/PieMarquee2/marquee/" + sysname  + "/" + romname  + ".png") == True:
        imgname = sysname + "/" + romname
        if ingame == "*":
            if burn_in_prevention_active:
                # Display maintitle logo as alternate imaghe to prevent burn-in
                imgname = "system/maintitle"

            ## Disable publisher and instructions as handled in original script
            ## publisher = get_publisher(romname)
            ##if os.path.isfile("/home/pi/PieMarquee2/marquee/publisher/" + publisher + ".png") == True:
            ##    pubpath = "/home/pi/PieMarquee2/marquee/publisher/" + publisher + ".png"
            # if os.path.isfile("/home/pi/PieMarquee2/marquee/instruction/" + romname + ".png") == True:
            #     instpath = "/home/pi/PieMarquee2/marquee/instruction/" + romname + ".png"
    elif os.path.isfile("/home/pi/PieMarquee2/marquee/system/" + sysname + ".png") == True:
        imgname = "system/" + sysname
    else:
        imgname = "system/maintitle"

    if imgname+ingame != cur_imgname: # change marquee images
        ps_grep = run_cmd("ps -aux | grep 'maintitle.mp4' | grep -v 'grep'")
        if len(ps_grep) > 1 :
            words = ps_grep.split()
            pid = words[1]
            os.system("ps -aux | grep maintitle.mp4 | awk '{print $2}'| xargs kill -9")
        if imgname == "system/maintitle" and os.path.isfile("/home/pi/PieMarquee2/marquee/system/maintitle.mp4") == True:
            kill_proc("omxiv-marquee")
            os.system("omxplayer --loop --no-osd --display 7 /home/pi/PieMarquee2/marquee/system/maintitle.mp4 &")
            cur_imgname = imgname+ingame
        else:
            '''
            f = open("/tmp/marquee.txt", "w")
            if pubpath != "":
                f.write(pubpath+"\n")
            f.write("/home/pi/PieMarquee2/marquee/" + imgname + ".png")
            if instpath != "":
                f.write("\n"+instpath)
            f.close()
            '''
            if os.path.isfile("/home/pi/PieMarquee2/marquee/custom/" + romname  + ".txt") == True and ingame == "*":
                os.system("cp /home/pi/PieMarquee2/marquee/custom/" + romname  + ".txt /tmp/marquee.txt")
            else:
                imgpath = "/home/pi/PieMarquee2/marquee/" + imgname + ".png"
                if ingame == "*":
                    if pubpath != "":
                        imgpath = pubpath+"\n"+imgpath
                    if instpath != "":
                        imgpath = imgpath+"\n"+instpath
                os.system('echo "' + imgpath + '" > /tmp/marquee.txt')
            sleep(0.2) 
            if is_running("omxiv-marquee") == False: # if omxiv failed, execute again
                os.system("clear > /dev/tty1")
                os.system('echo "' + imgpath + '" > /tmp/marquee.txt')
                os.system(VIEWER)
            cur_imgname = imgname+ingame

    sleep(SLEEP_INTERVAL)

