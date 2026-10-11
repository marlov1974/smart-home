// P0088: bounded CFG export, independent of stale Ghidra function bodies.
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.Address;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
public class P88A3Completion extends GhidraScript {
 public void run() throws Exception {
  if(getScriptArgs().length<2||getScriptArgs().length>3)throw new Exception("output, reference binary, optional qualified routine required");
  String routine=getScriptArgs().length==3?getScriptArgs()[2]:"a3-completion";
  long start,end;
  if(routine.equals("a3-completion")){start=0xcecfa;end=0xced4a;}
  else if(routine.equals("settings-clock")){start=0x94a20;end=0x94a45;}
  else throw new Exception("unqualified routine");
  byte[] rom=Files.readAllBytes(Path.of(getScriptArgs()[1]));
  if(rom.length!=0x80000)throw new Exception("incomplete image");
  String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(rom));
  if(!sha.equals("d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a"))throw new Exception("wrong image");
  for(long a=start;a<end;a++)if(getByte(toAddr(a))!=rom[(int)a-0x80000])throw new Exception("project bytes differ");
  TreeMap<Long,String> lines=new TreeMap<>();ArrayDeque<Address> queue=new ArrayDeque<>();queue.add(toAddr(start));
  while(!queue.isEmpty()){
   Address at=queue.removeFirst();if(lines.containsKey(at.getOffset()))continue;
   if(at.getOffset()<start||at.getOffset()>=end)throw new Exception("unexpected function escape "+at);
   if(getInstructionAt(at)==null)new DisassembleCommand(at,null,true).applyTo(currentProgram,monitor);
   var i=getInstructionAt(at);if(i==null)throw new Exception("undecodable instruction "+at);
   lines.put(at.getOffset(),at+"\t"+i.toString());
   if(i.getFallThrough()!=null)queue.add(i.getFallThrough());
   if(!i.getFlowType().isCall())for(Address a:i.getFlows())queue.add(a);
  }
  Files.writeString(Path.of(getScriptArgs()[0]),String.join("\n",lines.values())+"\n");
  println("P88_CFG_COMPLETE routine="+routine+" instructions="+lines.size());
 }
}
