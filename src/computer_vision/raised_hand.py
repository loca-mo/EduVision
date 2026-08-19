class RaisedHandDetector:
    def __init__(self, wrist_height_ratio=0.70):
        self.wrist_height_ratio = wrist_height_ratio

    def is_raised(self, hand_landmarks):
        if not hand_landmarks:
            return False

        wrist = hand_landmarks[0]

        # A smaller y value means the point is higher in the image.
        return wrist.y < self.wrist_height_ratio