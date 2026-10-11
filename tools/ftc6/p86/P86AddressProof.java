// P0086: emulate reviewed near load; no program/device mutation.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.util.Arrays;
public class P86AddressProof extends GhidraScript {
 public void run() throws Exception {
  var ins=getInstructionAt(toAddr(0x9e99c));
  if(ins==null || !ins.toString().equals("MOV.b [A0],0x1348[A1]") || !Arrays.equals(ins.getBytes(),new byte[]{0x72,0x6d,0x48,0x13}))throw new Exception("Unqualified load");
  var near=currentProgram.getAddressFactory().getAddressSpace("near");
  long[] addresses={0x400,0xfffe,0xffff,0x10000,0x10001,0x80000,0x80400,0xffffe};
  for(long logical:addresses){
   EmulatorHelper e=new EmulatorHelper(currentProgram);
   try{
    e.writeRegister("PC",0x9e99c);e.writeRegister("A0",logical&65535);e.writeRegister("A1",0);e.writeRegister("R2",logical>>>16);
    e.writeMemory(near.getAddress(logical&65535),new byte[]{0x5a});
    if(!e.step(monitor))throw new Exception(e.getLastError());
    if(e.readMemoryByte(near.getAddress(0x1348))!=(byte)0x5a)throw new Exception("Load failed "+Long.toHexString(logical));
    println("P86_ADDRESS_PASS logical="+Long.toHexString(logical)+" effective="+Long.toHexString(logical&65535));
   } finally {e.dispose();}
  }
 }
}
