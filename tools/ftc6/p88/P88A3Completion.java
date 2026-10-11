// P0088: bounded CFG export, independent of stale Ghidra function bodies.
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.Address;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
public class P88A3Completion extends GhidraScript {
 public void run() throws Exception {
  if(getScriptArgs().length!=2)throw new Exception("private output file and reference binary required");
  byte[] rom=Files.readAllBytes(Path.of(getScriptArgs()[1]));
  if(rom.length!=0x80000)throw new Exception("incomplete image");
  String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(rom));
  if(!sha.equals("d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a"))throw new Exception("wrong image");
  for(long a=0xcecfa;a<0xced4a;a++)if(getByte(toAddr(a))!=rom[(int)a-0x80000])throw new Exception("project bytes differ");
  TreeMap<Long,String> lines=new TreeMap<>();ArrayDeque<Address> queue=new ArrayDeque<>();queue.add(toAddr(0xcecfa));
  while(!queue.isEmpty()){
   Address at=queue.removeFirst();if(lines.containsKey(at.getOffset()))continue;
   if(at.getOffset()<0xcecfa||at.getOffset()>=0xced4a)throw new Exception("unexpected function escape "+at);
   if(getInstructionAt(at)==null)new DisassembleCommand(at,null,true).applyTo(currentProgram,monitor);
   var i=getInstructionAt(at);if(i==null)throw new Exception("undecodable instruction "+at);
   lines.put(at.getOffset(),at+"\t"+i.toString());
   if(i.getFallThrough()!=null)queue.add(i.getFallThrough());
   if(!i.getFlowType().isCall())for(Address a:i.getFlows())queue.add(a);
  }
  Files.writeString(Path.of(getScriptArgs()[0]),String.join("\n",lines.values())+"\n");
  println("P88_A3_CFG_COMPLETE instructions="+lines.size());
 }
}
