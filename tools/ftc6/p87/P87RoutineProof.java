// P0087 local ROM execution proof. Controlled synthetic RAM; no hardware access.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
public class P87RoutineProof extends GhidraScript {
 void put(EmulatorHelper e,int address,int value,int width)throws Exception{
  var n=currentProgram.getAddressFactory().getAddressSpace("near");
  byte[] bytes=new byte[width];for(int i=0;i<width;i++)bytes[i]=(byte)(value>>(8*i));
  e.writeMemory(n.getAddress(address),bytes);
 }
 int get(EmulatorHelper e,int address,int width)throws Exception{
  var n=currentProgram.getAddressFactory().getAddressSpace("near");int v=0;
  for(int i=0;i<width;i++)v|=(e.readMemoryByte(n.getAddress((address+i)&65535))&255)<<(8*i);
  return v;
 }
 int invoke(EmulatorHelper e,long entry)throws Exception{
  // Emulator-only JSR.a trampoline, same opcode as the original call at A1FDB.
  byte[] call=new byte[]{(byte)0xfd,(byte)entry,(byte)(entry>>8),(byte)(entry>>16)};
  e.writeMemory(toAddr(0x70000),call);
  e.writeRegister("PC",0x70000);e.writeRegister("SP",0x7000);e.writeRegister("FB",0);
  for(int steps=0;steps<200000;steps++){
   if(e.getExecutionAddress().getOffset()==0x70004){
    if(e.readRegister("SP").intValue()!=0x7000 || e.readRegister("FB").intValue()!=0)
     throw new Exception("Stack/frame restoration mismatch");
    return e.readRegister("R0").intValue()&65535;
   }
   // Documented EXITD workaround: module incorrectly ANDs return halves.
   long pc=e.getExecutionAddress().getOffset();
   if((e.readMemoryByte(toAddr(pc))&255)==0x7d && (e.readMemoryByte(toAddr(pc+1))&255)==0xf2){
    int sp=e.readRegister("FB").intValue()&65535;
    e.writeRegister("FB",get(e,sp,2));
    e.writeRegister("PC",get(e,(sp+2)&65535,3)&0xfffff);
    e.writeRegister("SP",(sp+5)&65535);continue;
   }
   // Signed5 byte displacement in bit,base:8[FB] (M16C60 addressing table).
   // The module zero-extends it. Adjust only the operand base for this step.
   int savedFB=e.readRegister("FB").intValue();
   boolean bitFB=(e.readMemoryByte(toAddr(pc))&255)==0x7e &&
       (e.readMemoryByte(toAddr(pc+1))&15)==11 &&
       (e.readMemoryByte(toAddr(pc+2))&128)!=0;
   if(bitFB)e.writeRegister("FB",(savedFB-32)&65535);
   if(!e.step(monitor))throw new Exception(e.getLastError()+" pc="+e.getExecutionAddress());
   if(bitFB)e.writeRegister("FB",savedFB);
  }
  throw new Exception("step bound at "+e.getExecutionAddress());
 }
 void check(String name,int actual,int expected)throws Exception{
  if(actual!=expected)throw new Exception(name+" actual="+actual+" expected="+expected);
  println("P87_ROM_PASS "+name+"="+actual);
 }
 void history(EmulatorHelper e,int enable,int error,int phase)throws Exception{
  e.writeRegister("R1",enable);put(e,0x7000,error,4);put(e,0x3d07,phase,1);
 }
 EmulatorHelper fresh()throws Exception{
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  e.writeMemory(currentProgram.getAddressFactory().getAddressSpace("near").getAddress(0),new byte[0x8000]);
  for(String r:new String[]{"R0","R1","R2","R3","A0","A1"})e.writeRegister(r,0);
  return e;
 }
 public void run()throws Exception{
  var source=getInstructionAt(toAddr(0xa1fdb));
  println("CALL_BYTES "+java.util.HexFormat.of().formatHex(source.getBytes()));
  for(int error:new int[]{-201,-200,-199,0,1,250,251}){
   EmulatorHelper e=fresh();
   try{
    put(e,0x3cb7,8,1);put(e,0x3a4f,0,1);put(e,0x0900,0,1);put(e,0x4911,0,1);
    put(e,0x3f6d,0,1);put(e,0x3a2c,0,1);put(e,0x3908,3500,2);put(e,0x0662,3500-error,2);
    int value=invoke(e,0xa1ed8);
    int expected=error<=-200?2900:error<=-150?2850:error<=0?2700:error<=50?2650:error<=250?2450:2400;
    check("lookup/"+error,value,expected);
   }finally{e.dispose();}
  }
  int[] temps={-1,0,1,49,50,51,8000,9000};
  int[] encoded={0,0,1,1,1,2,160,160};
  for(int i=0;i<temps.length;i++){
   EmulatorHelper e=fresh();
   try{e.writeRegister("R1",0);put(e,0x39ef,temps[i],2);check("target/"+temps[i],invoke(e,0x9a336)&255,encoded[i]);}
   finally{e.dispose();}
  }
  EmulatorHelper e=fresh();
  try{
   put(e,0x3e02,0,1);put(e,0x3e01,0,1);put(e,0x16d0,0,2);
   history(e,1,200,2);check("history70/equal200",invoke(e,0xac79a)&255,0);
   history(e,1,199,2);check("history70/enter",invoke(e,0xac79a)&255,1);
   history(e,1,199,0);check("history70/leave",invoke(e,0xac79a)&255,2);
   check("history70/start",get(e,0x16d0,2),0x8000);
   put(e,0x16d0,0x8000|599,2);history(e,1,999,0);
   check("history70/hold599",invoke(e,0xac79a)&255,2);
   put(e,0x16d0,0x8000|600,2);history(e,1,999,0);
   check("history70/expire600",invoke(e,0xac79a)&255,0);
   put(e,0x3e02,2,1);history(e,0,0,0);
   check("history70/disable",invoke(e,0xac79a)&255,0);
   check("history70/clear",get(e,0x16d0,2),0);
   put(e,0x16d2,0,2);put(e,0x3e05,0,1);put(e,0x4927,2,1);put(e,0x3da4,5,1);put(e,0x3944,6,1);
   history(e,1,201,0);check("history50/above200",invoke(e,0xac880)&255,0);
   history(e,1,200,0);check("history50/enter200",invoke(e,0xac880)&255,1);
   check("history50/start",get(e,0x16d2,2),0x8000);
   put(e,0x16d2,0x8000|179,2);history(e,1,999,0);
   check("history50/latched179",invoke(e,0xac880)&255,1);
   put(e,0x16d2,0x8000|180,2);history(e,1,999,0);
   check("history50/expire180",invoke(e,0xac880)&255,0);
   check("history50/clear",get(e,0x16d2,2),0);
   put(e,0x0600,70,1);put(e,0x3933,100,1);put(e,0x3934,50,1);
   invoke(e,0xac9a8);check("limit/min",get(e,0x05fe,1),50);
   check("limit/mirror",get(e,0x3935,1),50);
  }finally{e.dispose();}
  for(int cap:new int[]{0,10,30,50,70,100,255}){
   e=fresh();
   try{e.writeRegister("R1",0x10);put(e,0x05fe,cap,1);
    check("limit/encode/"+cap,invoke(e,0x99b8a),10-Math.min(10,cap/10));
   }finally{e.dispose();}
  }
  e=fresh();
  try{
   // Initialize every descriptor's timer to a known disabled word.
   for(int i=0;i<515;i++){
    int ptr=getInt(toAddr(0x8426c+4*i));
    int addr=getShort(toAddr(ptr))&65535;put(e,addr,0,2);
   }
   put(e,0x16d0,0x8000|599,2);put(e,0x7000,0,1);e.writeRegister("R1",1);
   invoke(e,0xa3298);check("timer/wrongmask",get(e,0x16d0,2),0x8000|599);
   put(e,0x7000,0,1);e.writeRegister("R1",2);
   invoke(e,0xa3298);check("timer/normal",get(e,0x16d0,2),0x8000|600);
   put(e,0x7000,1,1);e.writeRegister("R1",2);
   invoke(e,0xa3298);check("timer/accelerated",get(e,0x16d0,2),0x8000|660);
   put(e,0x16d0,0xfffe,2);put(e,0x7000,1,1);e.writeRegister("R1",2);
   invoke(e,0xa3298);check("timer/overflowguard",get(e,0x16d0,2),0xfffe);
  }finally{e.dispose();}
  for(int profile:new int[]{0,1,2}){
   e=fresh();
   try{
    put(e,0x0900,profile,1);put(e,0x3cb7,8,1);put(e,0x3a4f,0,1);
    put(e,0x3915,1,1);put(e,0x38bf,1,1);put(e,0x38c0,2,1);
    put(e,0x3908,3500,2);put(e,0x0662,3400,2);put(e,0x3947,100,2);
    put(e,0x3d97,1,1);put(e,0x3e01,0,1);put(e,0x3d07,2,1);
    check("fixed/profile"+profile+"/enter",invoke(e,0xac16c)&255,100);
    put(e,0x3d07,0,1);
    check("fixed/profile"+profile+"/leave",invoke(e,0xac16c)&255,profile==1?100:70);
    put(e,0x16d0,0x8000|600,2);
    check("fixed/profile"+profile+"/expire",invoke(e,0xac16c)&255,100);
   }finally{e.dispose();}
  }
  e=fresh();
  try{
   // Original C77B6: nonheating phase sets local return flag via bit7,-1[FB].
   put(e,0x3cb7,0,1);put(e,0x26f4,0,1);put(e,0x3a4f,0,1);
   check("bitfb/original_exit_flag",invoke(e,0xc77b6)&255,128);
   check("bitfb/no_positive_alias",get(e,0x701a,1),0);
  }finally{e.dispose();}
  println("P87_ROM_PROOF_COMPLETE");

 }
}
