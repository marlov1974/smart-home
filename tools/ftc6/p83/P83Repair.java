// Repair only verified ROT.w gaps in a local copy of P0082's project.
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
public class P83Repair extends GhidraScript {
 public void run() throws Exception {
  for(long gap:new long[]{0x8be27,0x9b038}) {
   var f=getFunctionContaining(toAddr(gap-1));
   new DisassembleCommand(toAddr(gap),null,true).applyTo(currentProgram,monitor);
   if(f!=null)CreateFunctionCmd.fixupFunctionBody(currentProgram,f,monitor);
   println("REPAIRED "+Long.toHexString(gap)+" "+getInstructionAt(toAddr(gap)));
  }
 }
}
