# config.py
pose_identifier = None

def initialize_pose_identifier():
    global pose_identifier
    if pose_identifier is None:
        from posture_recognition.static_recognition import StaticPostureIdentifier
        pose_identifier = StaticPostureIdentifier()
    return pose_identifier