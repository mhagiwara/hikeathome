from datetime import datetime
import subprocess
import sys
import time

mode = sys.argv[1]
assert mode in {'ext', 'ext-zero', 'int', 'int-zero'}

now = datetime.now()
timestamp = now.strftime('%Y%m%d-%H%M%S')

input1_id = '1' if mode.startswith('ext') else '0'
input1_options = ['-f', 'avfoundation', '-pix_fmt', 'yuyv422', '-r', '30', '-s', '1920x1080', '-i', input1_id]

if mode.endswith('zero'):
    input2_options = ['-f', 'rawvideo', '-pix_fmt', 'yuyv422', '-r', '30', '-s', '1920x1080', '-i', '/dev/zero']
else:
    input2_id = '2' if mode.startswith('ext') else '1'
    input2_options = ['-f', 'avfoundation', '-pix_fmt', 'yuyv422', '-r', '30', '-s', '1920x1200', '-i', input2_id]

filter_options = ['-filter_complex', '[0]scale=160:90 [overlay]; [1]scale=640:400 [base]; [base][overlay]  overlay=main_w - overlay_w:main_h - overlay_h[out]; [out]fps=30']

p = subprocess.Popen(['ffmpeg', '-probesize', '50000000'] + input1_options + input2_options + filter_options + [timestamp + '.mkv'])

while True:
    time.sleep(1.)
