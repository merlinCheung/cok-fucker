// Decompile matched functions, following IFUNC/PLT thunks to the real body.
//
// SFS2X symbols in libgame.so are GNU IFUNC-style exports: the symbol address
// holds a resolver, and Ghidra renders the body as
//   (*(code *)PTR__<sym>_<hexaddr>)();
// We read the 8-byte pointer at <hexaddr> and decompile the real target.
//
// usage: analyzeHeadless <proj> <name> -process <file> -noanalysis \
//          -postScript DecompileTargets.java <outfile> <match1> [match2 ...]
//@category Analysis
//@author REA

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.mem.Memory;

public class DecompileTargets extends GhidraScript {

    private static final Pattern THUNK = Pattern.compile(
        "PTR_[A-Za-z0-9_]*?_([0-9a-fA-F]{6,16})\\)");

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            println("usage: DecompileTargets <outfile> <match1> [match2 ...]");
            return;
        }
        File out = new File(args[0]);
        PrintWriter w = new PrintWriter(new FileWriter(out));

        DecompInterface ifc = new DecompInterface();
        ifc.openProgram(currentProgram);
        ifc.toggleCCode(true);
        ifc.setSimplificationStyle("decompile");

        List<String> wanted = new ArrayList<>();
        for (int i = 1; i < args.length; i++) {
            wanted.add(args[i]);
        }

        Memory mem = currentProgram.getMemory();

        FunctionIterator fit = currentProgram.getFunctionManager().getFunctions(true);
        int hit = 0;
        int thunked = 0;
        Set<String> done = new HashSet<>();

        while (fit.hasNext() && !monitor.isCancelled()) {
            Function f = fit.next();
            String name = f.getName();
            boolean match = false;
            for (String wnt : wanted) {
                if (wnt.startsWith("0x") || wnt.startsWith("0X")) {
                    // Explicit address selector: decompile the function living there.
                    try {
                        Address a = currentProgram.getAddressFactory()
                                .getDefaultAddressSpace().getAddress(wnt.substring(2));
                        Function af = currentProgram.getFunctionManager().getFunctionAt(a);
                        if (af != null && f.getEntryPoint().equals(a)) {
                            match = true;
                        }
                    } catch (Exception ignore) {
                    }
                    continue;
                }
                if (name.contains(wnt)) {
                    match = true;
                    break;
                }
            }
            if (!match) {
                continue;
            }
            hit++;
            String body = decompile(ifc, f, mem);
            if (body == null) {
                continue;
            }
            if (body.contains("PTR_") && body.contains("(*(code *)")) {
                // Thunk: follow the pointer to the real implementation.
                String target = resolveThunk(body, mem);
                if (target != null && !done.contains(target)) {
                    done.add(target);
                    thunked++;
                    Function real = currentProgram.getFunctionManager()
                            .getFunctionAt(currentProgram.getAddressFactory()
                                    .getDefaultAddressSpace().getAddress(target));
                    if (real != null) {
                        String rbody = decompile(ifc, real, mem);
                        if (rbody != null) {
                            body = rbody;
                            name = name + "  [thunk -> " + target + "]";
                        }
                    }
                }
            }
            w.println("================================================================");
            w.println("// FUNCTION: " + name);
            w.println("// ADDRESS : " + f.getEntryPoint());
            w.println("================================================================");
            w.println(body);
            w.println();
            w.flush();
        }
        w.println("// matched functions: " + hit + " | thunk-resolved: " + thunked);
        w.flush();
        w.close();
        ifc.dispose();
        println("DecompileTargets -> " + out.getAbsolutePath()
                + " (matched " + hit + ", thunk-resolved " + thunked + ")");
    }

    private String decompile(DecompInterface ifc, Function f, Memory mem) {
        try {
            DecompileResults res = ifc.decompileFunction(f, 180, monitor);
            if (res != null && res.decompileCompleted()) {
                return res.getDecompiledFunction().getC();
            }
            if (res != null && res.getErrorMessage() != null) {
                return "// decompile error: " + res.getErrorMessage();
            }
        } catch (Exception e) {
            return "// exception: " + e;
        }
        return null;
    }

    /** Read the function pointer stored at the address named in a PTR_ thunk. */
    private String resolveThunk(String body, Memory mem) {
        Matcher m = THUNK.matcher(body);
        if (!m.find()) {
            return null;
        }
        String hex = m.group(1);
        try {
            Address ptrAddr = currentProgram.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(hex);
            byte[] buf = new byte[8];
            mem.getBytes(ptrAddr, buf);
            long v = 0;
            for (int i = 7; i >= 0; i--) {
                v = (v << 8) | (buf[i] & 0xffL);
            }
            if (v == 0) {
                return null;
            }
            return "0x" + Long.toHexString(v);
        } catch (Exception e) {
            return null;
        }
    }
}
