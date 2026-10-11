// P0083: synthetic M16C decoding and direct-flow qualification, no vendor data.
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.listing.Instruction;
import ghidra.app.emulator.EmulatorHelper;
public class P83Vectors extends GhidraScript {
 public void run() throws Exception {
  String[] names={"NOP","RTS","REIT","JMP.A","JSR.a","JMP.b","JMP.b","JMP.w","JSR.w","JMP.s","LDE.w"};
  int[] lengths={1,1,1,4,4,2,2,3,3,1,5};
  long[] targets={-1,-1,-1,0xd5540,0xd5540,0xa5,0xbd,0xe5,0xfd,0x125,-1};
  for(int k=0;k<names.length;k++) {
   var a=toAddr(k*32);new DisassembleCommand(a,null,false).applyTo(currentProgram,monitor);Instruction i=getInstructionAt(a);
   if(i==null||!i.getMnemonicString().equalsIgnoreCase(names[k])||i.getLength()!=lengths[k])throw new Exception("decode failure case "+k+" "+i);
   if(targets[k]>=0&&(i.getFlows().length!=1||i.getFlows()[0].getOffset()!=targets[k]))throw new Exception("flow failure "+k+" "+i);
   if((k==4||k==8)&&!i.getFlowType().isCall())throw new Exception("call category failure");
   if(k==10&&!i.toString().contains("0x81234"))throw new Exception("far address failure "+i);
   println("PASS case="+k+" instruction="+i+" flow="+i.getFlowType());
  }
  int[] counts={6,3,-1,-8}; int[] inputs={0x8123,0x1234,0x8001,0xabcd,0};
  for(int k=0;k<counts.length;k++)for(int value:inputs){
   int n=counts[k], expected=n>0?((value<<n)|(value>>>(16-n)))&65535:((value>>>(-n))|(value<<(16+n)))&65535;
   int carry=n>0?(value>>>(16-n))&1:(value>>>(-n-1))&1;
   EmulatorHelper emu=new EmulatorHelper(currentProgram);
   try {
    emu.writeRegister("PC",0x160+k*32);emu.writeRegister("A0",value);
    if(!emu.step(monitor))throw new Exception("emulator failure "+emu.getLastError());
    if(emu.readRegister("A0").intValue()!=expected||emu.readRegister("Cflg").intValue()!=carry||emu.readRegister("Sflg").intValue()!=((expected>>>15)&1)||emu.readRegister("Zflg").intValue()!=(expected==0?1:0))throw new Exception("rotate mismatch n="+n+" value="+value);
    println("PASS ROT n="+n+" input="+value+" output="+expected+" carry="+carry);
   } finally {emu.dispose();}
  }
 }
}
