// P0083 targeted local-only function/data-flow evidence. Full output is proprietary.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
public class P83Trace extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();File out=new File(args[0]);out.mkdirs();
  DecompInterface d=new DecompInterface();d.openProgram(currentProgram);
  TreeSet<Long> wanted=new TreeSet<>();
  for(String arg:args[1].split(","))wanted.add(Long.parseLong(arg,16));
  try(PrintWriter w=new PrintWriter(new File(out,"requested.tsv"))) {
   for(long v:wanted){
    Function f=getFunctionContaining(toAddr(v));if(f==null){w.println(Long.toHexString(v)+"\tNO_FUNCTION");continue;}
    String key=Long.toHexString(f.getEntryPoint().getOffset());w.println(Long.toHexString(v)+"\t"+key+"\t"+f.getBody());
    try(PrintWriter a=new PrintWriter(new File(out,key+".asm"))){
     var it=currentProgram.getListing().getInstructions(f.getBody(),true);while(it.hasNext()){Instruction i=it.next();a.println(i.getAddress()+"\t"+i);}
    }
    DecompileResults result=d.decompileFunction(f,30,monitor);
    try(PrintWriter c=new PrintWriter(new File(out,key+".c"))){c.println(result.decompileCompleted()?result.getDecompiledFunction().getC():result.getErrorMessage());}
    try(PrintWriter refs=new PrintWriter(new File(out,key+"-refs.tsv"))){
     var iter=currentProgram.getReferenceManager().getReferencesTo(f.getEntryPoint());while(iter.hasNext()){Reference r=iter.next();Function caller=getFunctionContaining(r.getFromAddress());refs.println(r.getFromAddress()+"\t"+r.getReferenceType()+"\t"+(caller==null?"UNKNOWN":caller.getEntryPoint()));}
    }
   }
  }
  try(PrintWriter w=new PrintWriter(new File(out,"instructions.tsv"));PrintWriter refs=new PrintWriter(new File(out,"references.tsv"))){
   for(Instruction i:currentProgram.getListing().getInstructions(true)){
    Function f=getFunctionContaining(i.getAddress());w.println(i.getAddress()+"\t"+i+"\t"+(f==null?"UNKNOWN":f.getEntryPoint()));
    for(Reference r:i.getReferencesFrom())refs.println(r.getFromAddress()+"\t"+r.getToAddress()+"\t"+r.getReferenceType()+"\t"+(f==null?"UNKNOWN":f.getEntryPoint()));
   }
  }
  d.dispose();println("TARGETED_EXPORT_COMPLETE");
 }
}
