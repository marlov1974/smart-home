// P88: qualified source-link switch and per-entry CFG operand export, private only.
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.Address;
import java.nio.file.*;
import java.util.*;
public class P88SourceSwitch extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();if(args.length<1||args.length>2)throw new Exception("private output directory and optional tx selector required");
  Path dir=Path.of(args[0]);Files.createDirectories(dir);
  boolean tx=args.length==2 && args[1].equals("tx");
  if(args.length==2&&!tx)throw new Exception("unknown switch");
  long branch=tx?0x9bc57:0x9cd67,base=tx?0x9bc5c:0x9cd6c;
  int count=tx?23:16;
  // 9CD5D CMP.b10 then clamp-to0F, branch9CD67, relative table9CD6C:16 entries.
  for(int n=0;n<count;n++){
   long target=branch+(short)getShort(toAddr(base+2*n));
   if(target<(tx?0x9bc8a:0x9cd8c)||target>=(tx?0x9be98:0x9cfd2))throw new Exception("unqualified switch destination");
   new DisassembleCommand(toAddr(target),null,true).applyTo(currentProgram,monitor);
   TreeMap<Long,String> lines=new TreeMap<>();ArrayDeque<Address> queue=new ArrayDeque<>();queue.add(toAddr(target));
   while(!queue.isEmpty()){
    Address at=queue.removeFirst();if(lines.containsKey(at.getOffset()))continue;
    var i=getInstructionAt(at);if(i==null)throw new Exception("missing instruction "+at);
    if(lines.size()>1500)throw new Exception("CFG bound exceeded");
    lines.put(at.getOffset(),at+"\t"+i.toString());
    if(i.getFallThrough()!=null)queue.add(i.getFallThrough());
    if(!i.getFlowType().isCall())for(Address a:i.getFlows())queue.add(a);
   }
   Files.writeString(dir.resolve(String.format("branch-%02d.asm",n)),String.join("\n",lines.values())+"\n");
  }
  println("P88_SOURCE_SWITCH_COMPLETE");
 }
}
