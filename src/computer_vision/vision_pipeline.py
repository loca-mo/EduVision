import time

from src.computer_vision.multi_face_recognition import MultiFaceRecognizer
from src.computer_vision.object_detection import ObjectDetector
from src.computer_vision.distraction_detection import DistractionDetector
from src.computer_vision.hand_detection import HandDetector
from src.computer_vision.hand_gesture import RaisedHandDetector
from src.computer_vision.attendance_manager import AttendanceManager

from src.utils.data_manager import add_attendance_record, log_event

def _bbox_center(bbox):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def _point_in_bbox(point, bbox, pad_x=0, pad_y=0):
    if bbox is None or point is None:
        return False

    x1, y1, x2, y2 = bbox
    px, py = point

    return (
        (x1 - pad_x) <= px <= (x2 + pad_x)
        and
        (y1 - pad_y) <= py <= (y2 + pad_y)
    )

class VisionPipeline:

    def __init__(
        self,
        subject="General",
        min_presence_seconds=3,
        grace_period_seconds=12,

        # -----------------------------------------
        # Performance settings
        # -----------------------------------------
        face_every=5,
        object_every=3,
        hand_every=3,
    ):

        self.subject = subject

        # -----------------------------------------
        # AI modules
        # -----------------------------------------

        self.face_recognizer = MultiFaceRecognizer()

        self.object_detector = ObjectDetector()

        self.distraction_detector = DistractionDetector()

        self.hand_detector = HandDetector()

        self.raised_hand_detector = RaisedHandDetector()

        self.attendance_manager = AttendanceManager(
            min_presence_seconds=min_presence_seconds,
            grace_period_seconds=grace_period_seconds,
        )

        # -----------------------------------------
        # Performance
        # -----------------------------------------

        self.face_every = face_every
        self.object_every = object_every
        self.hand_every = hand_every

        self.frame_count = 0

        # -----------------------------------------
        # Cached AI results
        # -----------------------------------------

        self.last_faces = []
        self.last_objects = []
        self.last_hand_results = None

        self.last_result = None

        # -----------------------------------------
        # Timing information
        # -----------------------------------------

        self.last_processing_time = 0.0

    # ============================================================
    # MAIN PROCESSING
    # ============================================================

    def process_frame(self, frame):

        start_time = time.perf_counter()

        self.frame_count += 1

        # ========================================================
        # FACE RECOGNITION
        # ========================================================

        if (
            self.frame_count == 1
            or self.frame_count % self.face_every == 0
        ):

            try:
                self.last_faces = self.face_recognizer.process(
                    frame
                )

            except Exception as e:

                print(
                    f"Face recognition error: {e}"
                )

                # Keep previous faces instead of destroying
                # the last valid result.
                self.last_faces = self.last_faces or []

        faces = self.last_faces

        # ========================================================
        # OBJECT DETECTION
        # ========================================================

        if (
            self.frame_count == 1
            or self.frame_count % self.object_every == 0
        ):

            try:

                self.last_objects = (
                    self.object_detector.detect(frame)
                )

            except Exception as e:

                print(
                    f"Object detection error: {e}"
                )

                self.last_objects = (
                    self.last_objects or []
                )

        objects = self.last_objects

        # ========================================================
        # HAND DETECTION
        # ========================================================

        if (
            self.frame_count == 1
            or self.frame_count % self.hand_every == 0
        ):

            try:

                self.last_hand_results = (
                    self.hand_detector.detect(frame)
                )

            except Exception as e:

                print(
                    f"Hand detection error: {e}"
                )

                self.last_hand_results = None

        hand_results = self.last_hand_results

        # ========================================================
        # DISTRACTIONS
        # ========================================================

        distraction_events = (
            self.distraction_detector.analyze(
                objects
            )
        )

        phone_bboxes = [
            event["bbox"]
            for event in distraction_events
        ]

        any_phone_in_frame = (
            len(phone_bboxes) > 0
        )

        # ========================================================
        # RAISED HANDS
        # ========================================================

        raised_hand_points = (
            self._raised_hand_wrist_points(
                frame,
                hand_results
            )
        )

        any_hand_raised = (
            len(raised_hand_points) > 0
        )

        # ========================================================
        # BUILD PEOPLE
        # ========================================================

        people = []
        visible_ids = []

        for face in faces:

            person_id = face["id"]
            bbox = face["bbox"]

            visible_ids.append(person_id)

            # --------------------------------------------
            # Distraction
            # --------------------------------------------

            distracted = (
                self._is_person_distracted(
                    bbox,
                    phone_bboxes,
                    any_phone_in_frame
                )
            )

            # --------------------------------------------
            # Hand
            # --------------------------------------------

            hand_raised = (
                self._is_person_hand_raised(
                    bbox,
                    raised_hand_points,
                    any_hand_raised
                )
            )

            # --------------------------------------------
            # Focus
            # --------------------------------------------

            focus_score = (
                self._compute_focus_score(
                    recognized=face["recognized"],
                    distracted=distracted,
                )
            )

            people.append(
                {
                    "id": person_id,
                    "recognized": face["recognized"],
                    "attendance": self.attendance_manager.is_present(
                        person_id
                    ),
                    "focus_score": focus_score,
                    "distraction": distracted,
                    "hand_raised": hand_raised,
                    "bbox": bbox,
                }
            )

        # ========================================================
        # ATTENDANCE
        # ========================================================

        checked_in, checked_out = (
            self.attendance_manager.update(
                visible_ids
            )
        )

        self._log_attendance_changes(
            checked_in,
            checked_out
        )

        present_ids_now = (
            self.attendance_manager.present_ids()
        )

        for person in people:

            person["attendance"] = (
                person["id"] in present_ids_now
            )

        # ========================================================
        # STATISTICS
        # ========================================================

        raised_hands_count = sum(
            1
            for p in people
            if p["hand_raised"]
        )

        distraction_count = sum(
            1
            for p in people
            if p["distraction"]
        )

        average_focus = (
            sum(
                p["focus_score"]
                for p in people
            ) / len(people)
            if people
            else 0
        )

        # ========================================================
        # FINAL RESULT
        # ========================================================

        result = {

            "timestamp": time.time(),

            "people_count": len(people),

            "people": people,

            "objects": objects,

            "average_focus": round(
                average_focus,
                1
            ),

            "distraction_count": (
                distraction_count
            ),

            "raised_hands": (
                raised_hands_count
            ),

            "present_ids": sorted(
                present_ids_now
            ),
        }

        # ========================================================
        # SAVE LAST RESULT
        # ========================================================

        self.last_result = result

        self.last_processing_time = (
            time.perf_counter() - start_time
        )

        return result

    # ============================================================
    # HAND HELPERS
    # ============================================================

    def _raised_hand_wrist_points(
        self,
        frame,
        hand_results
    ):

        points = []

        if (
            not hand_results
            or not hand_results.hand_landmarks
        ):
            return points

        height, width = frame.shape[:2]

        for hand_landmarks in (
            hand_results.hand_landmarks
        ):

            if self.raised_hand_detector.is_raised(
                hand_landmarks
            ):

                wrist = hand_landmarks[0]

                points.append(
                    (
                        wrist.x * width,
                        wrist.y * height
                    )
                )

        return points

    # ============================================================
    # DISTRACTION
    # ============================================================

    @staticmethod
    def _is_person_distracted(
        bbox,
        phone_bboxes,
        any_phone_in_frame
    ):

        if not phone_bboxes:
            return False

        if bbox is None:
            return False

        person_center = _bbox_center(
            bbox
        )

        x1, y1, x2, y2 = bbox

        pad_x = (x2 - x1) * 2
        pad_y = (y2 - y1) * 3

        for phone_bbox in phone_bboxes:

            phone_center = _bbox_center(
                phone_bbox
            )

            if _point_in_bbox(
                phone_center,
                bbox,
                pad_x,
                pad_y
            ):

                return True

        return False

    # ============================================================
    # HAND ASSOCIATION
    # ============================================================

    @staticmethod
    def _is_person_hand_raised(
        bbox,
        raised_hand_points,
        any_hand_raised
    ):

        if not raised_hand_points:
            return False

        if bbox is None:
            return False

        x1, y1, x2, y2 = bbox

        pad_x = (x2 - x1) * 2
        pad_y = (y2 - y1) * 4

        for point in raised_hand_points:

            if _point_in_bbox(
                point,
                bbox,
                pad_x,
                pad_y
            ):

                return True

        return False

    # ============================================================
    # FOCUS
    # ============================================================

    @staticmethod
    def _compute_focus_score(
        recognized,
        distracted
    ):

        score = 60

        if recognized:
            score += 20

        if not distracted:
            score += 20

        return min(
            score,
            100
        )

    # ============================================================
    # ATTENDANCE
    # ============================================================

    def _log_attendance_changes(
        self,
        checked_in,
        checked_out
    ):

        for person_id in checked_in:

            try:

                add_attendance_record(
                    student_id=person_id,
                    student_name=person_id,
                    status="Present",
                    subject=self.subject,
                )

            except Exception as e:

                print(
                    f"Failed to record attendance "
                    f"for {person_id}: {e}"
                )

            log_event(
                event_type="check_in",
                source_module="vision_pipeline",
                details=person_id,
            )

        for person_id in checked_out:

            log_event(
                event_type="check_out",
                source_module="vision_pipeline",
                details=person_id,
            )

    # ============================================================
    # DRAW ANNOTATIONS
    # ============================================================

    def draw_annotations(self, frame):

        import cv2

        if self.last_result is None:
            return frame

        for person in self.last_result["people"]:

            bbox = person["bbox"]

            if not bbox:
                continue

            x1, y1, x2, y2 = bbox

            color = (
                (0, 0, 255)
                if person["distraction"]
                else (0, 255, 0)
            )

            cv2.rectangle(
                frame,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                color,
                2
            )

            label = (
                f'{person["id"]} | '
                f'Focus {person["focus_score"]}%'
            )

            if person["hand_raised"]:
                label += " | Hand up"

            cv2.putText(
                frame,
                label,
                (
                    int(x1),
                    max(int(y1) - 10, 20)
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        frame = (
            self.object_detector.draw_detections(
                frame,
                self.last_result["objects"]
            )
        )

        return frame

    # ============================================================
    # CLOSE
    # ============================================================

    def close(self):

        try:
            self.hand_detector.close()
        except Exception:
            pass