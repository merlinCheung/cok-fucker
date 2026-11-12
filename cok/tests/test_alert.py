#!/usr/bin/env python3
"""webhook 告警端到端测试: 起本地接收器, 验证三种载荷格式与实际送达。"""
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from cok_daemon import Alert  # noqa: E402

RECEIVED = []


class H(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        RECEIVED.append((self.path, json.loads(body.decode("utf-8"))))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"errcode":0}')

    def log_message(self, *a):
        pass


def main():
    srv = HTTPServer(("127.0.0.1", 0), H)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/hook" % port
    print("本地接收器: %s" % url)

    for kind in ("generic", "wechat", "dingtalk"):
        a = Alert(url, kind, ["sign", "claim", "task", "boss", "error"])
        ok = a.push("sign", "每日签到完成", ["服务器日期: 2026-10-23", "奖励: 211508 x20000"],
                    key="dailySign", value={"今日已签": True})
        print("  %-9s 推送=%s  累计发送=%d  最后错误=%s" % (kind, ok, a.sent, a.last_error))

    # 规则过滤: 未启用的规则不应推送
    a2 = Alert(url, "generic", ["error"])
    before = len(RECEIVED)
    a2.push("sign", "不该发", ["x"])
    print("  规则过滤: 收到 %d 条(应为 0)" % (len(RECEIVED) - before))

    # 不存在的地址应报错但不崩
    a3 = Alert("http://127.0.0.1:1/nope", "generic", ["sign"])
    ok = a3.push("sign", "x", ["y"])
    print("  失败处理: 推送=%s  last_error=%s" % (ok, (a3.last_error or "")[:60]))

    print("\n=== 收到的载荷 ===")
    for path, payload in RECEIVED:
        print("  %s -> %s" % (path, json.dumps(payload, ensure_ascii=False)[:200]))
    srv.shutdown()


if __name__ == "__main__":
    main()
