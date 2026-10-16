"""Execute the production C077 path through the linked ARM resident router."""
import runpy, struct, sys
from pathlib import Path

ns=runpy.run_path(str(Path(__file__).with_name("test_modules_arm.py")))
u,call,put,router=(ns[x] for x in ("u","call","put","router"))
u.mem_write(ns["a"],ns["old"]);put("bl2","mode",0)

def configure_idle():
    call("common","cn_init")
    for name,value,size in (("linked",1,1),("seen26",1,1),("seen28",1,1),
                            ("now",5000,4),("native26_at",5000,4),("native28_at",5000,4)):
        put("common",name,value,size)
    p26=bytearray(16);p26[6]=2
    u.mem_write(ns["symbols"]["common"]["native26"],bytes(p26))
    u.mem_write(ns["symbols"]["common"]["native28"],bytes(16))
    assert call("common","maintenance_ready")==1

def read(address,count=1):
    response=router(struct.pack(">BBHH",1,4,address,count))
    assert response[:3]==bytes([1,4,2*count]),response.hex()
    return struct.unpack(">"+"H"*count,response[3:-2])

uid=tuple(call("bl2","identity_read",address) for address in range(78,84))
assert uid==(0,1,0,2,0,3)
def envelope(gain,words=uid):
    return bytes([1,16,1,44,0,8,16])+struct.pack(">8H",0xc077,gain,*words)
def write(gain,words=uid):
    return router(envelope(gain,words))

configure_idle()
put("common","owner",3,1)
assert write(1420)[1:3]==bytes([0x90,6])
assert read(310)==(1350,) and read(346)==(0,)
put("common","owner",0,1)

bad=list(uid);bad[4]^=1
assert write(1420,bad)[1:3]==bytes([0x90,3])
assert write(1420)[:6]==envelope(1420)[:6]
assert read(308)==(4,) and read(310)==(1420,) and read(346)==(1,)

# Exact retry bypasses a newly busy gate; any changed seed remains locked out.
put("common","owner",3,1)
assert write(1420)[:6]==envelope(1420)[:6]
assert write(1430)[1:3]==bytes([0x90,3])
assert write(1420,bad)[1:3]==bytes([0x90,3])
assert read(310)==(1420,) and read(346)==(1,)

# Common init models reboot and restores the deterministic local fallback.
configure_idle()
assert read(310)==(1350,) and read(346)==(0,)
assert write(2000)[:6]==envelope(2000)[:6]
assert read(310)==(2000,) and read(346)==(1,)
print("PASS actual ARM gain seed: resident/Dispatcher route, exact UID, busy gate, one-per-boot retry lock and reboot fallback")
