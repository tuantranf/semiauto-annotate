from threading import Thread
from queue import Queue
from time import time

from labelme.utils import Config
from pose_estm.pose_detection import PoseDetection
from yolo.yolo_class import YOLO
from .pose_estm_parser import PoseEstmParser
from .yolo_parser import YoloParser


class ModelLoader(object):
    def __init__(self, on_inited):
        t0 = time()
        self.pose_detection = PoseDetection()
        t1 = time()
        print(f'Pose detection loaded in {t1 - t0} secs')
        self.yolo = YOLO()
        print(f'Yolo loaded in {time() - t1} secs')
        self.task_queue = Queue()
        on_inited(True, self)
        while True:
            image_file, on_completion = self.task_queue.get()
            self._infer(image_file, on_completion)

    def _infer(self, image_file, on_completion):
        results = []
        t0 = time()
        try:
            labels = Config.get('labels').keys()
            yolo_json = self.yolo.infer_on_image(image_file)
            yolo = YoloParser(yolo_json, accepted_label=labels)
            results.extend(yolo.data)
        except Exception as e:
            print(e)
        t1 = time()
        print(f'Yolo inference in {t1 - t0} secs')
        try:
            pose_estm_json = self.pose_detection.infer_on_image(image_file)
            pose_estm = PoseEstmParser(pose_estm_json)
            results.extend(pose_estm.data)
        except Exception as e:
            print(e)
        print(f'Pose detection inference in {time() - t1} secs')
        on_completion(True, results)

    @classmethod
    def main_thread_ctor(cls, on_completion):
        load_thread = Thread(
            target=cls,
            args=(on_completion,)
        )
        load_thread.start()

    def main_thread_infer(self, image_path, on_completion):
        self.task_queue.put((image_path, on_completion))
