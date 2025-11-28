from flask import Flask, render_template, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# AI配置
API_BASE_URL = "https://api.ephone.ai"
API_KEY = "sk-t7gEReNbFHqwg8a2CDFlBpaSxAwuoKBtth8BinWXnNy2xUzc"
MODEL = "gpt-4o"

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_flowchart():
    """生成流程图"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        
        if not description:
            return jsonify({'error': '请输入流程图描述'}), 400
        
        # 调用AI生成Mermaid流程图代码
        mermaid_code = call_ai_api(description)
        
        return jsonify({
            'success': True,
            'mermaid_code': mermaid_code
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def call_ai_api(description):
    """调用AI API生成Mermaid流程图代码"""
    
    prompt = f"""请根据以下描述生成一个美观的Mermaid流程图代码。
要求：
1. 只返回Mermaid代码，不要有其他解释
2. 使用flowchart TD或flowchart LR格式
3. 使用中文标签
4. 确保流程清晰、美观
5. 可以使用不同的节点样式（圆角矩形、菱形等）和颜色

描述：{description}

请直接返回Mermaid代码："""
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    payload = {
        'model': MODEL,
        'messages': [
            {
                'role': 'system',
                'content': '你是一个专业的流程图设计师，擅长使用Mermaid语法创建清晰美观的流程图。'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    response = requests.post(
        f'{API_BASE_URL}/v1/chat/completions',
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code != 200:
        raise Exception(f'API调用失败: {response.status_code} - {response.text}')
    
    result = response.json()
    mermaid_code = result['choices'][0]['message']['content'].strip()
    
    # 清理可能的markdown代码块标记
    if mermaid_code.startswith('```mermaid'):
        mermaid_code = mermaid_code.replace('```mermaid', '').replace('```', '').strip()
    elif mermaid_code.startswith('```'):
        mermaid_code = mermaid_code.replace('```', '').strip()
    
    return mermaid_code

@app.route('/examples', methods=['GET'])
def get_examples():
    """获取示例流程图"""
    examples = [
        {
            'title': '用户登录流程',
            'description': '创建一个用户登录系统的流程图，包含输入用户名密码、验证、登录成功或失败的处理'
        },
        {
            'title': '订单处理流程',
            'description': '设计一个电商订单处理流程，从下单到配送完成'
        },
        {
            'title': '软件开发流程',
            'description': '展示敏捷开发的完整流程，包括需求分析、设计、开发、测试、部署'
        },
        {
            'title': '请假审批流程',
            'description': '员工请假审批系统的流程图，包含申请、主管审批、HR审批等环节'
        }
    ]
    return jsonify(examples)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
