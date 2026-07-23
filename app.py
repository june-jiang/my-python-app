from flask import Flask

app = Flask(__name__)

# 🌟 当前版本定义为 v1
APP_VERSION = "v1.0"
BG_COLOR = "#3498db" # 蓝色代表 v1

@app.route('/')
def hello():
    # 返回一个好看的 HTML 页面，带版本号和背景色
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Canary Test App</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: {BG_COLOR};
                color: white;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background: rgba(0,0,0,0.2);
                padding: 40px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 8px 16px rgba(0,0,0,0.3);
            }}
            h1 {{ font-size: 3rem; margin-bottom: 10px; }}
            p {{ font-size: 1.5rem; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚀 APP VERSION: {APP_VERSION}</h1>
            <p>Welcome to GitOps Canary Deployment Test!</p>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)