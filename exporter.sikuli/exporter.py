import sys
import os

def clickifexists(x):
    if exists(x):
        click(x)
        return True
    return False

def waitandclick(x):
    wait(x)
    click(x)

if len(sys.argv) < 2:
    print("Usage: exporter <outputpath> [res:4K|6K|8K] [rate:low|high|recommended]")
    os.exit(1)

outputpath = sys.argv[1]
output_dir, filename = os.path.split(outputpath)
filename = filename.replace(".mp4", "")

ress = {'4K':("resolution_4K_option.png", "resolution_4K_set.png"),
        '6K':("resolution_6K_option.png", "resolution_6K_set.png"),
        '8K':("resolution_8K_option.png", "resolution_8K_set.png")}
res = '8K'

if len(sys.argv) > 2:
   if sys.argv[2] in ress:
       res = sys.argv[2]
   else:
        print("Resolution "+sys.argv[2]+" is not supported")
        os.exit(2)

rates = {'low':("bitrate_low_option.png", "bitrate_low_set.png"),
         'high':("bitrate_high_option.png","bitrate_high_set.png"),
         'recommended':("bitrate_recommended_option.png","bitrate_recommended_set.png")}
rate = 'recommended'
if len(sys.argv) > 3:
   if sys.argv[3] in rates:
       rate = sys.argv[3]
   else:
        print("Bitrate "+sys.argv[3]+" is not supported")
        os.exit(2)

wait = 2.5
if len(sys.argv) > 4:
    try:
        wait = max(float(sys.argv[4]), 0)
    except ValueError:
        print("Sleep time "+sys.argv[4]+" is not supported")
        os.exit(3)

sleep(wait)

click("create_button.png")

sleep(wait)
if exists("already_open_warning.png"):
    click("create_project_button.png")
    sleep(wait)

sleep(wait)
dragDrop(Pattern("import_button.png").targetOffset(50, 75),"timeline_zone.png")

sleep(wait)
if exists("free_view.png"):
    sleep(wait)
    click("free_view.png")
    sleep(wait)
    click("direction_lock.png")

sleep(wait*2)
click("export_button.png")
sleep(wait)
click("panoramic_video.png")
sleep(wait)
click("file_name.png")

doubleClick(getLastMatch())
type(Key.BACKSPACE)
paste(filename)

sleep(wait)

click("change_folder_button.png")
sleep(wait)
click(Pattern("path_anchor.png").targetOffset(-25, 0))
sleep(wait)
type(Key.BACKSPACE)
paste(output_dir)
type(Key.ENTER)
click("select_folder_button.png")

sleep(wait)
while exists(ress[res][1]) is None:
    click(Pattern("resolution_label.png").targetOffset(100, 0))
    sleep(wait)
    click(ress[res][0])
    sleep(wait)

click(Pattern("framerate_label.png").targetOffset(100, 0))
sleep(wait)
click("framerate_30_option.png")
sleep(wait)

while exists(rates[rate][1]) is None:
    click(Pattern("bitrate_label.png").targetOffset(100, 0))
    sleep(wait)
    click(rates[rate][0])
    sleep(wait)

click("export_submit_button.png")
sleep(wait)

click("export_task_button.png")
sleep(wait)

while exists("tab_anchor.png") is not None:
    try:
        click(Pattern("tab_anchor.png").targetOffset(-10, 0))
        sleep(wait)
    except:
        break
