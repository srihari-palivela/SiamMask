import cv2
import sys
import shutil
import os

try:
    filename = sys.argv[1]
    fname, ext = filename.split(".")
except:
    exit(1)

dirpath = os.path.isdir(fname)
if os.path.exists(dirpath) and os.path.isdir(dirpath):
    shutil.rmtree(dirpath)
    os.makedirs(os.path.dir_name(dirpath))
        
vidcap = cv2.VideoCapture(filename)
fps = vidcap.get(cv2.CAP_PROP_FPS)
print("FPS : ",vidcap.get(cv2.CAP_PROP_FPS))
# timestamps = [vidcap.get(cv2.CAP_PROP_POS_MSEC)]

success,image = vidcap.read()
count = 0
frame_step = 1/fps
while success:
  frame_timestamp = "{sec}.{frame_number}".format(sec=str(int(count/fps)).zfill(5), frame_number= str(int(count%fps)).zfill(5))
  cv2.imwrite("{fname}/%s.jpg" % str(frame_timestamp), image)     # save frame as JPEG file
  success,image = vidcap.read()
  # print('Read a new frame: ', success)
  count += 1

