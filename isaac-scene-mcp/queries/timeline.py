import json

ACTION = """__ACTION__"""

import omni.timeline

tl = omni.timeline.get_timeline_interface()
before = tl.is_playing()

if ACTION == "play":
    tl.play()
elif ACTION == "pause":
    tl.pause()
elif ACTION == "stop":
    tl.stop()
elif ACTION == "status":
    pass
else:
    raise RuntimeError(f"Unknown action: {ACTION}. Use play|pause|stop|status")

print(
    json.dumps(
        {
            "action": ACTION,
            "was_playing": before,
            "playing": tl.is_playing(),
            "current_time": tl.get_current_time(),
        },
        indent=2,
    )
)
