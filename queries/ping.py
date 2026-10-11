print("pong")
import omni.usd

stage = omni.usd.get_context().get_stage()
print("stage", "ok" if stage else "none")
