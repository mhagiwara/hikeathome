import argparse
import base64
import json
import os
import shutil
import sys

import cv2

from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
prompt = """
This is a screen capture of a laptop screen with an image of the laptop's user (who is a research scientist) at the lower right corner.
Based on the content of the screen and the image, how concentrated at his research work is the person?
Please answer on a scale of 1 (least concentrated) to 10 (most concentrated).
Just answer with a number.
"""

def call_openai_api(image_path):
    # read image and convert to base64
    with open(image_path, 'rb') as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                prompt,
                {"image": base64_image},
            ],
        },
    ]
    params = {
        "model": "gpt-4o-mini",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 200,
    }

    result = client.chat.completions.create(**params)
    return result.choices[0].message.content

parser = argparse.ArgumentParser(description='Analyze a video file')
parser.add_argument('filename', help='the video file to analyze')
parser.add_argument('--keep-images', action='store_true', help='keep the images after processing')
args = parser.parse_args()

# get the filename from the command line
filename = args.filename
# create a directory to store the images
os.makedirs(filename + '_images', exist_ok=True)
# open the video file
cap = cv2.VideoCapture(filename)
# get the frame count
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# get the frames per second
fps = cap.get(cv2.CAP_PROP_FPS)
# get the duration in seconds
duration_in_seconds = frame_count / fps
# loop through all the frames
for i in range(frame_count):
    # read the frame
    ret, frame = cap.read()
    if not ret:
        break
    # save the frame as an image every minute
    if i % int(fps * 60) == 0:
        print(f'Processing frame {i}', file=sys.stderr)
        image_path = f'{filename}_images/{i}.png'
        cv2.imwrite(image_path, frame)
        score = call_openai_api(image_path)
        print(json.dumps({"frame": i, "score": score}))

# delete the directory
if not args.keep_images:
    shutil.rmtree(filename + '_images')
