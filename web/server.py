#!/usr/bin/env python3
"""
Sorting Hat · 本地服务器
接收浏览器 POST 请求，将生成的人设内容写入目标文件。
目标路径通过环境变量 SORTING_HAT_OUTPUT 指定，默认写入 ~/.claude/memory/persona.md。
"""
import http.server
import json
import os
import threading
import webbrowser

PORT = 7432
DEFAULT_SAVE_PATH = os.path.expanduser("~/.claude/memory/persona.md")
SAVE_PATH = os.environ.get("SORTING_HAT_OUTPUT", DEFAULT_SAVE_PATH)


class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        # 提供静态文件
        base = os.path.dirname(os.path.abspath(__file__))
        path = self.path.split("?")[0]
        if path == "/" or path == "/index.html":
            filepath = os.path.join(base, "index.html")
            ctype = "text/html"
        else:
            self.send_response(404)
            self.end_headers()
            return

        try:
            with open(filepath, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{ctype}; charset=utf-8")
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/save":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
            content = data.get("content", "")

            # 确保目录存在
            os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

            # 写入文件
            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                f.write(content)

            resp = json.dumps({"ok": True, "path": SAVE_PATH}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", len(resp))
            self.end_headers()
            self.wfile.write(resp)

            print(f"\n✓ 人设已写入 {SAVE_PATH}")
            print("  分院仪式完成，服务器即将关闭…\n")

            # 延迟关闭，让响应先发出去
            threading.Thread(target=self._shutdown, daemon=True).start()

        except Exception as e:
            err = json.dumps({"ok": False, "error": str(e)}).encode()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", len(err))
            self.end_headers()
            self.wfile.write(err)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _shutdown(self):
        import time
        time.sleep(0.8)
        self.server.shutdown()

    def log_message(self, fmt, *args):
        # 只打印 POST 请求，过滤 GET 的噪音
        if args and "POST" in str(args[0]):
            print(f"  {args[0]}")


def main():
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

    server = http.server.HTTPServer(("localhost", PORT), Handler)

    print("=" * 52)
    print("  🎩  Sorting Hat · 分院仪式启动")
    print("=" * 52)
    print(f"  浏览器已打开，请在页面中完成问卷")
    print(f"  完成后点击「保存人设」，文件将自动写入：")
    print(f"  {SAVE_PATH}")
    print("=" * 52)
    print("  按 Ctrl+C 可手动退出\n")

    # 自动打开浏览器
    url = f"http://localhost:{PORT}"
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  服务器已退出。")


if __name__ == "__main__":
    main()
