from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    # 返回一个简单的 JSON 响应
    return jsonify({"status": "success", "message": "Hello from Python CI/CD Pipeline!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)