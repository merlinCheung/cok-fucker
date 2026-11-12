#!/usr/bin/env python3
"""dex 反汇编器(够用版): 把指定类的 dalvik 指令列成可读清单。

为什么要自己写: 机器上没有 apktool/jadx/baksmali, 而读 elex 账号服务的
签名算法 / RSA 加密必须看字节码。

支持:
  * 解析 dex 头 → string/type/proto/field/method/class_defs
  * 解 class_data_item(静态/实例字段 + 直接/虚方法)
  * 解 code_item(寄存器数 + 指令流)
  * 解码常用 dalvik 指令格式(10x..35c/3rc/45cc 等), 把 const-string /
    invoke / sget / new-instance / 跳转目标 都解析成可读符号

用法:
    python3 dexdis.py <dex> <类名正则> [方法名正则]
    python3 dexdis.py apktool/classes.dex "elex/account/client"
    python3 dexdis.py apktool/classes.dex "elex/account/client" "NetUtil"

类名正则匹配的是内部名(斜杠形式), 例如 Lcom/elex/account/client/AccountNetUtil;
输出时会同时显示点号形式, 方便对照。
"""
import re
import struct
import sys

# ---------------------------------------------------------------- 指令格式表
# opcode -> (格式名, 指令长度(代码单元))
OPCODES = {}


def _op(code, fmt, size, name):
    OPCODES[code] = (fmt, size, name)


# 0x00-0x0d
for c, n in ((0x00, "nop"), (0x01, "move"), (0x02, "move/from16"), (0x03, "move/16"),
             (0x04, "move-wide"), (0x05, "move-wide/from16"), (0x06, "move-wide/16"),
             (0x07, "move-object"), (0x08, "move-object/from16"), (0x09, "move-object/16"),
             (0x0a, "move-result"), (0x0b, "move-result-wide"), (0x0c, "move-result-object"),
             (0x0d, "move-exception")):
    _op(c, {0x01: "12x", 0x04: "12x", 0x07: "12x", 0x02: "22x", 0x05: "22x", 0x08: "22x",
            0x03: "32x", 0x06: "32x", 0x09: "32x"}.get(c, "10x"), 1, n)
_op(0x0e, "10x", 1, "return-void")
for c, n in ((0x0f, "return"), (0x10, "return-wide"), (0x11, "return-object")):
    _op(c, "11x", 1, n)
_op(0x12, "11n", 1, "const/4")
_op(0x13, "21s", 2, "const/16")
_op(0x14, "31i", 3, "const")
_op(0x15, "21h", 2, "const/high16")
_op(0x16, "21s", 2, "const-wide/16")
_op(0x17, "31i", 3, "const-wide/32")
_op(0x18, "51l", 5, "const-wide")
_op(0x19, "21h", 2, "const-wide/high16")
_op(0x1a, "21c", 2, "const-string")
_op(0x1b, "31c", 3, "const-string/jumbo")
_op(0x1c, "21c", 2, "const-class")
_op(0x1d, "11x", 1, "monitor-enter")
_op(0x1e, "11x", 1, "monitor-exit")
_op(0x1f, "21c", 2, "check-cast")
_op(0x20, "22c", 2, "instance-of")
_op(0x21, "12x", 1, "array-length")
_op(0x22, "21c", 2, "new-instance")
_op(0x23, "22c", 2, "new-array")
_op(0x24, "35c", 3, "filled-new-array")
_op(0x25, "3rc", 3, "filled-new-array/range")
_op(0x26, "31t", 3, "fill-array-data")
_op(0x27, "11x", 1, "throw")
_op(0x28, "10t", 1, "goto")
_op(0x29, "20t", 2, "goto/16")
_op(0x2a, "30t", 3, "goto/32")
_op(0x2b, "31t", 3, "packed-switch")
_op(0x2c, "31t", 3, "sparse-switch")
for c, n in ((0x2d, "cmpl-float"), (0x2e, "cmpg-float"), (0x2f, "cmpl-double"),
             (0x30, "cmpg-double"), (0x31, "cmp-long")):
    _op(c, "23x", 2, n)
for c, n in ((0x32, "if-eq"), (0x33, "if-ne"), (0x34, "if-lt"), (0x35, "if-ge"),
             (0x36, "if-gt"), (0x37, "if-le")):
    _op(c, "22t", 2, n)
for c, n in ((0x38, "if-eqz"), (0x39, "if-nez"), (0x3a, "if-ltz"), (0x3b, "if-gez"),
             (0x3c, "if-gtz"), (0x3d, "if-lez")):
    _op(c, "21t", 2, n)
for c in range(0x3e, 0x44):
    _op(c, "10x", 1, "unused-%02x" % c)
for c, n in ((0x44, "aget"), (0x45, "aget-wide"), (0x46, "aget-object"), (0x47, "aget-boolean"),
             (0x48, "aget-byte"), (0x49, "aget-char"), (0x4a, "aget-short"),
             (0x4b, "aput"), (0x4c, "aput-wide"), (0x4d, "aput-object"), (0x4e, "aput-boolean"),
             (0x4f, "aput-byte"), (0x50, "aput-char"), (0x51, "aput-short")):
    _op(c, "23x", 2, n)
for c in range(0x52, 0x6e):
    _op(c, "22c", 2, {0x52: "iget", 0x53: "iget-wide", 0x54: "iget-object", 0x55: "iget-boolean",
                      0x56: "iget-byte", 0x57: "iget-char", 0x58: "iget-short",
                      0x59: "iput", 0x5a: "iput-wide", 0x5b: "iput-object", 0x5c: "iput-boolean",
                      0x5d: "iput-byte", 0x5e: "iput-char", 0x5f: "iput-short",
                      0x60: "sget", 0x61: "sget-wide", 0x62: "sget-object", 0x63: "sget-boolean",
                      0x64: "sget-byte", 0x65: "sget-char", 0x66: "sget-short",
                      0x67: "sput", 0x68: "sput-wide", 0x69: "sput-object", 0x6a: "sput-boolean",
                      0x6b: "sput-byte", 0x6c: "sput-char", 0x6d: "sput-short"}.get(c, "field"))
for c in range(0x6e, 0x73):
    _op(c, "35c", 3, "invoke")
_op(0x73, "10x", 1, "unused-73")
for c in range(0x74, 0x79):
    _op(c, "3rc", 3, "invoke/range")
_op(0x79, "10x", 1, "unused-79")
_op(0x7a, "10x", 1, "unused-7a")
for c in range(0x7b, 0x90):
    _op(c, "12x", 1, "unary-%02x" % c)
for c in range(0x90, 0xb0):
    _op(c, "23x", 2, "binop-%02x" % c)
for c in range(0xb0, 0xd0):
    _op(c, "12x", 1, "binop2-%02x" % c)
for c in range(0xd0, 0xd8):
    _op(c, "22s", 2, "binop-lit16-%02x" % c)
for c in range(0xd8, 0xe3):
    _op(c, "22b", 2, "binop-lit8-%02x" % c)
_op(0xfa, "45cc", 4, "invoke-polymorphic")
_op(0xfb, "4rcc", 4, "invoke-polymorphic/range")
_op(0xfc, "35c", 3, "invoke-custom")
_op(0xfd, "3rc", 3, "invoke-custom/range")
_op(0xfe, "21c", 2, "const-method-handle")
_op(0xff, "21c", 2, "const-method-type")


def uleb(buf, off):
    result = 0
    shift = 0
    while True:
        b = buf[off]
        off += 1
        result |= (b & 0x7F) << shift
        if not b & 0x80:
            break
        shift += 7
    return result, off


def sleb(buf, off):
    result = 0
    shift = 0
    while True:
        b = buf[off]
        off += 1
        result |= (b & 0x7F) << shift
        shift += 7
        if not b & 0x80:
            break
    if shift < 64 and (b & 0x40):
        result |= -(1 << shift)
    return result, off


class Dex(object):
    def __init__(self, path):
        self.buf = open(path, "rb").read()
        b = self.buf
        if b[:4] != b"dex\n":
            raise SystemExit("不是 dex 文件")
        u32 = lambda o: struct.unpack_from("<I", b, o)[0]
        u16 = lambda o: struct.unpack_from("<H", b, o)[0]
        self.n_str, self.off_str = u32(0x38), u32(0x3C)
        self.n_type, self.off_type = u32(0x40), u32(0x44)
        self.n_proto, self.off_proto = u32(0x48), u32(0x4C)
        self.n_field, self.off_field = u32(0x50), u32(0x54)
        self.n_meth, self.off_meth = u32(0x58), u32(0x5C)
        self.n_cls, self.off_cls = u32(0x60), u32(0x64)

    def string(self, idx):
        data_off = struct.unpack_from("<I", self.buf, self.off_str + 4 * idx)[0]
        _, off = uleb(self.buf, data_off)
        end = self.buf.find(b"\x00", off)
        return self.buf[off:end].decode("utf-8", "replace")

    def type(self, idx):
        return self.string(struct.unpack_from("<I", self.buf, self.off_type + 4 * idx)[0])

    def proto(self, idx):
        o = self.off_proto + 12 * idx
        shorty, ret, params = struct.unpack_from("<III", self.buf, o)
        p = []
        if params:
            # params 直接就是 type_list 的偏移(不是再套一层指针)
            n = struct.unpack_from("<I", self.buf, params)[0]
            for i in range(n):
                t = struct.unpack_from("<H", self.buf, params + 4 + 2 * i)[0]
                p.append(self.type(t))
        return self.type(ret), p

    def field(self, idx):
        o = self.off_field + 8 * idx
        cls, typ, name = struct.unpack_from("<HHI", self.buf, o)
        return self.type(cls), self.type(typ), self.string(name)

    def method(self, idx):
        o = self.off_meth + 8 * idx
        cls, proto, name = struct.unpack_from("<HHI", self.buf, o)
        ret, args = self.proto(proto)
        return self.type(cls), self.string(name), args, ret

    def static_values(self, static_off, static_fields):
        """解 class_def 的 static_values(encoded_array) -> {字段名: 值}。"""
        if not static_off:
            return {}
        b = self.buf
        off = static_off
        size, off = uleb(b, off)
        out = {}
        for i in range(size):
            val, off = self._encoded_value(off)
            if i < len(static_fields):
                _, _, fn = self.field(static_fields[i][0])
                out[fn] = val
        return out

    def _encoded_value(self, off):
        b = self.buf
        head = b[off]
        off += 1
        vtype = head & 0x1F
        varg = head >> 5
        if vtype == 0x1E:                     # NULL
            return None, off
        if vtype == 0x1F:                     # BOOLEAN
            return bool(varg), off
        if vtype == 0x17:                     # STRING
            raw = b[off:off + varg * 2]
            off += varg * 2
            return raw.decode("utf-16-le", "replace"), off
        if vtype == 0x1C:                     # ARRAY
            n, off = uleb(b, off)
            arr = []
            for _ in range(n):
                v, off = self._encoded_value(off)
                arr.append(v)
            return arr, off
        sizes = {0x00: 1, 0x02: 2, 0x03: 2, 0x04: 4, 0x06: 8, 0x10: 4, 0x11: 8,
                 0x15: 2, 0x16: 2, 0x18: 2, 0x19: 2, 0x1A: 2, 0x1B: 2}
        size = sizes.get(vtype, 0)
        if not size:
            return "<type 0x%x>" % vtype, off
        raw = b[off:off + size]
        off += size
        return int.from_bytes(raw, "little", signed=True), off

    def classes(self):
        for i in range(self.n_cls):
            o = self.off_cls + 32 * i
            (cls_idx, access, super_idx, ifaces_off, src_idx, ann_off,
             data_off, static_off) = struct.unpack_from("<IIIIIIII", self.buf, o)
            yield self.type(cls_idx), access, data_off, static_off

    def class_data(self, data_off):
        """返回 (static_fields, instance_fields, methods)。"""
        if not data_off:
            return [], [], []
        off = data_off
        n_sf, off = uleb(self.buf, off)
        n_if, off = uleb(self.buf, off)
        n_dm, off = uleb(self.buf, off)
        n_vm, off = uleb(self.buf, off)
        static, inst, meths = [], [], []
        idx = 0
        for _ in range(n_sf):
            d, off = uleb(self.buf, off)
            fl, off = uleb(self.buf, off)
            idx += d
            static.append((idx, fl))
        idx = 0
        for _ in range(n_if):
            d, off = uleb(self.buf, off)
            fl, off = uleb(self.buf, off)
            idx += d
            inst.append((idx, fl))
        idx = 0
        for group, count in (("direct", n_dm), ("virtual", n_vm)):
            idx = 0
            for _ in range(count):
                d, off = uleb(self.buf, off)
                flags, off = uleb(self.buf, off)
                code_off, off = uleb(self.buf, off)
                idx += d
                meths.append((idx, flags, code_off, group))
        return static, inst, meths

    def code_item(self, code_off):
        b = self.buf
        regs, ins, outs, tries = struct.unpack_from("<HHHH", b, code_off)
        insns_size = struct.unpack_from("<I", b, code_off + 12)[0]
        insns = struct.unpack_from("<%dH" % insns_size, b, code_off + 16)
        return regs, ins, outs, insns


def _s8(v):
    return v - 0x100 if v & 0x80 else v


def _s16(v):
    return v - 0x10000 if v & 0x8000 else v


def _s32(v):
    return v - 0x100000000 if v & 0x80000000 else v


def decode_method(dx, meth_idx, flags, code_off):
    cls, name, args, ret = dx.method(meth_idx)
    if not code_off:
        return None
    regs, ins, outs, insns = dx.code_item(code_off)
    lines = []
    i = 0
    n = len(insns)
    while i < n:
        unit = insns[i]
        op = unit & 0xFF
        fmt, size, nm = OPCODES.get(op, ("10x", 1, "unknown-%02x" % op))
        raw = insns[i:i + size]
        text = ""
        try:
            if nm == "const-string":
                text = '  "%s"' % dx.string(raw[1])
            elif nm == "const-string/jumbo":
                idx = raw[1] | (raw[2] << 16)
                text = '  "%s"' % dx.string(idx)
            elif nm in ("const-class", "new-instance", "check-cast", "instance-of"):
                text = "  %s" % dx.type(raw[1])
            elif nm in ("sget", "sget-wide", "sget-object", "sget-boolean", "sget-byte",
                        "sget-char", "sget-short", "iput", "iput-wide", "iput-object",
                        "iput-boolean", "iput-byte", "iput-char", "iput-short",
                        "iget", "iget-wide", "iget-object", "iget-boolean", "iget-byte",
                        "iget-char", "iget-short"):
                c, t, fn = dx.field(raw[1])
                text = "  %s->%s : %s" % (c, fn, t)
            elif nm == "invoke":
                # 35c 实测: unit0 = A|op(A=参数个数), unit1 = 完整 method_idx
                mi = raw[1]
                c, mn, a, r = dx.method(mi)
                text = "  %s.%s(%s)   [argc=%d]" % (c, mn, ", ".join(a), (unit >> 8) & 0xF)
            elif nm == "invoke/range":
                # 3rc: unit0 = AA|op, unit1 = method_idx, unit2 = 起始寄存器
                mi = raw[1]
                c, mn, a, r = dx.method(mi)
                text = "  %s.%s(%s)   [argc=%d]" % (c, mn, ", ".join(a), (unit >> 8) & 0xF)
            elif nm.startswith("invoke"):
                mi = raw[1]
                c, mn, a, r = dx.method(mi)
                text = "  %s.%s(%s)" % (c, mn, ", ".join(a))
            elif fmt == "10t":
                off = _s8(unit & 0xFF)
                text = "  -> %04x" % (i + off)
            elif fmt == "20t":
                off = _s16(raw[1])
                text = "  -> %04x" % (i + off)
            elif fmt == "30t":
                off = _s32(raw[1] | (raw[2] << 16))
                text = "  -> %04x" % (i + off)
            elif fmt in ("21t", "22t"):
                off = _s8(raw[1] >> 8)
                text = "  -> %04x" % (i + off)
            elif fmt == "31t":
                off = _s32(raw[1] | (raw[2] << 16))
                text = "  -> %04x" % (i + off)
            elif nm == "const/4":
                text = "  v%d, #%d" % (raw[1] & 0xF, _s8((raw[1] >> 4) & 0xF))
            elif nm == "const/16":
                text = "  v%d, #%d" % (raw[1] & 0xFF, _s16(raw[2]))
            elif nm == "const":
                text = "  v%d, #%d" % (raw[1] & 0xFF, _s32(raw[2] | (raw[3] << 16)))
            elif nm in ("move", "move-wide", "move-object", "return", "return-wide",
                        "return-object", "move-result", "move-result-wide",
                        "move-result-object", "throw", "monitor-enter", "monitor-exit",
                        "array-length", "new-array"):
                text = "  v%d" % (raw[1] & 0xFF)
            elif fmt == "12x":
                text = "  v%d, v%d" % (raw[1] & 0xF, (raw[1] >> 4) & 0xF)
            elif fmt == "22x":
                text = "  v%d, v%d" % (raw[1] & 0xFF, raw[2])
            elif fmt == "23x":
                text = "  v%d, v%d, v%d" % (raw[1] & 0xFF, (raw[1] >> 8) & 0xFF, raw[2])
            elif fmt == "22c":
                text = "  v%d, v%d" % (raw[1] & 0xFF, raw[2])
            elif fmt == "21c":
                text = "  v%d" % (raw[1] & 0xFF)
            elif fmt == "35c":
                text = "  args mask=0x%04x" % (raw[1] & 0xFFFF)
        except Exception as e:  # noqa: BLE001
            text = "  <%s>" % e
        lines.append("%04x: %-22s %-6s%s" % (i, nm, fmt, text))
        i += size
    return cls, name, args, ret, regs, ins, outs, lines


def xref(dx, needle):
    """打印所有引用了包含 needle 的字符串的方法。"""
    pat = re.compile(needle)
    for cls, access, data_off, static_off in dx.classes():
        static, inst, meths = dx.class_data(data_off)
        for midx, flags, code_off, group in meths:
            if not code_off:
                continue
            c, mn, a, r = dx.method(midx)
            if not pat.search(cls) and not pat.search(mn):
                # 类名/方法名不匹配时仍要检查方法体, 但先快速跳过同名类
                pass
            got = decode_method(dx, midx, flags, code_off)
            if not got:
                continue
            lines = got[-1]
            for idx, ln in enumerate(lines):
                if '"' not in ln:
                    continue
                m = re.search(r'"([^"]*)"', ln)
                if not m or not pat.search(m.group(1)):
                    continue
                print("\n%s  ->  %s" % (c.replace("/", "."), mn))
                lo = max(0, idx - 6)
                hi = min(len(lines), idx + 7)
                for j in range(lo, hi):
                    mark = ">>" if j == idx else "  "
                    print("   %s %s" % (mark, lines[j]))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    path = sys.argv[1]
    if sys.argv[2] == "--xref":
        dx = Dex(path)
        for needle in sys.argv[3:]:
            print("\n############ xref: %s" % needle)
            xref(dx, needle)
        return 0
    cls_re = re.compile(sys.argv[2])
    meth_re = re.compile(sys.argv[3]) if len(sys.argv) > 3 else None
    dx = Dex(path)
    for cls, access, data_off, static_off in dx.classes():
        if not cls_re.search(cls):
            continue
        print("\n" + "=" * 100)
        print("CLASS %s   (access=0x%x)" % (cls.replace("/", "."), access))
        static, inst, meths = dx.class_data(data_off)
        for fidx, flags in static:
            c, t, fn = dx.field(fidx)
            print("  static field  %s : %s   (flags=0x%x)" % (fn, t, flags))
        for fidx, flags in inst:
            c, t, fn = dx.field(fidx)
            print("  instance field %s : %s   (flags=0x%x)" % (fn, t, flags))
        for midx, flags, code_off, group in meths:
            c, mn, a, r = dx.method(midx)
            if meth_re and not meth_re.search(mn):
                continue
            print("\n  --- %s %s %s(%s)  [flags=0x%x]" % (group, r, mn, ", ".join(a), flags))
            got = decode_method(dx, midx, flags, code_off)
            if not got:
                print("      (no code)")
                continue
            for ln in got[-1]:
                print("      " + ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
