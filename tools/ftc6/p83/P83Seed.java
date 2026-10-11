// Explicit table-backed targets only; run against local research project.
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import java.util.*;
public class P83Seed extends GhidraScript {
 public void run() throws Exception {
  ArrayDeque<long[]> queue=new ArrayDeque<>();HashSet<Long> seen=new HashSet<>();
  int depth=getScriptArgs().length>1?Integer.parseInt(getScriptArgs()[1]):0;
  for(String arg:getScriptArgs()[0].split(","))queue.add(new long[]{Long.parseLong(arg,16),depth});
  while(!queue.isEmpty()){
   long[] item=queue.remove();if(!seen.add(item[0]))continue;
   var a=toAddr(item[0]);
   new DisassembleCommand(a,null,true).applyTo(currentProgram,monitor);
   if(getFunctionAt(a)==null)createFunction(a,null);
   println("SEEDED "+a+" "+getInstructionAt(a));
   var f=getFunctionAt(a);
   if(item[1]>0&&f!=null)for(var i:currentProgram.getListing().getInstructions(f.getBody(),true))
    if(i.getFlowType().isCall())for(var t:i.getFlows())
     if(t.getOffset()>=0x80000&&t.getOffset()<0x100000)queue.add(new long[]{t.getOffset(),item[1]-1});
  }
 }
}
