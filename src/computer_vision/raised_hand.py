class RaisedHandDetector:
    def __init__(self):
        pass

    def is_raised(self, hand_landmarks):
        if not hand_landmarks:
            return False

        wrist = hand_landmarks[0]

        index_mcp = hand_landmarks[5]
        index_pip = hand_landmarks[6]
        index_tip = hand_landmarks[8]

        middle_mcp = hand_landmarks[9]
        middle_pip = hand_landmarks[10]
        middle_tip = hand_landmarks[12]

        index_raised = (
            index_tip.y < index_pip.y < index_mcp.y
        )

        middle_raised = (
            middle_tip.y < middle_pip.y < middle_mcp.y
        )

        wrist_below_fingers = (
            wrist.y > index_tip.y
            and wrist.y > middle_tip.y
        )

        return (
            index_raised
            and middle_raised
            and wrist_below_fingers
        )

    def analyze(self, hand_landmarks):
        raised = self.is_raised(hand_landmarks)

        return {
            "gesture": "raised_hand" if raised else "none",
            "is_raised": raised,
        }
        from src.computer_vision.raised_hand import RaisedHandDetector


def test_no_hand():
    detector = RaisedHandDetector()

    result = detector.analyze(None)

    assert result["gesture"] == "none"
    assert result["is_raised"] is False

    print("No-hand test: PASSED")


if __name__ == "__main__":
    test_no_hand()