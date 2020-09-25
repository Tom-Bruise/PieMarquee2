import sys, os
from subprocess import *

def run_cmd(cmd):
# runs whatever in the cmd variable
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output
  
source_path = "/home/pi/RetroPie/roms/"+sys.argv[1]+"/marquee/"
snapshot_parh = "/home/pi/RetroPie/roms/"+sys.argv[1]+"/snap/"
dest_path = sys.argv[1]
resize = sys.argv[2]
resize_method = sys.argv[3]
bg_color = sys.argv[4]
bg_trans = str(100-int(sys.argv[5])*100)
marquee_size = sys.argv[6]

run_cmd("convert -size " + resize + "xc:" + bg_color + 
    " -matte -channel A +level 0," + bg_trans + "% +channel ./bg.png")

if source_path.endswith("/") == False:
    source_path = source_path+"/"
if dest_path.endswith("/") == False:
    dest_path = dest_path+"/"

if os.path.isdir(source_path) == False:
    print "source path is not valid"
else:
    if os.path.isdir(os.getcwd()+"/"+dest_path) == False:
        os.mkdir(os.getcwd()+"/"+dest_path)
    file_list = os.listdir(source_path)
    file_list.sort()
    for f in file_list:
        if ".png" in f:
            run_cmd('convert "' + source_path + f + '" -background black -alpha remove -resize ' + resize + ' "./' + dest_path + f + '"')
            print 'convert "' + source_path + f + '" -background black -alpha remove -resize ' + resize + ' "./' + dest_path + f + '"'
        elif ".jpg" in f:
            run_cmd('convert "' + source_path + f + '" -resize ' + resize + ' "./' + dest_path + f.replace("jpg","png") + '"')
            print 'convert "' + source_path + f + '" -resize ' + resize + ' "./' + dest_path + f.replace("jpg","png") + '"'

convert kof97-snap.png -resize 1280x400\! bg.png -composite kof97.png
convert kof97-snap.png -resize 1280x400^ bg.png -composite kof97.png
convert kof97-logo.png -resize 1280x400 -resize 80% logo.png 
convert logo.png -background black -shadow 80x3+5+5 logo.png -composite shadow.png
composite -gravity center shadow.png kof97.png kof97.png 
