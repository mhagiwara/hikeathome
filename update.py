# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "matplotlib==3.7.5",
#     "openai==1.59.2",
#     "opencv-python==4.8.1.78",
# ]
# ///
# get the filename of the latest video file that ends with .mkv
import glob
import json
import os
import subprocess
import sys
import datetime
from datetime import timedelta

latest_filename = list(sorted(glob.glob('data/*.mkv')))[-1]

# run analyze_video.py with that file, outputting  to stdout the result in the jsonl file that has the same filename
result_filename = latest_filename.replace('.mkv', '.jsonl')
if not os.path.exists(result_filename):
    print(f"Analyzing {latest_filename}...", file=sys.stderr)
    with open(result_filename, mode='w') as f:
        subprocess.run(['python', 'analyze_video.py', latest_filename], stdout=f)

def analyze_jsonl(filename):
    scores = []
    with open(filename) as f:
        for line in f:
            data = json.loads(line)
            scores.append(int(data['score']))
    # compute AFMAD — Average Focus Minus Average Distraction
    # average distraction is variance of the differences between consecutive focus levels
    af = sum(scores) / len(scores)
    ad = sum(abs(scores[i] - scores[i-1]) for i in range(1, len(scores))) / (len(scores) - 1)

    length = len(scores)
    total = length * (af - ad)
    return f"{total:.2f} ({af:.2f}-{ad:.2f})*{length}"



# Output README.md

scores = []
dates = []

# Embed contribution.png
print("![contribution](contribution.png)")

print("```")
start_date = datetime.date(2024, 8, 1)
# adjust to the first Monday of the month
start_date = start_date + timedelta(days=(7 - start_date.weekday()) % 7)
end_date = datetime.date.today()

current_date = start_date

while current_date <= end_date:
    datestr = current_date.strftime('%Y%m%d')

    day_scores = []
    total_day_score = 0
    for filename in sorted(glob.glob(f"data/{datestr}*.jsonl")):
        score = analyze_jsonl(filename)
        day_scores.append(str(score))
        total_day_score += float(score.split()[0])        
    
    if day_scores:
        print(f"{datestr} {'   '.join(day_scores)}")
    
    scores.append(total_day_score)
    dates.append(current_date)

    # Increment the current_date by one day
    current_date += datetime.timedelta(days=1)

print("```")


# Visualize the data in a heatmap
import numpy as np
import matplotlib.pyplot as plt
import calendar
from datetime import datetime, timedelta

# Initialize an array to hold contributions in a (weeks x 7 days) shape
weeks_in_year = (len(dates) + start_date.weekday()) // 7 + 1
contribution_grid = np.zeros((7, weeks_in_year))  # 7 rows for each day of the week

# Fill the contribution grid
for i, date in enumerate(dates):
    week = (date - start_date).days // 7
    day_of_week = date.weekday()
    contribution_grid[day_of_week, week] = scores[i]

# Calculate the Mondays for each week
week_start_dates = [start_date + timedelta(weeks=i) for i in range(weeks_in_year)]
week_labels = [date.strftime('%Y-%m-%d') for date in week_start_dates]

# Plotting the contribution heatmap
fig, ax = plt.subplots(figsize=(15, 5))
heatmap = ax.imshow(contribution_grid, cmap='Greens', interpolation='nearest')

# Customize the ticks (set weekdays and weeks)
ax.set_yticks(np.arange(7))
ax.set_yticklabels([calendar.day_name[i] for i in range(7)])

# Set week labels as the Monday dates
ax.set_xticks(np.arange(weeks_in_year))
ax.set_xticklabels(week_labels, rotation=45, ha='right')

# Add colorbar to show the scale
plt.colorbar(heatmap, ax=ax)

# Save to contribution.png
plt.title('Github-like Contribution Heatmap')
plt.savefig('contribution.png', bbox_inches='tight')
