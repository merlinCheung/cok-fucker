#!/usr/bin/env bash
# Detached Ghidra headless decompile of COK libgame.so protocol functions.
# Runs fully outside the agent task lifetime (nohup + setsid), so the 1-hour
# background-task cap does not kill the analysis.
set -u

OUT="$HOME/workspace/me/local/apk/COK-CN1-analysis"
GH="/Users/a1234/Applications/ghidra_12.1.4_PUBLIC"
export GHIDRA_INSTALL_DIR="$GH"
export JAVA_HOME="/Users/a1234/Library/Java/JavaVirtualMachines/ms-21.0.10/Contents/Home"
unset _JAVA_OPTIONS JAVA_TOOL_OPTIONS JDK_JAVA_OPTIONS

mkdir -p "$OUT/ghidra-project"
cd "$OUT"

nohup "$GH/support/analyzeHeadless" "$OUT/ghidra-project" COK \
  -import "$OUT/apk-extract/lib/arm64-v8a/libgame.so" \
  -overwrite \
  -postScript "$OUT/scripts/DecompileTargets.java" "$OUT/native/libgame-decompiled.c" \
     "DefaultPacketEncrypter" "CryptoKey" "PacketHeader" "SFSProtocolCodec" \
     "SFSIOHandler" "FnHandshake" "BlowFishDecrypt" "HandshakeRequest" \
     "LoginRequest" "ExtensionRequest" "GenericMessageRequest" \
  -scriptPath "$OUT/scripts" \
  > "$OUT/native/ghidra-run.log" 2>&1 &

echo "PID=$!"
echo "LOG=$OUT/native/ghidra-run.log"
