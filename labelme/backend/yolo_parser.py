from qtpy.QtCore import QPointF

from labelme.shape import Shape, LabeledPoint


class YoloParser(object):
    def __init__(self, filename, accepted_label=None):
        self.data = None
        self.accepted_label = accepted_label
        if filename is not None:
            self.load(filename)
        self.filename = filename

    def load(self, filename):
        import json
        from collections import namedtuple
        with open(filename, 'r') as f:
            loaded = json.load(f, object_hook=lambda d: namedtuple('X', d.keys(), rename=True)(*d.values()))
        self.data = [self.yolo_dict_to_shape(yolo_dict) for yolo_dict in loaded]
        self.data = [x for x in self.data if x is not None]

    def yolo_dict_to_shape(self, val):
        label = val._1
        if label not in self.accepted_label:
            print(f'Dropped shape of label {label}')
            return None
        loc = val.location
        points = [
            QPointF(loc.left, loc.top),
            QPointF(loc.right, loc.bottom)
        ]
        points = [LabeledPoint(p) for p in points]
        return Shape.from_points(
            points,
            label=label,
            shape_type='rectangle'
        )
