#!/bin/sh
# 抓「游戏侧」HTTP 流量 —— 目标是拿到 getserverlist.php 的**真实请求**(含 sig)。
#
# 为什么需要它(见 RE-渠道登录逆向方案.md §8.10):
#   游戏服对"没在果盘后端登记过的 pfId"回 E100111(无法获取服务器信息);
#   登记这一步在游戏 native 里做, 走 gameservice 的 PHP 接口, 请求带 sig,
#   而 sig 的 key 只存在于 libgame.so 的加密字符串里(爆破失败)。
#   → 抓一次真实请求, 参数集 + sig 算法就都有了。
#
# 用法:
#   sh capture_gamesvc.sh                 # 自动挑真机(非 emulator-*)
#   sh capture_gamesvc.sh emulator-5554   # 指定设备
#
# 产物: protocol/evidence/chanlogin/capture_gamesvc_<host>.pcap
set -e

HERE=$(cd "$(dirname "$0")" && pwd)
OUT_DIR="$HERE/evidence/chanlogin"
ADB="${ADB:-$HOME/Library/Android/sdk/platform-tools/adb}"
PKG="${PKG:-com.hcg.cok.ewanqf.guopan}"
LAUNCH_ACT="${LAUNCH_ACT:-cn.ewan.supersdk.activity.SplashActivity}"

# 1) 选设备: 优先真机
SERIAL="$1"
if [ -z "$SERIAL" ]; then
  for d in $($ADB devices | awk 'NR>1 && $2=="device" {print $1}'); do
    case "$d" in emulator-*) ;; *) SERIAL="$d"; break;; esac
  done
fi
[ -z "$SERIAL" ] && { echo "[!] 没找到真机(只有模拟器?) 请手动指定 serial"; exit 1; }
echo "[*] 设备: $SERIAL   包: $PKG"

# 2) 起抓包(游戏侧主机 + 果盘 SDK 主机都抓, 方便对照)
FILTER="host txaia-cok.elexapp.com or host p1cok.elexapp.com or host p3cok.elexapp.com or host sid.cok.elexapp.com or host c3cok.elexapp.com or host userapi.guopan.cn or host open.guopan.cn"
$ADB -s "$SERIAL" shell "rm -f /data/local/tmp/gamesvc.pcap" >/dev/null 2>&1 || true
$ADB -s "$SERIAL" shell "su -c 'nohup tcpdump -i any -s 0 -U -w /data/local/tmp/gamesvc.pcap \"$FILTER\" >/dev/null 2>&1 &'" || true
sleep 4

# 3) 重启 App —— 触发 首次取服务器信息 + 登录
$ADB -s "$SERIAL" shell "am force-stop $PKG" >/dev/null 2>&1 || true
sleep 2
$ADB -s "$SERIAL" shell "monkey -p $PKG -c android.intent.category.LAUNCHER 1" >/dev/null 2>&1 || true
echo "[*] 已重启 App, 等待 35s 让它走完取服务器信息 + 登录 ..."
sleep 35

# 4) 收包
$ADB -s "$SERIAL" shell "su -c 'pkill tcpdump; sleep 1; ls -l /data/local/tmp/gamesvc.pcap'" || true
mkdir -p "$OUT_DIR"
DST="$OUT_DIR/capture_gamesvc_$(echo "$SERIAL" | tr ':' '_').pcap"
$ADB -s "$SERIAL" pull /data/local/tmp/gamesvc.pcap "$DST" || true
$ADB -s "$SERIAL" shell "rm -f /data/local/tmp/gamesvc.pcap" >/dev/null 2>&1 || true
echo "[*] 抓到: $DST"
ls -l "$DST" 2>/dev/null || true
echo
echo "下一步: 用脚本解出 HTTP 请求(找 getserverlist.php 的 URL + sig):"
echo "  python3 - <<'EOF'"
echo "  import sys; sys.path.insert(0,'$HERE')"
echo "  # 用 protocol/cok_channel_login.py 里的 pcap 解析思路(或 evidence 下的 pcap_sfs) 提取请求行"
echo "  EOF"
