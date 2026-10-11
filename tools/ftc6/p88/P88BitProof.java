// P0088 synthetic single-instruction semantics. Never touches hardware.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
public class P88BitProof extends GhidraScript {
 int cases=0;
 void check(byte[] code,String reg,int value,int target,int bit)throws Exception{
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  var near=currentProgram.getAddressFactory().getAddressSpace("near");
  try{
   e.writeMemory(toAddr(0x70000),code);e.writeRegister("PC",0x70000);
   e.writeRegister("FB",0x6000);e.writeRegister("SB",0x4000);e.writeRegister(reg,value);
   // Guard the complete near space: a wrong address must also fail.
   byte[] zero=new byte[65536];e.writeMemory(near.getAddress(0),zero);
   if(!e.step(monitor))throw new Exception(e.getLastError());
   byte[] after=e.readMemory(near.getAddress(0),65536);
   for(int i=0;i<65536;i++)if((after[i]&255)!=(i==target?1<<bit:0))
    throw new Exception("case="+cases+" reg="+reg+" target="+Integer.toHexString(target)+" unexpected="+Integer.toHexString(i));
   cases++;
  }finally{e.dispose();}
 }
 public void run()throws Exception{
  for(int disp=-16;disp<=15;disp++)for(int bit=0;bit<8;bit++)
   check(new byte[]{0x7e,(byte)0x9b,(byte)((disp&31)*8+bit)},"FB",0x6000,(0x6000+disp)&65535,bit);
  for(int reg=0;reg<2;reg++)for(int index:new int[]{0,1,3,4,7,8,15,255,256,65535}){
   check(new byte[]{0x7e,(byte)(0x96+reg)},"A"+reg,index,index>>3,index&7);
   for(int base:new int[]{0,1,127,255})
    check(new byte[]{0x7e,(byte)(0x98+reg),(byte)base},"A"+reg,index,(base+(index>>3))&65535,index&7);
   for(int base:new int[]{0,0x1367,0x3acf,0xffff})
    check(new byte[]{0x7e,(byte)(0x9c+reg),(byte)base,(byte)(base>>8)},"A"+reg,index,(base+(index>>3))&65535,index&7);
  }
  for(int base:new int[]{0,1,255,8191})for(int bit=0;bit<8;bit++){
   int packed=base*8+bit;
   check(new byte[]{0x7e,(byte)0x9e,(byte)packed,(byte)(packed>>8)},"SB",0xff00,(0xff00+base)&65535,bit);
  }
  println("P88_BIT_PROOF_PASS cases="+cases+" language="+currentProgram.getLanguageID());
 }
}
