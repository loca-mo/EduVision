from src.computer_vision.raised_hand import RaisedHandDetector


def test_no_hand():
    detector = RaisedHandDetector()

    result = detector.analyze(None)

    assert result["gesture"] == "none"
    assert result["is_raised"] is False

    print("No-hand test: PASSED")


if __name__ == "__main__":
    test_no_hand()