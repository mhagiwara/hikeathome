import glob
import cv2
import re

total_miles = 0
# get all the mkv files in the same directory
for filepath in glob.glob('*.mkv'):
    print(filepath)
    cap = cv2.VideoCapture(filepath)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration_in_seconds = frame_count / fps
    duration_in_hours = duration_in_seconds / 3600

    # extract the speed info (such as ".1_8mph.") from the filename
    speed = re.search(r'\.(\d+_\d+)mph\.', filepath).group(1)
    speed = float(speed.replace('_', '.'))
    print(duration_in_hours, speed)

    # add the distance traveled to the total
    total_miles += duration_in_hours * speed

print('Total miles traveled:', total_miles)
