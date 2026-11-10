#!/usr/bin/env python3
"""Minimal MCP client for the Fusion 360 local MCP server (streamable HTTP)."""
import base64, json, sys, urllib.request

URL = "http://127.0.0.1:27182/mcp"
_sid = None


def _post(payload, notify=False):
    global _sid
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    if _sid:
        req.add_header("MCP-Session-Id", _sid)
    with urllib.request.urlopen(req, timeout=600) as r:
        got = r.headers.get("MCP-Session-Id")
        if got:
            _sid = got
        body = r.read().decode("utf-8", "replace")
    if notify or not body.strip():
        return None
    if body.lstrip().startswith("event:") or body.lstrip().startswith("data:"):
        for line in body.splitlines():
            if line.startswith("data:"):
                body = line[5:].strip()
                break
    return json.loads(body)


def init():
    _post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
           "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                      "clientInfo": {"name": "fusion-mcp-client", "version": "1.0.0"}}})
    _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, notify=True)


def call(tool, args, rid=2):
    return _post({"jsonrpc": "2.0", "id": rid, "method": "tools/call",
                  "params": {"name": tool, "arguments": args}})


def show(resp):
    if resp is None:
        print("<no response>"); return
    if "error" in resp:
        print("JSONRPC ERROR:", json.dumps(resp["error"], indent=2)); sys.exit(2)
    res = resp.get("result", {})
    if res.get("isError"):
        print("TOOL ERROR:")
    for item in res.get("content", []):
        if item.get("type") == "text":
            print(item["text"])
        else:
            print("[", item.get("type"), "]")
    if res.get("isError"):
        sys.exit(3)


def main():
    mode = sys.argv[1]
    init()
    if mode == "script":
        src = open(sys.argv[2], "r", encoding="utf-8").read()
        args = {"featureType": "script", "object": {"script": src}}
        if "--readonly" in sys.argv:
            args["object"]["readOnly"] = True
        show(call("fusion_mcp_execute", args))
    elif mode == "read":
        show(call("fusion_mcp_read", json.loads(sys.argv[2])))
    elif mode == "shot":
        out = sys.argv[2]
        q = {"queryType": "screenshot", "width": 1600, "height": 1200,
             "transparentBackground": "--transparent" in sys.argv}
        if len(sys.argv) > 3 and not sys.argv[3].startswith("--"):
            q["direction"] = sys.argv[3]
        resp = call("fusion_mcp_read", q)
        res = resp.get("result", {})
        blob = None
        for item in res.get("content", []):
            if item.get("type") == "image" and item.get("data"):
                blob = item["data"]
            elif item.get("type") == "text":
                try:
                    d = json.loads(item["text"])
                    blob = d.get("base64Data") or blob
                except Exception:
                    print(item["text"][:400])
        if not blob:
            print("NO IMAGE"); sys.exit(4)
        open(out, "wb").write(base64.b64decode(blob))
        print("saved", out)
    else:
        print("usage: fus.py script <file>|read <json>|shot <out.png> [dir]"); sys.exit(1)


main()
