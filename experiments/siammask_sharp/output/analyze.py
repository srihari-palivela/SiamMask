import json
import sys
import os.path


x_left_tank_zones = [(0,506),(506,632),(632,840)]
x_right_tank_zones = [(830,964),(964,1090),(1090,1500)]

try:
  json_file = sys.argv[1]
  video_id = sys.argv[2]
  tank = sys.argv[3]
  if tank == 'left':
    x_zones = x_left_tank_zones
  elif tank == 'right':
    x_zones = x_right_tank_zones
  else:
    print("Invalid tank : ",tank)
    sys.exit(1)
except :
  print("Invalid command \nanalyze.py <json_file> <video_id> <tank>[left|right]")
  sys.exit(1)

y_zones = [(0,580),(580,860),(860,1200)]

data = {}
with open(json_file,"r") as data_file:
  data = json.load(data_file)


# start = data.keys()[0]
total_still = 0
total_mobile = 0
time_in_lz = 0
time_in_mz = 0
time_in_uz = 0
transistion_lm = 0
transistion_mu = 0
transistion_um = 0
transistion_ml = 0
first_lm = 0
first_mu = 0


prev_value = []
prev_y_zone = -1
prev_x_zone = -1
frames_in_x_zone = [0,0,0]
frames_in_y_zone = [0,0,0]

def get_x_zone(x_cord):
  for i,(ll,ul) in enumerate(x_zones):
    print(x_cord, i, ll,ul)
    if x_cord >=ll and x_cord <= ul:
      return i

def get_y_zone(y_cord):
  for i,(ll,ul) in enumerate(y_zones):
    if y_cord >=ll and y_cord <=ul:
      return i

def get_x_y_zones(x_cord, y_cord):
  x_zone = get_x_zone(x_cord)
  y_zone = get_y_zone(y_cord)
  return x_zone,y_zone

def update_time_in_zone(x_zone, y_zone):
  frames_in_x_zone[x_zone] += 1
  frames_in_y_zone[y_zone] += 1

def update_transitions(prev_y_zone, y_zone, frame_num):
  global transistion_um, transistion_ml, transistion_lm, transistion_mu, first_lm, first_mu
  if prev_y_zone == 0 and y_zone == 1:
    transistion_um+=1
  elif prev_y_zone == 1 and y_zone == 2:
    transistion_ml+=1
  elif prev_y_zone == 2 and y_zone == 1:
    transistion_lm+=1
    if not first_lm:
      first_lm = frame_num
  elif prev_y_zone == 1 and y_zone == 0:
    transistion_mu+=1
    if not first_mu:
      first_mu = frame_num

def is_still(prev_value, value):
  global total_still, total_mobile
  abs_change = abs(prev_value[0]-value[0]) + abs(prev_value[1]-value[1])
  if abs_change < 2:
    total_still +=1
  else:
    total_mobile+=1

for i,(key,value) in enumerate(data.items()):
  print(key)
  # init frame
  if not prev_value:
    prev_value = value
    prev_x_zone = get_x_zone(value[0])
    prev_y_zone = get_y_zone(value[1])
    update_time_in_zone(prev_x_zone, prev_y_zone)
    continue
  # from second frame
  else:
    x_zone, y_zone = get_x_y_zones(value[0], value[1])
    update_time_in_zone(x_zone, y_zone)
    update_transitions(prev_y_zone, y_zone, i)
    is_still(prev_value, value)
    prev_x_zone = x_zone
    prev_y_zone = y_zone
    prev_value = value
  
  # frames_in_x_zone,
total_frames = len(data.items())
total_time = round(total_frames/24, 3)
time_total_still = round(total_still/24, 3)
time_total_mobile = round(total_mobile/24, 3)
time_lower_zone = round(frames_in_y_zone[2]/24, 3)
time_middle_zone = round(frames_in_y_zone[1]/24, 3)
time_upper_zone = round(frames_in_y_zone[0]/24, 3)
time_first_lm = round(first_lm/24, 3)
time_first_mu = round(first_mu/24, 3)
print(
total_time,
total_frames,
time_total_still,
time_total_mobile,
time_lower_zone, # lower zone
time_middle_zone, # middle zone
time_upper_zone, # upper zone
first_lm,
first_mu,
transistion_lm,
transistion_mu ,
transistion_um ,
transistion_ml)

if not os.path.isfile("result.csv"):
  with open("result.csv","w") as res_file:
    res_file.write("Video id,Tank,Total time,Total Frames,Total time Still,Total time mobile,Time in LZ,Time in MZ,Time in UZ,Latency to first LM Transit,Latency to first MU Transit,Transitions LM,Transitions MU,Transitions UM,Transitions ML\n")

with open("result.csv","a") as res_file:
  res_file.write(f"{video_id},{tank},{total_time},{total_frames},{time_total_still},{time_total_mobile},{time_lower_zone},{time_middle_zone},{time_upper_zone},{time_first_lm},{time_first_mu},{transistion_lm},{transistion_mu},{transistion_um},{transistion_ml}\n")

