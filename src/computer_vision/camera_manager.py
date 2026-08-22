import platform
import threading

import cv2

class CameraManager:
    """
    Thread-safe singleton wrapper around ONE cv2.VideoCapture.

    Optimized for real-time AI/computer-vision processing:
    - Uses 640x480 by default instead of 1280x720.
    - Uses DirectShow on Windows.
    - Sets a target FPS.
    - Discards initial frames when opening.
    - Uses a lock around camera access.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False

            return cls._instance

    def __init__(
        self,
        camera_index=0,
        width=640,
        height=480,
        fps=30
    ):
        if self._initialized:
            return

        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps

        self.cap = None

        # Protect camera access
        self._frame_lock = threading.Lock()

        self._initialized = True

    def open(self):
        """
        Open the camera if it isn't already open.

        Returns:
            True  -> camera opened successfully
            False -> camera could not be opened
        """

        with self._frame_lock:

            # Already open
            if self.cap is not None and self.cap.isOpened():
                return True

            candidates = []

            # Windows: DirectShow is usually better for webcam latency
            if platform.system() == "Windows":
                candidates.append(cv2.CAP_DSHOW)

            # Fallback
            candidates.append(cv2.CAP_ANY)

            for backend in candidates:

                cap = cv2.VideoCapture(
                    self.camera_index,
                    backend
                )

                if not cap.isOpened():
                    cap.release()
                    continue

                self.cap = cap
                break

            # No backend worked
            if self.cap is None:
                return False

            # --------------------------------------------------
            # Camera settings
            # --------------------------------------------------

            self.cap.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                self.width
            )

            self.cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                self.height
            )

            self.cap.set(
                cv2.CAP_PROP_FPS,
                self.fps
            )

            # Reduce internal buffering where supported.
            # This helps prevent displaying old frames.
            self.cap.set(
                cv2.CAP_PROP_BUFFERSIZE,
                1
            )

            # --------------------------------------------------
            # Print actual camera settings
            # --------------------------------------------------

            actual_width = int(
                self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            )

            actual_height = int(
                self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            )

            actual_fps = self.cap.get(
                cv2.CAP_PROP_FPS
            )

            print(
                f"Camera opened: "
                f"{actual_width}x{actual_height} "
                f"@ {actual_fps:.1f} FPS"
            )

            # --------------------------------------------------
            # Warm-up
            # --------------------------------------------------

            for _ in range(5):
                self.cap.read()

            return True

    def read(self):
        """
        Read one frame.

        Returns:
            (True, frame)
            (False, None)
        """

        if self.cap is None or not self.cap.isOpened():

            if not self.open():
                return False, None

        with self._frame_lock:

            if self.cap is None:
                return False, None

            ret, frame = self.cap.read()

            if not ret or frame is None:
                return False, None

            return True, frame

    def is_opened(self):
        """Return True if the camera is currently open."""

        return (
            self.cap is not None
            and self.cap.isOpened()
        )

    def release(self):
        """Release the camera."""

        with self._frame_lock:

            if self.cap is not None:

                try:
                    self.cap.release()
                except Exception:
                    pass

                self.cap = None

    def get_resolution(self):
        """Return the actual camera resolution."""

        if self.cap is None or not self.cap.isOpened():
            return None

        width = int(
            self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        height = int(
            self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        return width, height

    def get_fps(self):
        """Return the camera FPS reported by OpenCV."""

        if self.cap is None or not self.cap.isOpened():
            return None

        return self.cap.get(
            cv2.CAP_PROP_FPS
        )