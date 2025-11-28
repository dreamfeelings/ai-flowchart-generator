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
    """生成图表（流程图、ER图等）"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        chart_type = data.get('chart_type', 'flowchart')  # flowchart 或 er
        
        if not description:
            return jsonify({'error': '请输入图表描述'}), 400
        
        # 调用AI生成Mermaid代码
        mermaid_code = call_ai_api(description, chart_type)
        
        return jsonify({
            'success': True,
            'mermaid_code': mermaid_code,
            'chart_type': chart_type
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def call_ai_api(description, chart_type='flowchart'):
    """调用AI API生成Mermaid代码"""
    
    if chart_type == 'mindmap':
        prompt = f"""请根据以下描述生成一个树状结构的思维导图Mermaid代码。
要求：
1. 只返回Mermaid代码，不要有其他解释
2. 使用flowchart LR格式（从左到右展开）
3. 使用中文标签
4. 结构清晰，层次分明（建议3-5层）
5. 中心主题用圆角矩形：A[中心主题]
6. 一级分支用矩形：B[一级分支]
7. 二级及以下用矩形：C[二级内容]
8. 使用箭头连接：A --> B --> C
9. 节点ID用英文，显示文本用中文

示例格式：
flowchart LR
    A[中心主题]
    B1[一级分支1]
    B2[一级分支2]
    C1[二级内容1]
    C2[二级内容2]
    C3[二级内容3]
    D1[三级细节1]
    D2[三级细节2]
    
    A --> B1
    A --> B2
    B1 --> C1
    B1 --> C2
    B2 --> C3
    C1 --> D1
    C1 --> D2

描述：{description}

请直接返回Mermaid代码（使用flowchart LR格式）："""
        system_content = '你是一个专业的思维导图设计师，擅长使用Mermaid的flowchart语法创建树状结构的思维导图。使用从左到右的布局，节点用方框表示。'
    elif chart_type == 'chen':
        prompt = f"""请根据以下描述生成一个传统陈氏ER图（Chen Notation）的Mermaid代码。
要求：
1. 只返回Mermaid代码，不要有其他解释
2. 使用graph TD或graph LR格式（不是erDiagram）
3. 实体使用矩形：EntityName[实体名]
4. 属性使用椭圆：AttrName(属性名)
5. 关系使用菱形：RelName{{关系名}}
6. 使用英文命名节点ID，显示文本用中文
7. 连接线格式：Entity --> Relation --> Entity 或 Entity --> Attribute

示例格式：
graph TD
    Product[商品]
    ProductName(名称)
    ProductPrice(价格)
    Order[订单]
    OrderDate(订单日期)
    PlaceOrder{{下单}}
    
    Product --> ProductName
    Product --> ProductPrice
    Product --> PlaceOrder
    PlaceOrder --> Order
    Order --> OrderDate

描述：{description}

请直接返回Mermaid代码："""
        system_content = '你是一个专业的数据库设计师，擅长使用传统陈氏表示法（Chen Notation）创建ER图。使用Mermaid的graph语法模拟陈氏ER图：矩形表示实体、椭圆表示属性、菱形表示关系。'
    elif chart_type == 'er':
        prompt = f"""请根据以下描述生成一个美观的Mermaid ER图（实体关系图）代码。
要求：
1. 只返回Mermaid代码，不要有其他解释
2. 使用erDiagram格式
3. **实体名称必须使用英文或拼音**（例如：User、Order、Student）
4. 属性名称使用英文，可以添加中文注释（例如：string name "姓名"）
5. 关系描述使用英文或拼音（例如："places"、"has"）
6. 正确定义实体、属性和关系
7. 关系类型：||--||（一对一）、||--o{{（一对多）、}}o--o{{（多对多）等
8. 为每个实体添加合适的属性，格式：类型 属性名 "中文注释"

示例格式：
erDiagram
    USER ||--o{{ ORDER : places
    USER {{
        int id "用户ID"
        string name "姓名"
        string email "邮箱"
    }}
    ORDER {{
        int id "订单ID"
        date orderDate "下单日期"
    }}

描述：{description}

请直接返回Mermaid代码："""
        system_content = '你是一个专业的数据库设计师，擅长使用Mermaid语法创建清晰美观的ER图。注意实体名称和关系必须使用英文。'
    else:
        prompt = f"""请根据以下描述生成一个美观的Mermaid流程图代码。
要求：
1. 只返回Mermaid代码，不要有其他解释
2. 使用flowchart TD或flowchart LR格式
3. 使用中文标签
4. 确保流程清晰、美观
5. 使用不同的节点样式：
   - 圆角矩形用于普通步骤：A[文本]
   - 菱形用于判断：B{{判断条件}}
   - 圆形用于开始/结束：C((开始))
   - 圆柱形用于数据库：D[(数据库)]
6. 必须为每个节点添加样式类，使用以下格式：
   - 成功/正常节点：:::successClass
   - 失败/错误节点：:::errorClass  
   - 警告/待处理节点：:::warningClass
   - 信息/普通节点：:::infoClass
   - 判断节点：:::decisionClass

示例格式：
flowchart TD
    A[开始]:::infoClass
    B{{判断条件}}:::decisionClass
    C[成功操作]:::successClass
    D[失败操作]:::errorClass
    A --> B
    B -->|是| C
    B -->|否| D

描述：{description}

请直接返回Mermaid代码（必须包含样式类）："""
        system_content = '你是一个专业的流程图设计师，擅长使用Mermaid语法创建清晰美观的流程图。必须为节点添加合适的样式类。'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    payload = {
        'model': MODEL,
        'messages': [
            {
                'role': 'system',
                'content': system_content
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
    """获取示例图表"""
    examples = [
        {
            'title': '用户登录流程',
            'description': '创建一个用户登录系统的流程图，包含输入用户名密码、验证、登录成功或失败的处理',
            'type': 'flowchart'
        },
        {
            'title': '订单处理流程',
            'description': '设计一个电商订单处理流程，从下单到配送完成',
            'type': 'flowchart'
        },
        {
            'title': '电商数据库ER图',
            'description': '设计一个电商系统的数据库ER图，包含用户、商品、订单、订单详情等实体及其关系',
            'type': 'er'
        },
        {
            'title': '学生管理系统ER图',
            'description': '创建一个学生管理系统的ER图，包含学生、课程、教师、成绩等实体',
            'type': 'er'
        },
        {
            'title': '电商系统陈氏ER图',
            'description': '用传统陈氏表示法设计电商系统，显示商品、客户、订单的实体、属性和关系',
            'type': 'chen'
        },
        {
            'title': '图书馆陈氏ER图',
            'description': '用陈氏表示法设计图书馆系统，包含图书、读者、借阅关系及其属性',
            'type': 'chen'
        },
        {
            'title': '软件开发流程',
            'description': '展示敏捷开发的完整流程，包括需求分析、设计、开发、测试、部署',
            'type': 'flowchart'
        },
        {
            'title': '项目管理思维导图',
            'description': '创建一个项目管理的思维导图，包含计划、执行、监控、收尾等阶段及其关键要素',
            'type': 'mindmap'
        },
        {
            'title': '学习方法思维导图',
            'description': '设计学习方法论的思维导图，包含预习、听课、复习、练习、总结等环节',
            'type': 'mindmap'
        },
        {
            'title': 'Python知识体系',
            'description': '构建Python编程知识体系思维导图，涵盖基础语法、数据结构、面向对象、常用库等',
            'type': 'mindmap'
        }
    ]
    return jsonify(examples)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
