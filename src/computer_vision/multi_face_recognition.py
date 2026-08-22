import os
import time
from pathlib import Path

import cv2
import numpy as np
from deepface import DeepFace


os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")


class MultiFaceRecognizer:
    """
    Multi-face recognition optimized for real-time classroom monitoring.

    Important:
    - Does NOT automatically create a new person when recognition fails.
    - Recognition is throttled.
    - Uses cached results between recognition frames.
    - Uses a smaller image for DeepFace to reduce CPU load.
    """

    def __init__(
        self,
        faces_dir="faces",
        model_name="Facenet512",
        detector_backend="opencv",
        distance_threshold=0.35,

        # Run face recognition every N pipeline frames.
        check_every=8,

        # Maximum width sent to DeepFace.
        max_width=640,

        # Keep previous recognition briefly.
        max_cache_age=1.5,
    ):

        self.faces_dir = Path(faces_dir)

        self.model_name = model_name
        self.detector_backend = detector_backend
        self.distance_threshold = distance_threshold

        self.check_every = max(1, check_every)
        self.max_width = max_width
        self.max_cache_age = max_cache_age

        self.known_faces = []

        self._frame_count = 0
        self._last_results = []
        self._last_recognition_time = 0.0

        self.last_error = None

        self.faces_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self._load_known_faces()

    # =========================================================
    # LOAD KNOWN FACES
    # =========================================================

    def _load_known_faces(self):

        print("Loading known faces...")

        for person_folder in self.faces_dir.iterdir():

            if not person_folder.is_dir():
                continue

            person_id = person_folder.name

            for image_path in person_folder.iterdir():

                if image_path.suffix.lower() not in (
                    ".jpg",
                    ".jpeg",
                    ".png",
                ):
                    continue

                try:

                    embedding = DeepFace.represent(
                        img_path=str(image_path),
                        model_name=self.model_name,
                        detector_backend=self.detector_backend,
                        enforce_detection=False,
                    )

                    if not embedding:
                        continue

                    if isinstance(embedding, list):
                        embedding = embedding[0]

                    vector = embedding.get("embedding")

                    if vector is None:
                        continue

                    vector = self._normalize(
                        np.asarray(
                            vector,
                            dtype=np.float32
                        )
                    )

                    self.known_faces.append(
                        {
                            "id": person_id,
                            "embedding": vector,
                        }
                    )

                    print(
                        f"Loaded face: {person_id}"
                    )

                    # One good reference image is enough
                    # for the current implementation.
                    break

                except Exception as e:

                    print(
                        f"Failed loading "
                        f"{image_path}: {e}"
                    )

        print(
            f"Loaded "
            f"{len(self.known_faces)} "
            f"known face(s)."
        )

    # =========================================================
    # NORMALIZE EMBEDDING
    # =========================================================

    @staticmethod
    def _normalize(vector):

        vector = np.asarray(
            vector,
            dtype=np.float32
        )

        norm = np.linalg.norm(vector)

        if norm == 0:
            return vector

        return vector / norm

    # =========================================================
    # COSINE DISTANCE
    # =========================================================

    @staticmethod
    def _cosine_distance(a, b):

        a = MultiFaceRecognizer._normalize(a)
        b = MultiFaceRecognizer._normalize(b)

        return float(
            1.0 - np.dot(a, b)
        )

    # =========================================================
    # FIND PERSON
    # =========================================================

    def _find_person(self, embedding):

        if not self.known_faces:
            return None, None

        best_id = None
        best_distance = float("inf")

        for person in self.known_faces:

            distance = self._cosine_distance(
                embedding,
                person["embedding"]
            )

            if distance < best_distance:

                best_distance = distance
                best_id = person["id"]

        if (
            best_id is not None
            and best_distance <= self.distance_threshold
        ):
            return best_id, best_distance

        return None, best_distance

    # =========================================================
    # BBOX
    # =========================================================

    @staticmethod
    def _area_to_bbox(area):

        if not area:
            return None

        x = int(area.get("x", 0))
        y = int(area.get("y", 0))
        w = int(area.get("w", 0))
        h = int(area.get("h", 0))

        if w <= 0 or h <= 0:
            return None

        return (
            x,
            y,
            x + w,
            y + h,
        )

    # =========================================================
    # RESIZE FOR AI
    # =========================================================

    def _prepare_frame(self, frame):

        height, width = frame.shape[:2]

        if width <= self.max_width:
            return frame, 1.0

        scale = self.max_width / width

        new_width = self.max_width
        new_height = int(height * scale)

        resized = cv2.resize(
            frame,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA,
        )

        return resized, scale

    # =========================================================
    # MAIN PROCESS
    # =========================================================

    def process(self, frame):

        self._frame_count += 1

        now = time.monotonic()

        # -----------------------------------------------------
        # Use cached result
        # -----------------------------------------------------

        if (
            self._frame_count % self.check_every != 0
            and self._last_results
            and now - self._last_recognition_time
            < self.max_cache_age
        ):

            return self._last_results

        # -----------------------------------------------------
        # Prepare smaller image
        # -----------------------------------------------------

        small_frame, scale = self._prepare_frame(frame)

        try:

            faces = DeepFace.represent(

                img_path=small_frame,

                model_name=self.model_name,

                detector_backend=self.detector_backend,

                enforce_detection=False,

                align=True,
            )

            self.last_error = None

        except Exception as e:

            self.last_error = (
                f"{type(e).__name__}: {e}"
            )

            print(
                "Face recognition failed:",
                self.last_error
            )

            return self._last_results

        if isinstance(faces, dict):
            faces = [faces]

        results = []

        for face in faces or []:

            embedding = face.get(
                "embedding"
            )

            if embedding is None:
                continue

            bbox = self._area_to_bbox(
                face.get("facial_area")
            )

            # Convert bbox from resized image
            # back to original camera resolution.

            if bbox is not None and scale != 1.0:

                x1, y1, x2, y2 = bbox

                bbox = (
                    int(x1 / scale),
                    int(y1 / scale),
                    int(x2 / scale),
                    int(y2 / scale),
                )

            # -------------------------------------------------
            # Recognition
            # -------------------------------------------------

            person_id, distance = (
                self._find_person(
                    embedding
                )
            )

            recognized = (
                person_id is not None
            )

            # IMPORTANT:
            # Do NOT create a new person automatically.
            #
            # Unknown faces remain "Unknown".
            #

            if not recognized:

                person_id = "Unknown"

            results.append(
                {
                    "id": person_id,
                    "recognized": recognized,
                    "distance": (
                        float(distance)
                        if distance is not None
                        else None
                    ),
                    "bbox": bbox,
                }
            )

        self._last_results = results
        self._last_recognition_time = now

        return results

    # =========================================================
    # OPTIONAL: ADD PERSON MANUALLY
    # =========================================================

    def add_person(
        self,
        frame,
        bbox,
        person_id=None
    ):

        if person_id is None:

            numbers = []

            for folder in self.faces_dir.iterdir():

                if not folder.is_dir():
                    continue

                if not folder.name.startswith(
                    "Person_"
                ):
                    continue

                try:
                    numbers.append(
                        int(
                            folder.name.split("_")[1]
                        )
                    )
                except (
                    IndexError,
                    ValueError
                ):
                    pass

            number = (
                max(numbers) + 1
                if numbers
                else 1
            )

            person_id = (
                f"Person_{number:03d}"
            )

        x1, y1, x2, y2 = bbox

        h, w = frame.shape[:2]

        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(w, int(x2))
        y2 = min(h, int(y2))

        crop = frame[
            y1:y2,
            x1:x2
        ]

        if crop.size == 0:
            return None

        folder = (
            self.faces_dir /
            person_id
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        image_path = (
            folder / "face.jpg"
        )

        cv2.imwrite(
            str(image_path),
            crop
        )

        try:

            embedding = DeepFace.represent(
                img_path=crop,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                enforce_detection=False,
            )

            if isinstance(
                embedding,
                list
            ):
                embedding = embedding[0]

            embedding = self._normalize(
                embedding["embedding"]
            )

            self.known_faces.append(
                {
                    "id": person_id,
                    "embedding": embedding,
                }
            )

            return person_id

        except Exception as e:

            print(
                f"Failed adding {person_id}: {e}"
            )

            return None