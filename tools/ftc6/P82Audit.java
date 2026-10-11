// P0082: offline decoder fixtures and bounded reference export. Outputs stay local.
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;

public class P82Audit extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();
  if(args[0].equals("fixture")) {
   long[] offsets={0,1,2,3};String[] names={"NOP","RTS","REIT","JMP.A"};int[] lengths={1,1,1,4};
   for(int n=0;n<4;n++) {
    Address a=toAddr(offsets[n]);new DisassembleCommand(a,null,false).applyTo(currentProgram,monitor);
    Instruction i=getInstructionAt(a);
    if(i==null||!i.getMnemonicString().equalsIgnoreCase(names[n])||i.getLength()!=lengths[n])throw new Exception("fixture failed "+n+" "+i);
    if(n==3 && !i.toString().toLowerCase().contains("0xd5540")) throw new Exception("operand mismatch");
    if(n==3) println("LIMITATION: absolute jump decoded as "+i+"; static flows="+i.getFlows().length);
    println("DECODE PASS "+i);
   }
   return;
  }
  AddressSet allowed=new AddressSet();
  for(var b:currentProgram.getMemory().getBlocks())if(b.isInitialized())allowed.add(b.getStart(),b.getEnd());
  for(long root:new long[]{0xd5540,0xa35de,0xd5662}){
   Address a=toAddr(root);new DisassembleCommand(a,allowed,true).applyTo(currentProgram,monitor);createFunction(a,"entry_"+Long.toHexString(root));
  }
  // Evidence: c9461 uses stride 0x15; c948b/c948f/c9493 call copied fields +5/+9/+17.
  // Image-specific table, not a heuristic sweep over arbitrary constants.
  for(int row=0;row<38;row++) for(int field:new int[]{5,9,17}) {
   long value=Integer.toUnsignedLong(currentProgram.getMemory().getInt(toAddr(0x87a60+row*21+field)));
   Address a=toAddr(value);
   if(value<=0xfffff && allowed.contains(a)) {
    new DisassembleCommand(a,allowed,true).applyTo(currentProgram,monitor);
    if(getFunctionAt(a)==null)createFunction(a,null);
   }
  }
  // Explicitly resolve only documented direct branch/call encodings encountered in code.
  // Upstream module models these as computed flows; do not trust its call graph alone.
  for(int pass=0;pass<12;pass++) {
   java.util.ArrayList<Address> targets=new java.util.ArrayList<>();
   for(Instruction i:currentProgram.getListing().getInstructions(true)) {
    byte[] b=i.getBytes();int op=b[0]&255;long target=-1;boolean call=false;
    if((op==0xfc||op==0xfd)&&b.length==4){target=(b[1]&255)|((b[2]&255)<<8)|((b[3]&15)<<16);call=op==0xfd;}
    else if((op==0xf4||op==0xf5)&&b.length==3){target=i.getAddress().getOffset()+1+(short)((b[1]&255)|((b[2]&255)<<8));call=op==0xf5;}
    else if(op==0xfe&&b.length==2)target=i.getAddress().getOffset()+1+b[1];
    else if((op&0xf8)==0x60&&b.length==1)target=i.getAddress().getOffset()+2+(op&7);
    if(target>=0&&allowed.contains(toAddr(target))) {
     Address a=toAddr(target);targets.add(a);
     currentProgram.getReferenceManager().addMemoryReference(i.getAddress(),a,call?RefType.UNCONDITIONAL_CALL:RefType.UNCONDITIONAL_JUMP,SourceType.USER_DEFINED,0);
     if(call&&getFunctionAt(a)==null){new DisassembleCommand(a,allowed,true).applyTo(currentProgram,monitor);createFunction(a,null);}
    }
   }
   int count=0;for(Address a:targets)if(getInstructionAt(a)==null){new DisassembleCommand(a,allowed,true).applyTo(currentProgram,monitor);count++;}
   if(count==0&&pass>0)break;
  }
  analyzeAll(currentProgram);
  File dir=new File(args[0]);dir.mkdirs();
  try(PrintWriter w=new PrintWriter(new File(dir,"instructions.tsv"))){
   for(Instruction i:currentProgram.getListing().getInstructions(true))w.println(i.getAddress()+"\t"+i+"\t"+i.getLength());
  }
  try(PrintWriter w=new PrintWriter(new File(dir,"functions.tsv"))){
   for(Function f:currentProgram.getFunctionManager().getFunctions(true)){
    w.println(f.getEntryPoint()+"\t"+f.getName()+"\t"+f.getBody().getNumAddresses());
   }
  }
  try(PrintWriter w=new PrintWriter(new File(dir,"references.tsv"))){
   for(Instruction i:currentProgram.getListing().getInstructions(true))for(Reference r:i.getReferencesFrom())w.println(r.getFromAddress()+"\t"+r.getToAddress()+"\t"+r.getReferenceType());
  }
  java.security.MessageDigest digest=java.security.MessageDigest.getInstance("SHA-256");
  long populated=0;
  for(var b:currentProgram.getMemory().getBlocks())if(b.isInitialized()) {
   for(long offset=b.getStart().getOffset();offset<=b.getEnd().getOffset();offset++) {
    digest.update(new byte[]{(byte)(offset>>>24),(byte)(offset>>>16),(byte)(offset>>>8),(byte)offset,currentProgram.getMemory().getByte(toAddr(offset))});populated++;
   }
  }
  String sparseHash=java.util.HexFormat.of().formatHex(digest.digest());
  try(PrintWriter w=new PrintWriter(new File(dir,"memory-validation.txt"))){w.println("populated="+populated);w.println("address_byte_sha256="+sparseHash);}
  println("AUDIT language="+currentProgram.getLanguageID()+" blocks="+currentProgram.getMemory().getBlocks().length+" functions="+currentProgram.getFunctionManager().getFunctionCount());
 }
}
