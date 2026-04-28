import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有域名跨域访问

# 数据源列表
SOURCES = [
    {
        "url": "https://www.77cxw.com/api/ssq?num=100",
        "parser": lambda data: [
            {
                "period": item["expect"],
                "reds": [int(x) for x in item["opencode"].split("+")[0].split(",")],
                "blue": int(item["opencode"].split("+")[1])
            }
            for item in data.get("data", [])
            if "opencode" in item and "+" in item["opencode"]
        ]
    },
    {
        "url": "https://api.oioweb.cn/api/ssq?format=json",
        "parser": lambda data: [
            {
                "period": item["code"],
                "reds": [int(x) for x in item["red"].split(",")],
                "blue": int(item["blue"])
            }
            for item in data.get("result", {}).get("list", [])
            if "red" in item and "blue" in item
        ]
    }
]

def fetch_lottery():
    for src in SOURCES:
        try:
            resp = requests.get(src["url"], timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                parsed = src["parser"](data)
                if parsed and len(parsed) > 0:
                    return parsed
        except Exception:
            continue
    return []  # 兜底

@app.route('/api/ssq')
def get_ssq():
    data = fetch_lottery()
    if data:
        return jsonify({"code": 200, "data": data})
    else:
        return jsonify({"code": 500, "msg": "无法获取数据"}), 500

# 健康检查
@app.route('/')
def index():
    return "双色球后端服务运行中"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)