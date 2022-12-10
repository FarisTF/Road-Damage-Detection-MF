#   ====================================== SLOW DOWN VIDEO ======================================
def slow_down_video(input_path, output_folder):
    import os
    import cv2
    video = cv2.VideoCapture(input_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps

    print('fps = ' + str(fps))
    print('number of frames = ' + str(frame_count))
    print('duration (S) = ' + str(duration))
    minutes = int(duration/60)
    seconds = duration%60
    print('duration (M:S) = ' + str(minutes) + ':' + str(seconds))

    frame_width = int(video.get(3))
    frame_height = int(video.get(4))
      
    size = (frame_width, frame_height)

    # Ngebuat folder result kalo belom ada
    if not os.path.exists("result"):
        os.makedirs("result")

    folder_path = "result/"+output_folder
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    slow_folder_path = "result/"+output_folder+"/slowed"
    if not os.path.exists(slow_folder_path):
        os.makedirs(slow_folder_path)

    # Ngebuat pathnya 
    slow_output_path = "result/"+ output_folder + "/slowed/"+ output_folder + "_slowed.mp4"
    
    # Below VideoWriter object will create a frame of above defined 
    # The output is stored in 'filename.avi' file.
    result = cv2.VideoWriter(slow_output_path, 
                            cv2.VideoWriter_fourcc(*'mp4v'),
                            30, size) # Untuk ngatur FPS

    # Untuk ngehitung frame yang asli (soalnya video yang dari gopro langsung ada yang di tengah tengah ngereturn frame ghoib)
    x=0
    while(x<frame_count):
        ret, frame = video.read()
        print(str(x) + str(ret))
      
        if ret == True: 
            result.write(frame)
            x+=1
      
        # Break the loop
    print ("==========UDAH BERES================")
    for i in range(60):
      ret, frame = video.read()
      print(str(x) + str(ret))
      x+=1

    video.release()
    result.release()
    cv2.destroyAllWindows()
      
    print("Slowed video sudah selesai, silahkan cek di: " + slow_output_path)
    return slow_output_path




#   ====================================== REGION OF INTEREST ======================================
def roi(frame, bbox):
    import cv2
    start = (0, 1080)
    end = (1920, 648)
    r = cv2.rectangle(frame, start, end, (0, 0, 0), 0)
    rect_img = frame[648:1080, 0:1920]
    y_middle= (bbox[3]-bbox[1])/2 + bbox[1]
#     x= (xmax - xmin)/2 + xmin
    if (y_middle < 648):
        return False, r
    else:
        return True, r




#   ====================================== COUNTING ======================================
def counting(set_of_id):
  return len(set_of_id)




#   ====================================== BOUNDING BOX ======================================
def boundingBox(track, colors, frame, bbox, class_name):
  import numpy as np
  import cv2
  color = colors[int(track.track_id) % len(colors)]
  color = [i * 255 for i in color]
  # Bounding box utama
  cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 2)

  # Untuk kotak tempat textnya
  cv2.rectangle(frame, (int(bbox[0]), int(bbox[1]-30)), (int(bbox[0])+(len(class_name)+len(str(track.track_id)))*17, int(bbox[1])), color, -1)

  # Ya untuk text
  cv2.putText(frame, class_name + "-" + str(track.track_id),(int(bbox[0]), int(bbox[1]-10)),0, 0.75, (255,255,255),2)
  return frame




#   ====================================== MEASURE AREA ======================================
def measure_bbox(xmin, ymin, xmax, ymax):

  #ini kalo 0,0 di kiri atas
  temp = ymin
  ymin = 1080 - ymax
  ymax = 1080 - temp
  
  # https://pyimagesearch.com/2016/03/28/measuring-size-of-objects-in-an-image-with-opencv/
  # https://stackabuse.com/3d-object-detection-3d-bounding-boxes-in-python-with-mediapipe-objectron/
  # kalo ini pake cara "berapa panjang dan jauh kamera memandang"
  # dengan konsep trapesium terbalik

  #       A_________________________________B  "ROI (432 px)" measured 3192, 774194 cm
  #        \                               /
  #         \                             / 
  #          \                           /
  #          E\_________hole____________/F
  #            \                       /
  #             \_____________________/       "Camera Position (0px)" measured 480cm 
  #             D                     C       The height of this trapesium is the distance from the camera to ROI, measured 663,65217 cm

  # By get EF length, we can get the scale of 1 px to real size
  # EF = ((DCxAE) + (ABxDE))/(AE + DE)

  #       A________H        DH = 1470 (432 pixel)
  #        \       |        AH = (AB-DC)/2 
  #         \      |           = 1356 cm
  #          \     |        by phytagoras theorem we get AD, 1509 cm
  #           \    |          
  #           E\___|G        
  #             \  |                    
  #              \ |
  #               D

  # DH, CD, Lebar Jalan perlu dicek lagi

  #Known
  AB = 1200
  CD = 315
  AD = 442.522074
  ROI_px = 432 
  video_width = 1920
  video_height = 1080

  x_hole_px = xmax-xmin
  y_hole_px = ymax-ymin

  
  #Ask
  #EF -> real size of x_hole
  
  DE = (ymin/ROI_px)*AD
  AE = AD-DE
  EF = ((CD*AE)+(AB*DE))/(AE+DE)
  # print(EF)

  #lebar sebenarnya atau x_hole
  x_hole = EF*(x_hole_px/video_width)

  #lalu bagaimana dengan y_hole?
  #konsep percepatan tapi kecepatannya adalah panjang jalan dan waktunya adalah pixel, makin kecil pixel, makin besar percepatan
  # variabel penentu : jarak sebenarnya = d
  #                    tinggi pixel = t
  #                    kecepatan (V) = d/t
  #                    percepatan (a) = d/t^2 
  # a = 424cm/(276^2)px
  # Xt (jarak sebenarnya ditempuh dalam t pixel) = X0 (jarak awal ketika 0 pixel) + Vo (kecepatan saat t pixel) . t + 1/2 (a [percepatan] . t^2)                 
  # y_hole (jarak sebenarnya dari ymin ke ymax) = Xymax - Xymin
  # Xymax = Vymax .t_ymax + 1/2 (a).t_ymax^2
  # Xymin = Vymin .t_ymin + 1/2 (a).t_ymin^2
  # Vymax = v0 + a.t
  #      = (424/276^2).t_ymax
  # Vymin = v0 + a.t
  #      = (424/276^2).t_ymin 
  # y_hole = (Vymax .t_ymax + 1/2 (a).t_ymax^2)-(Vymin .t_ymin + 1/2 (a).t_ymin^2)
  #        = ((424/276^2).t_ymax .t_ymax + 1/2 (a).t_ymax^2)-((424/276^2).t_ymin .t_ymin + 1/2 (a).t_ymin^2)

  a = 443/(432**2)
  Vymax = (442/(432**2))*ymax
  Vymin = (442/(432**2))*ymin
  Xymax = (Vymax*ymax) + (0.5)*(a*(ymax)**2)
  Xymin = (Vymin*ymin) + (0.5)*(a*(ymin)**2)

  print("ymax, ymin, xmax, xmin, x_hole_px, y_hole_px : ", ymax, ymin, xmax, xmin, x_hole_px, y_hole_px)
  y_hole = Xymax-Xymin

  return (x_hole*y_hole, x_hole, y_hole)




#   ====================================== SCREENSHOOT ======================================
def screenshot(frame, detection_id, folder_path, detect_what):
  import cv2, os
  # start helper function
  if not os.path.isdir(folder_path + "/ss_"+detect_what):
   os.makedirs(folder_path + "/ss_"+ detect_what)
  path_ss = folder_path + "/ss_"+ detect_what + "/" + str(detection_id) + ".png"
  full_color = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
  cv2.imwrite(path_ss, full_color)
  return path_ss




#   ====================================== TIMESTAMP ======================================
def timestamps(vid):
  import datetime
  import cv2
  cap = vid
  ms = cap.get(cv2.CAP_PROP_POS_MSEC)
  print("Milisecond: "+str(ms))
  bentuk_dt = datetime.datetime.fromtimestamp(ms/1000.0, datetime.timezone.utc)
  bentuk_str = bentuk_dt.strftime('%-H:%M:%S')
  print(bentuk_str)
  print("Timestamp: "+ bentuk_str)
  return(bentuk_str)




#   ====================================== EVALUATION ======================================
def evaluation(path_to_csv):
  import csv
  results = []
  tp = 0
  tn = 0
  fp = 0
  fn = 0
  with open(path_to_csv) as csvfile:
      reader = csv.reader(csvfile) # change contents to floats
      next(reader, None)
      for row in reader:
        if (row[1] == "pothole" and row[2] == "pothole"):
          tp = tp +1
        elif (row[1] == "none" and row[2] == "none"):
          tn = tn +1
        elif (row[1] == "none" and row[2] == "pothole"):
          fp = fp + 1
        else:
          fn = fn + 1

  print("TP:",tp,"    TN:",tn,"    FP:",fp,"    FN:",fn)
  accuracy=round((tp+tn)/(tp+tn+fp+fn),3)
  precision=round(tp/(tp+fp),3) 
  recall=round(tp/(tp+fn),3)
  f1= round(2*((precision*recall)/(precision+recall)),3)
  print("Accuracy:",accuracy,"\t Precision:",precision,"\t Recall:",recall, "\t F1 score:",f1)
  
  return accuracy, precision, recall, f1



#   ====================================== DEEP SORT ======================================
def deep_sort(tracker,detections,colors,frame,set_of_id,vid,frame_num,array_of_data,flag_info, folder_path, detect_what):
  import cv2
  # Call the tracker
  tracker.predict()
  tracker.update(detections)

  # update tracks
  for track in tracker.tracks:
      if not track.is_confirmed() or track.time_since_update > 1:
          continue 
      bbox = track.to_tlbr()
      class_name = track.get_class()

      inside_roi, frame = roi(frame, bbox)
      if not inside_roi:
        continue

      # draw bbox on screen
      frame = boundingBox(track, colors, frame, bbox, class_name)

      if (track.track_id not in set_of_id):
        set_of_id.add(track.track_id)

        # Panggil panggil fungsi
        ss_path = screenshot(frame, track.track_id, folder_path, detect_what)
        time_stamp = str(timestamps(vid))
        real_size, real_x, real_y = measure_bbox(int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))
        current_count = counting(set_of_id)

        data = [track.track_id, detect_what, frame_num, ss_path, time_stamp, real_size, real_x, real_y, bbox, current_count]
        array_of_data.append(data)

      # if enable info flag then print details about each track
      if flag_info:
          print("Tracker ID: {}, Class: {},  BBox Coords (xmin, ymin, xmax, ymax): {}".format(str(track.track_id), class_name, (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))))
  return(frame,array_of_data,set_of_id,tracker)




#   ====================================== OBJECT DETECTION ======================================
def detection_and_deepsort(input_path, detect_what, score_threshold, iou_threshold, output_folder):
  import os
  # comment out below line to enable tensorflow logging outputs
  os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
  import csv
  import time
  import tensorflow as tf
  physical_devices = tf.config.experimental.list_physical_devices('GPU')
  if len(physical_devices) > 0:
      tf.config.experimental.set_memory_growth(physical_devices[0], True)
  from tensorflow.python.saved_model import tag_constants
  from PIL import Image
  import cv2
  import numpy as np
  import matplotlib.pyplot as plt
  from tensorflow.compat.v1 import ConfigProto
  from tensorflow.compat.v1 import InteractiveSession
  # deep sort imports
  from dependency.deep_sort import preprocessing, nn_matching
  from dependency.deep_sort.detection import Detection
  from dependency.deep_sort.tracker import Tracker
  from dependency.tools import generate_detections as gdet

  # Ngebuat folder result kalo belom ada
  if not os.path.exists("result"):
      os.makedirs("result")

  # Variabel penting
  flag_video = input_path

  folder_path = "result/"+output_folder
  if not os.path.exists(folder_path):
      os.makedirs(folder_path)
      
  flag_output = "result/"+output_folder+"/"+detect_what+"_"+output_folder+".mp4"

  folder_eval_path = "result/"+output_folder+"/eval"
  if not os.path.exists(folder_eval_path):
      os.makedirs(folder_eval_path)

  csv_path = "result/"+output_folder+"/eval/"+detect_what+"_"+output_folder+".csv"

  eval_path ="result/"+output_folder+"/eval/eval_"+detect_what+"_"+output_folder+".csv"
  
  if detect_what == "Lubang":
    flag_weights = "dependency/model/Lubang"
  else:
    flag_weights = "dependency/model/Retak Kulit Buaya"
  flag_score = score_threshold
  flag_iou = iou_threshold

  # Definition of the parameters
  max_cosine_distance = 0.4
  nms_max_overlap = 1.0

  # initialize deep sort
  model_filename = 'dependency/model/untuk_deepsort.pb'
  encoder = gdet.create_box_encoder(model_filename, batch_size=1)
  # calculate cosine distance metric
  metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, None)
  # initialize tracker
  tracker = Tracker(metric)

  # load configuration for object detector
  config = ConfigProto()
  config.gpu_options.allow_growth = True
  session = InteractiveSession(config=config)

  video_path = flag_video

  saved_model_loaded = tf.saved_model.load(flag_weights, tags=[tag_constants.SERVING])
  infer = saved_model_loaded.signatures['serving_default']

  # begin video capture
  vid = cv2.VideoCapture(video_path)

  out = None

  # get video ready to save locally if flag is set
  # by default VideoCapture returns float instead of int
  width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
  height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
  fps = int(vid.get(cv2.CAP_PROP_FPS))
  codec = cv2.VideoWriter_fourcc(*'mp4v')
  out = cv2.VideoWriter(flag_output, codec, fps, (width, height))

  frame_num = 0
  set_of_id = set()

  # untuk csv detail Lubang / Retak Kulit Buaya
  header = ['id_kerusakan', 'jenis_kerusakan', 'frame', 'screenshoot', 'timestamp', 'real_size', 'real_x', 'real_y', 'bbox', 'total_count']
  
  f = open(csv_path, 'w')
  writer = csv.writer(f)
  array_of_data = []

  # untuk csv evaluasi
  header_eval = ['frame', 'actual', 'predicted', 'prob']
  f_eval = open(eval_path, 'w')
  writer_eval = csv.writer(f_eval)
  array_of_data_eval = []

  def format_boxes(bboxes, image_height, image_width):
    for box in bboxes:
        ymin = int(box[0] * image_height)
        xmin = int(box[1] * image_width)
        ymax = int(box[2] * image_height)
        xmax = int(box[3] * image_width)
        width = xmax - xmin
        height = ymax - ymin
        box[0], box[1], box[2], box[3] = xmin, ymin, width, height
    return bboxes

  # while video is running
  while True:
      return_value, frame = vid.read()
      if return_value:
          frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
          image = Image.fromarray(frame)
      else:
          print('Video sudah selesai!')
          break
      frame_num +=1
      print('Frame deteksi '+ detect_what +' #: '+ str(frame_num))
      frame_size = frame.shape[:2]
      image_data = cv2.resize(frame, (416, 416))
      image_data = image_data / 255.
      image_data = image_data[np.newaxis, ...].astype(np.float32)
      start_time = time.time()

      batch_data = tf.constant(image_data)
      pred_bbox = infer(batch_data)
      for key, value in pred_bbox.items():
        boxes = value[:, :, 0:4]
        pred_conf = value[:, :, 4:]

      boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
          boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
          scores=tf.reshape(
              pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
          max_output_size_per_class=50,
          max_total_size=50,
          iou_threshold=flag_iou,
          score_threshold=flag_score
      )

      # convert data to numpy arrays and slice out unused elements
      num_objects = valid_detections.numpy()[0]
      bboxes = boxes.numpy()[0]
      bboxes = bboxes[0:int(num_objects)]
      scores = scores.numpy()[0]
      scores = scores[0:int(num_objects)]
      classes = classes.numpy()[0]
      classes = classes[0:int(num_objects)]

      # format bounding boxes from normalized ymin, xmin, ymax, xmax ---> xmin, ymin, width, height
      original_h, original_w, _ = frame.shape
      bboxes = format_boxes(bboxes, original_h, original_w)

      # store all predictions in one parameter for simplicity when calling functions
      pred_bbox = [bboxes, scores, classes, num_objects]
      
      if detect_what == "Lubang":
        names=['Lubang']
      else:
        names=['Retak Kulit Buaya']

      # encode yolo detections and feed to tracker
      features = encoder(frame, bboxes)
      detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in zip(bboxes, scores, names, features)]

      #initialize color map
      cmap = plt.get_cmap('tab20b')
      colors = [cmap(i)[:3] for i in np.linspace(0, 1, 20)]

      # run non-maxima supression
      boxs = np.array([d.tlwh for d in detections])
      scores = np.array([d.confidence for d in detections])
      classes = np.array([d.class_name for d in detections])
      indices = preprocessing.non_max_suppression(boxs, classes, nms_max_overlap, scores)
      detections = [detections[i] for i in indices]

      # ngeappend ke array untuk ke csv evaluasi
      if len(scores) != 0:
        if detect_what == "Lubang":
          data_eval = [frame_num, "", "Lubang", scores]
          array_of_data_eval.append(data_eval)
        else:
          data_eval = [frame_num, "", "Retak Kulit Buaya", scores]
          array_of_data_eval.append(data_eval)

      # Untuk naro skor confidence di framenya (soalnya kalo udah masuk deepsort udah gaada lagi skor confidencenya)
      for d in detections:
        color = (0, 0, 0) # hitam legam

        x_kiri_atas = int(d.to_tlbr()[0])+(len(detect_what)+5)*17
        y_kiri_atas = int(d.to_tlbr()[1]-30)
        x_kanan_bawah = x_kiri_atas + (len(str(d.confidence)))*17
        y_kanan_bawah = int(d.to_tlbr()[1])

        # Untuk kotak tempat text confidence score
        cv2.rectangle(frame, (x_kiri_atas, y_kiri_atas), (x_kanan_bawah, y_kanan_bawah), color, -1)

        # Ya untuk text confidence score
        cv2.putText(frame, str(d.confidence),(x_kiri_atas, y_kiri_atas+20),0, 0.75, (255,255,255),2)

      frame,array_of_data,set_of_id,tracker = deep_sort(tracker,detections,colors,frame,
                                                        set_of_id,vid,frame_num,array_of_data,True, folder_path, detect_what)
      
      # calculate frames per second of running detections
      fps = 1.0 / (time.time() - start_time)
      print("FPS: %.2f" % fps)
      result = np.asarray(frame)
      result = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
      
      
      # if output flag is set, save video file
      out.write(result)
      if cv2.waitKey(1) & 0xFF == ord('q'): break
  
  session.close()

  writer.writerow(header)
  writer.writerows(array_of_data)

  writer_eval.writerow(header_eval)
  writer_eval.writerows(array_of_data_eval)

  f.close()
  f_eval.close()

  out.release()
  cv2.destroyAllWindows()
  return flag_output, csv_path




#   ====================================== FUNGSI PIPELINE ======================================
def road_damage_detection(input_video, out_folder):
  slow_vid_path = slow_down_video(input_video, out_folder)

  # Yang Lubang dulu
  detect_what = "Lubang"
  confidence_threshold = 0.4 # Batas bawah confidence level, prediksi yang conf levelnya berada di bawah 0.4 tidak dianggap (skala 0 sampai 1.0)
  iou_threshold = 1.0 # Intersection over union, semakin tinggi ID switch semakin rendah (skala 0 sampai 1.0)
  output_folder = out_folder

  lubang_path, csv_lubang_path = detection_and_deepsort(slow_vid_path,
                      detect_what, 
                      confidence_threshold,
                      iou_threshold,
                      output_folder)
  
  # Yang Retak Kulit Buaya
  detect_what = "Retak Kulit Buaya"
  confidence_threshold = 0.15 # Batas bawah confidence level, prediksi yang conf levelnya berada di bawah 0.4 tidak dianggap (skala 0 sampai 1.0)
  iou_threshold = 1.0 # Intersection over union, semakin tinggi ID switch semakin rendah (skala 0 sampai 1.0)
  output_folder = out_folder

  retak_kulit_buaya_path, csv_retak_kulit_buaya_path = detection_and_deepsort(slow_vid_path,
                      detect_what, 
                      confidence_threshold,
                      iou_threshold,
                      output_folder)

  import pandas as pd
  df_lubang = pd.read_csv(csv_lubang_path)
  df_retak_kulit_buaya = pd.read_csv(csv_retak_kulit_buaya_path)

  pd.concat([df_lubang, df_retak_kulit_buaya]).to_csv('result/'+ out_folder +'/detail_deteksi.csv',index = False)
  
  print("Video hasil Lubang disimpan di:\n" + lubang_path +"\n\n")
  print("Video hasil Retak Kulit Buaya disimpan di:\n" + retak_kulit_buaya_path +"\n\n")