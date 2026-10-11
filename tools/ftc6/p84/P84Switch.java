// P0084: repair targeted relative switch flow; never access hardware.
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.SourceType;
public class P84Switch extends GhidraScript {
 public void run() throws Exception {
  // Table bounds and origin are checked against the dispatch operands manually.
  String[] a=getScriptArgs(); long owner=Long.parseLong(a[0],16),branch=Long.parseLong(a[1],16),table=Long.parseLong(a[2],16); int n=Integer.parseInt(a[3]);
  if(!((branch==0x9f315 && table==0x9f31a && n==25)||(branch==0xcf695 && table==0xcf69a && n==48)||(branch==0xa910a && table==0xa910f && n==48)))throw new Exception("unqualified switch bounds");
  for(int i=0;i<n;i++){
   long target=branch+(short)getShort(toAddr(table+2*i));
   if(target<0x80000||target>=0x100000)throw new Exception("target outside image");
   new DisassembleCommand(toAddr(target),null,true).applyTo(currentProgram,monitor);
   currentProgram.getReferenceManager().addMemoryReference(toAddr(branch),toAddr(target),RefType.COMPUTED_JUMP,SourceType.USER_DEFINED,0);
   println("SWITCH "+Long.toHexString(branch)+" index="+i+" target="+Long.toHexString(target));
  }
  var f=getFunctionAt(toAddr(owner));if(f==null)f=createFunction(toAddr(owner),null);
  if(f!=null)CreateFunctionCmd.fixupFunctionBody(currentProgram,f,monitor);
 }
}
