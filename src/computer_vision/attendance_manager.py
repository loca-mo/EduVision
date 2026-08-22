import time


class AttendanceManager:
    """
    Turns raw per-frame face-recognition results into check-in / check-out
    attendance events, instead of writing a new attendance record every
    single frame (which would flood the CSV with thousands of rows for
    one person).

    - A person is checked IN only after their face has been seen
      continuously for `min_presence_seconds`.
    - A person is checked OUT only after they've been missing for
      `grace_period_seconds` (so briefly looking away or a missed frame
      doesn't count as leaving the room).
    """

    def __init__(self, min_presence_seconds=3, grace_period_seconds=12):
        self.min_presence_seconds = min_presence_seconds
        self.grace_period_seconds = grace_period_seconds

        self._first_seen = {}    # person_id -> first-seen timestamp (this streak)
        self._last_seen = {}     # person_id -> last-seen timestamp
        self._checked_in = set()  # person_ids currently marked present

    def update(self, visible_ids, now=None):
        """
        visible_ids: iterable of person_ids detected in the current frame.

        Returns (checked_in_now, checked_out_now): lists of person_ids
        whose attendance status changed as a result of this call.
        """
        now = now if now is not None else time.time()
        visible_ids = set(visible_ids)

        checked_in_now = []
        checked_out_now = []

        # --- People visible this frame -------------------------------
        for person_id in visible_ids:
            if person_id not in self._first_seen:
                self._first_seen[person_id] = now

            self._last_seen[person_id] = now

            already_in = person_id in self._checked_in
            seen_long_enough = (
                now - self._first_seen[person_id] >= self.min_presence_seconds
            )

            if not already_in and seen_long_enough:
                self._checked_in.add(person_id)
                checked_in_now.append(person_id)

        # --- People who were present but are now missing --------------
        for person_id in list(self._checked_in):
            if person_id in visible_ids:
                continue

            last_seen = self._last_seen.get(person_id, 0)

            if now - last_seen >= self.grace_period_seconds:
                self._checked_in.discard(person_id)
                self._first_seen.pop(person_id, None)
                checked_out_now.append(person_id)

        return checked_in_now, checked_out_now

    def is_present(self, person_id):
        return person_id in self._checked_in

    def present_ids(self):
        return set(self._checked_in)
