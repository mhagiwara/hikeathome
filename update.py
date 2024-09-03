# get the filename of the latest video file that ends with .mkv
import glob
import json
import os
import subprocess
import sys
import datetime

latest_filename = list(sorted(glob.glob('*.mkv')))[-1]

# run analyze_video.py with that file, outputting  to stdout the result in the jsonl file that has the same filename
result_filename = latest_filename.replace('.mkv', '.jsonl')
if not os.path.exists(result_filename):
    print(f"Analyzing {latest_filename}...", file=sys.stderr)
    with open(result_filename, mode='w') as f:
        subprocess.run(['python', 'analyze_video.py', latest_filename], stdout=f)

def analyze_jsonl(filename):
    total_score = 0
    with open(filename) as f:
        for line in f:
            data = json.loads(line)
            total_score += int(data['score'])
    return total_score


# Output README.md

print("```")
start_date = datetime.date(2024, 8, 1)
end_date = datetime.date(2024, 9, 30)

current_date = start_date
while current_date <= end_date:
    datestr = current_date.strftime('%Y%m%d')

    scores = []
    for filename in sorted(glob.glob(f"{datestr}*.jsonl")):
        score = analyze_jsonl(filename)
        scores.append(str(score))
    
    if scores:
        print(f"{datestr} {' '.join(scores)}")
    
    # Increment the current_date by one day
    current_date += datetime.timedelta(days=1)

print("```")
