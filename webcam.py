import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import drawing_styles
import cv2
import threading
import time
import mediapipe as mp

class Webcam:
  def __init__(self, id_camera, largura , altura):
    self.id_camera = id_camera
    self.largura = largura
    self.altura = altura
    self.cap = cv2.VideoCapture(self.id_camera)
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.largura)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.altura)

    self.frame = None
    self.ok = False
    self.running = False
    self.lock = threading.Lock()

  def start(self):
    if not self.cap.isOpened():
      print(f"[Aviso] Não foi possível abrir a câmera {self.cam_id}")
      return self
    self.running = True
    self.thread = threading.Thread(target=self._update, daemon=True)
    self.thread.start()
    return self
  
  def _update(self):
    while self.running:
      ok, frame = self.cap.read()
      with self.lock:
        self.ok = ok
        self.frame = frame if ok else self.frame
      if not ok:
        time.sleep(0.05)

  def read(self):
    with self.lock:
      if self.frame == None:
        return False, None
      return self.ok, self.frame.copy()
  
  def stop(self):
    self.running = False
    if hasattr(self, "thread"):
      self.thread.join(timeout=1)
    self.cap.release()


def bounding_box(landmark ,  width , height):
  #print(landmark, "\n")
  
  xmin = float('inf')
  ymin = float('inf')
  xmax = float('-inf')
  ymax = float('-inf')
  for poit in landmark:
    x = int(poit.x * width)
    y = int(poit.y * height)
    if x < xmin:
      xmin = x
    if y < ymin:
      ymin = y
    if x > xmax:
      xmax = x
    if y > ymax:
      ymax = y
  print(xmin, ymin, xmax, ymax)
  return (xmin, ymin, xmax, ymax)

def draw_landmarks_on_image(rgb_image, pose_landmarks):
  
  annotated_image = np.copy(rgb_image)

  pose_landmark_style = drawing_styles.get_default_pose_landmarks_style()
  pose_connection_style = drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2)

  
  drawing_utils.draw_landmarks(
      image=annotated_image,
      landmark_list=pose_landmarks,
      connections=vision.PoseLandmarksConnections.POSE_LANDMARKS,
      landmark_drawing_spec=pose_landmark_style,
      connection_drawing_spec=pose_connection_style)

  return annotated_image



base_options = python.BaseOptions(model_asset_path='pose_landmarker_lite.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True)
detector = vision.PoseLandmarker.create_from_options(options)

def process_frame(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame[:, :, ::-1])

    detection_result = detector.detect(image)

    poseLandmarkList = detection_result.pose_landmarks
    if poseLandmarkList:
      for idx , landmark in enumerate(poseLandmarkList):
        annotated_image = draw_landmarks_on_image(image.numpy_view(), landmark)
      return cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
