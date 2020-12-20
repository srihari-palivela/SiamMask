import cv2
vidcap = cv2.VideoCapture('00101.MTS')
fps = vidcap.get(cv2.CAP_PROP_FPS)
print("FPS : ",vidcap.get(cv2.CAP_PROP_FPS))
# timestamps = [vidcap.get(cv2.CAP_PROP_POS_MSEC)]

success,image = vidcap.read()
count = 0
frame_step = 1/fps
while success:
  frame_timestamp = "{sec}.{frame_number}".format(sec=str(int(count/fps)).zfill(5), frame_number= str(int(count%fps)).zfill(5))
  cv2.imwrite("frames/%s.jpg" % str(frame_timestamp), image)     # save frame as JPEG file
  success,image = vidcap.read()
  # print('Read a new frame: ', success)
  count += 1