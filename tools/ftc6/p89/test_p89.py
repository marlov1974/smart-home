import ast,json,os,sys,tempfile,unittest
from pathlib import Path
from controls import ownership,inhibit_status,inhibit_write,counter_step,demand_selection,target35,scaled_temperature
from codec import frame,parse,a3,plan_read
from models import ServiceObserver,SettingsObserver,preserve_category
from report import build,render
from extract_evidence import image,extract
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'requirements/package-runs/P0089'
class Offline(unittest.TestCase):
    def test_ownership(self):
        self.assertEqual(ownership(0,request=True),1)
        for kw in ({'system':2},{'system':3},{'override':1},{'watchdog':1}):
            self.assertEqual(ownership(0,request=True,**kw),0);self.assertEqual(ownership(1,**kw),0)
        self.assertEqual(ownership(1,peer_release=True),0);self.assertEqual(ownership(1,release=True),0)
        self.assertEqual(ownership(7,request=True),0)
    def test_inhibit_selection(self):
        self.assertEqual(inhibit_status(0,17,2,8),17);self.assertEqual(inhibit_status(1,17,2,8),2)
        self.assertEqual(inhibit_status(2,17,2,8),8)
        for bit in range(5):
            for value in range(256):
                prior=31;values=[255]*5;values[bit]=value
                expected=prior&~(1<<bit) if value==0 else prior
                self.assertEqual(inhibit_write(prior,1<<(bit+2),values),expected)
                self.assertEqual(inhibit_write(prior,0,values),prior)
    def test_counter_retries_wrap(self):
        counter=0;state=0
        for _ in range(10):counter,state=counter_step(counter,state,True,1)
        self.assertEqual((counter,state),(10,1));self.assertEqual(ownership(1,watchdog=int(counter>=10)),0)
        self.assertEqual(counter_step(255,1,True,1),(0,1));self.assertEqual(counter_step(10,1,True,0),(0,0))
        for v in range(2,256):self.assertEqual(counter_step(8,1,True,v),(8,1))
        self.assertEqual(counter_step(8,1,False,0),(8,1))
    def test_demand_limits_and_readback(self):
        self.assertEqual(demand_selection(100,True,3,False,80,100),dict(stored=30,active=30,selected=30,get05_p5=3))
        self.assertEqual(demand_selection(100,True,3,True,80,100)['selected'],80)
        self.assertEqual(demand_selection(100,True,0,False,80,20)['selected'],20)
        for v in range(11,256):self.assertEqual(demand_selection(20,True,v,False,100,100)['stored'],100)
        self.assertEqual(demand_selection(20,False,0,False,100,100)['stored'],20)
        self.assertEqual(demand_selection(100,True,10,False,100,100)['get05_p5'],10)
    def test_target35_routing(self):
        p=bytearray(16);p[0]=0x35;p[1]=10;p[4:8]=bytes.fromhex('08020a03')
        before={(0,0):2000,(0,1):2100,(1,0):2200,(1,1):2300}
        for mode in (0,1):
            p[3]=mode;r=target35(p,0,before);self.assertEqual((r[(mode,0)],r[(mode,1)]),(2050,2563));self.assertEqual(r[(1-mode,0)],before[(1-mode,0)])
        self.assertEqual(target35(p,2,before),before)
        p[3]=2;self.assertEqual(target35(p,0,before),before)
        p[3]=0;p[1]=0;self.assertEqual(target35(p,0,before),before)
        p[1]=10;p[4:8]=b'\xff'*4;self.assertEqual(target35(p,0,before),before)
    def test_target32_mode_context(self):
        from controls import target32
        p=bytearray(16);p[0]=0x32;p[1]=128;p[2]=2;p[6]=1;p[7]=3;p[10:14]=bytes.fromhex('0dac0bb8')
        prior={(1,0):3300,(3,1):2500}
        self.assertEqual(target32(p,0,prior),{(1,0):3500,(3,1):3000})
        p[6]=2;self.assertEqual(target32(p,0,prior)[(1,0)],3300)
        p[6]=255;self.assertEqual(target32(p,0,prior)[(1,0)],3300)
        self.assertEqual(target32(p,2,prior),prior)
        p[1]=0;p[2]=0;self.assertEqual(target32(p,0,prior),prior)
        p[1]=128;p[6]=1;p[10:12]=b'\xff\xff';self.assertEqual(target32(p,0,prior),prior)

    def test_coupled_modes(self):
        from controls import coupled_modes
        table=json.loads((OUT/'evidence.json').read_text())['tables']['860cc']
        self.assertEqual(coupled_modes(0,0,(1,0),0,table),(0,1))
        self.assertEqual(coupled_modes(0,0,(1,0),1,table),(0,0))
        self.assertEqual(coupled_modes(1,255,(1,1),0,table),(1,1))
        for feature in (0,1):
            for a in range(5):
                for b in range(5):
                    result=coupled_modes(0,a,(0,b),feature,table)
                    self.assertTrue(all(0<=v<=5 for v in result))

    def test_temperature_boundaries(self):
        for signed,expected in [(-32768,0),(-4001,0),(-4000,0),(-3951,0),(-3950,1),(0,80),(8750,255),(32767,255)]:
            self.assertEqual(scaled_temperature(signed&65535),expected)
        for raw in range(65536):
            signed=raw if raw<32768 else raw-65536
            self.assertEqual(scaled_temperature(raw),max(0,min(255,int((signed+4000)/50))))
    def test_frame_rejection(self):
        p=bytes([0x28])+bytes(15);f=frame(0x62,p);self.assertEqual(parse(f,0x62,0x28),p)
        for i in range(len(f)):
            bad=bytearray(f);bad[i]^=1
            with self.assertRaises(ValueError):parse(bad,0x62,0x28)
        for n in range(len(f)):
            with self.assertRaises(ValueError):parse(f[:n],0x62,0x28)
        with self.assertRaises(ValueError):parse(frame(0x61,p),0x62,0x28)
        with self.assertRaises(ValueError):parse(f,0x62,0x26)
    def test_ack_not_application(self):
        self.assertEqual(parse(frame(0x61,bytes(16)),0x61),bytes(16))
        self.assertEqual(ownership(0,request=True,watchdog=1),0)
    def test_typed_a3(self):
        p=bytearray(16);p[0]=0xa3;p[2]=27;p[4:6]=bytes.fromhex('3412')
        for fmt in (0,1,2,3,4,6,7):
            p[3]=fmt;r=a3(frame(0x62,p),27);self.assertEqual(r['raw_le'],0x1234);self.assertEqual(r['format'],fmt)
        p[3]=5
        with self.assertRaises(ValueError):a3(frame(0x62,p),27)
        p[3]=1
        with self.assertRaises(ValueError):a3(frame(0x62,p),28)
    def test_read_exclusions(self):
        for n in [340,532,*range(520,532),1002]:
            with self.assertRaises(ValueError):plan_read(n)
        self.assertTrue(plan_read(27)['offline_only']);self.assertFalse(plan_read(27)['physical_ready'])
    def test_service_cache_ownership(self):
        s=ServiceObserver(27);s.request()
        for _ in range(12):s.reply(dict(selector=27,format=0))
        self.assertEqual(s.pending_polls,12);self.assertEqual(s.transport_failures,0)
        s.reply(dict(selector=27,format=2,raw_le=5));s.request();self.assertEqual(s.status,'cached-age-unknown')
        s.stale();self.assertEqual(s.status,'stale');s.cancel()
        with self.assertRaises(ValueError):s.reply(dict(selector=27,format=1))
    def test_read_close_synthetic(self):
        s=SettingsObserver(1,32)
        for event in ('open','peer1002_read','get','peer_end','read_finish','close','peer1002_close_read','close_reply'):s.event(event)
        self.assertEqual(s.state,0);self.assertFalse(s.applied)
        with self.assertRaises(ValueError):s.event('ack')
        with self.assertRaises(ValueError):SettingsObserver(1,6)
    def test_apply_timeout_not_rollback(self):
        s=SettingsObserver(0,32)
        for e in ('open','peer1002_write','stage','apply'):s.event(e)
        self.assertEqual(s.state,4);self.assertTrue(s.applied);s.persistence(False);s.event('timeout')
        self.assertEqual(s.state,0);self.assertTrue(s.applied);self.assertFalse(s.persisted)
        with self.assertRaises(ValueError):preserve_category(6,{'pump':5,'unknown':9},{'pump':True,'unknown':False},{'pump':4})
        with self.assertRaises(ValueError):preserve_category(6,{'pump':5},{'pump':True},{'pump':4})
    def test_artifacts(self):
        c,e,v=build(OUT);self.assertEqual(render(c),(OUT/'control-contracts.md').read_text())
        self.assertEqual(v,json.loads((OUT/'coverage.json').read_text()));self.assertEqual(len(c['backlog']),141)
    def test_missing_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d)
            for n in ('cn105-contracts.json','evidence.json'):(d/n).write_bytes((OUT/n).read_bytes())
            e=json.loads((d/'evidence.json').read_text());e['assembly_sha256'].pop('a5628');(d/'evidence.json').write_text(json.dumps(e))
            with self.assertRaises(ValueError):build(d)
    def test_wrong_image(self):
        with self.assertRaises(ValueError):image(bytes(0x80000))
        with self.assertRaises(ValueError):image(b'')
    def test_no_transport_imports(self):
        banned={'socket','requests','urllib','http','serial','subprocess'}
        for p in Path(__file__).parent.glob('*.py'):
            tree=ast.parse(p.read_text())
            for n in ast.walk(tree):
                if isinstance(n,ast.Import):self.assertFalse({x.name.split('.')[0] for x in n.names}&banned,p.name)
                if isinstance(n,ast.ImportFrom):self.assertNotIn((n.module or '').split('.')[0],banned,p.name)
@unittest.skipUnless(os.environ.get('P89_IMAGE') and os.environ.get('P89_PRIVATE'),'private inputs unavailable')
class Private(unittest.TestCase):
    def test_repeated_evidence(self):self.assertEqual(extract(os.environ['P89_IMAGE'],os.environ['P89_PRIVATE']),json.loads((OUT/'evidence.json').read_text()))
if __name__=='__main__':unittest.main()
