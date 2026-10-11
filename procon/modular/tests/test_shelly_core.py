"""P0080 execute exact helper JS in Node with UART mock (not device proof)."""
import sys,json,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from shelly_ota import CORE
js="""
const vm=require('vm'),assert=require('assert');let receiver,timeout,sent=[],baud;
const ctx={UART:{get:()=>({recv:f=>receiver=f,configure:c=>baud=c.baud,send:b=>{sent.push(b);return b.length;}})},Timer:{set:(ms,repeat,f)=>timeout=f},Shelly:{call:()=>{}},atob:s=>Buffer.from(s,'base64').toString('binary'),btoa:s=>Buffer.from(s,'binary').toString('base64')};
vm.createContext(ctx);vm.runInContext(SOURCE,ctx);
assert.equal(vm.runInContext('baud(9600)',ctx),true);assert.equal(baud,9600);
let data=Buffer.alloc(252,0x57).toString('base64');assert.equal(vm.runInContext('stage('+JSON.stringify(data)+')',ctx),252);
assert.equal(vm.runInContext('send()',ctx),252);receiver('abc');assert.equal(vm.runInContext('result()',ctx),'YWJj');
assert.throws(()=>vm.runInContext('stage('+JSON.stringify(Buffer.alloc(253).toString('base64'))+')',ctx));
receiver('unexpected');assert.throws(()=>vm.runInContext('send()',ctx));timeout();assert.equal(baud,115200);
console.log('PASS exact Shelly helper JS: staging252, RX, bounds, unsolicited traffic gate, timer cleanup');
""".replace('SOURCE',json.dumps(CORE))
subprocess.run(['node','-e',js],check=True)
