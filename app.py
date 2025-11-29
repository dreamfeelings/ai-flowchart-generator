from flask import Flask, render_template, request, jsonify
import requests
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

# 导入配置
try:
    from config import API_BASE_URL, API_KEY, MODEL
except ImportError:
    raise ImportError("请复制 config.example.py 为 config.py 并配置你的API密钥")
import os

app = Flask(__name__)

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
        layout = data.get('layout', 'LR')  # LR 横向或 TD 纵向
        
        logging.info(f"="*50)
        logging.info(f"收到请求: 类型={chart_type}, 布局={layout}")
        logging.info(f"描述: {description[:100]}..." if len(description) > 100 else f"描述: {description}")
        
        if not description:
            logging.warning("请求失败: 描述为空")
            return jsonify({'error': '请输入图表描述'}), 400
        
        # 调用AI生成Mermaid代码
        mermaid_code = call_ai_api(description, chart_type, layout)
        
        logging.info(f"✅ 生成成功! Mermaid代码长度: {len(mermaid_code)} 字符")
        logging.info(f"生成的代码:\n{mermaid_code}")
        
        return jsonify({
            'success': True,
            'mermaid_code': mermaid_code,
            'chart_type': chart_type
        })
    
    except Exception as e:
        logging.error(f"❌ 生成失败: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/extract', methods=['POST'])
def extract_key_info():
    """从长文本中提取关键流程信息"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        chart_type = data.get('chart_type', 'flowchart')
        
        logging.info(f"="*50)
        logging.info(f"提取请求: 类型={chart_type}, 文本长度={len(text)}")
        
        if not text:
            return jsonify({'error': '请输入文本'}), 400
        
        # 调用AI提取关键信息
        extracted = extract_with_ai(text, chart_type)
        
        logging.info(f"✅ 提取成功! 结果长度: {len(extracted)} 字符")
        logging.info(f"提取结果:\n{extracted}")
        
        return jsonify({
            'success': True,
            'extracted_text': extracted
        })
    
    except Exception as e:
        logging.error(f"❌ 提取失败: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

def extract_with_ai(text, chart_type='flowchart'):
    """调用AI提取关键流程信息"""
    
    if chart_type == 'flowchart':
        prompt = f"""请从以下文本中提取流程图所需的关键信息。

【提取要求】
1. 识别流程的开始和结束点
2. 提取每个处理步骤
3. **重点识别判断/决策点**（如：是否满足条件、成功/失败、通过/不通过）
4. 标注分支走向（满足条件做什么，不满足做什么）
5. 识别循环或返回的流程

【输出格式示例】
开始：用户登录
步骤1：输入用户名密码
判断：验证是否通过？
  - 是：进入主页
  - 否：显示错误，返回步骤1
结束：流程完成

【原始文本】
{text}

【提取结果】："""
    elif chart_type in ['er', 'chen']:
        prompt = f"""请从以下文本中提取ER图所需的信息。

【提取要求】
1. 识别所有实体（名词，如：用户、订单、商品）
2. 识别实体的属性
3. 识别实体之间的关系（一对一、一对多、多对多）

【输出格式】
实体1：用户（属性：ID、姓名、邮箱）
实体2：订单（属性：订单号、金额、时间）
关系：用户 --1对多-- 订单

【原始文本】
{text}

【提取结果】："""
    else:  # mindmap
        prompt = f"""请从以下文本中提取思维导图所需的层级信息。

【提取要求】
1. 识别中心主题
2. 提取一级分支（主要类别）
3. 提取二级分支（子类别或细节）

【输出格式】
中心：项目管理
├─ 计划阶段
│  ├─ 需求分析
│  └─ 资源规划
├─ 执行阶段
│  ├─ 开发
│  └─ 测试

【原始文本】
{text}

【提取结果】："""

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    payload = {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': '你是文本分析专家，擅长从复杂文本中提取关键流程信息。只输出提取结果，不要任何解释。'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3,
        'max_tokens': 1000
    }
    
    try:
        response = requests.post(
            f'{API_BASE_URL}/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
    except requests.exceptions.Timeout:
        raise Exception('API请求超时')
    except requests.exceptions.ConnectionError:
        raise Exception('API连接失败')
    
    if response.status_code != 200:
        raise Exception(f'API调用失败: {response.status_code}')
    
    result = response.json()
    extracted_text = result['choices'][0]['message']['content'].strip()
    
    return extracted_text

def call_ai_api(description, chart_type='flowchart', layout='LR'):
    """调用AI API生成Mermaid代码
    layout: LR(横向,适合Word) 或 TD(纵向)
    """
    
    layout_desc = '从左到右横向展开' if layout == 'LR' else '从上到下纵向展开'
    logging.info(f"调用AI API: {API_BASE_URL}, 模型: {MODEL}")
    
    if chart_type == 'mindmap':
        prompt = f"""请根据以下描述生成一个树状结构的思维导图Mermaid代码。

【严格要求】
1. 只返回纯Mermaid代码，不要任何解释、注释或markdown标记
2. 使用 flowchart {layout} 格式（{layout_desc}）
3. 节点ID必须是简单的英文字母+数字，如 A1, B2, C3（不要用特殊字符）
4. 中文文本放在方括号内：A1[中文内容]
5. 连接线只用 --> 符号
6. 不要使用 subgraph、class、style 等高级语法
7. 每行一个定义或连接，保持简洁

【正确示例】
flowchart {layout}
    A[中心主题]
    B1[一级分支1]
    B2[一级分支2]
    C1[二级内容1]
    C2[二级内容2]
    A --> B1
    A --> B2
    B1 --> C1
    B1 --> C2

描述：{description}

请直接返回Mermaid代码："""
        system_content = '你是Mermaid语法专家。只输出有效的Mermaid代码，不要任何解释。节点ID用简单英文字母数字，中文放在方括号内。'
    elif chart_type == 'chen':
        prompt = f"""请根据以下描述生成一个传统陈氏ER图（Chen Notation）的Mermaid代码。

【严格要求】
1. 只返回纯Mermaid代码，不要任何解释、注释或markdown标记
2. 使用 graph {layout} 格式（{layout_desc}）
3. 节点ID必须是简单英文，如 Product, Order, User（不要特殊字符）
4. 实体用矩形：Product[商品]
5. 属性用圆括号：Name(名称)
6. 关系用双花括号：Rel{{"关系名"}}
7. 连接只用 --> 或 ---
8. 不要使用 linkStyle、classDef 等高级语法

【正确示例】
graph {layout}
    Product[商品]
    PName(名称)
    Price(价格)
    Order[订单]
    Buy{{"购买"}}
    Product --> PName
    Product --> Price
    Product --> Buy
    Buy --> Order

描述：{description}

请直接返回Mermaid代码："""
        system_content = '你是Mermaid语法专家。只输出有效的Mermaid代码，不要任何解释。使用graph语法，节点ID用简单英文。'
    elif chart_type == 'er':
        prompt = f"""请根据以下描述生成Mermaid ER图代码。

【严格要求 - 必须遵守】
1. 只返回纯Mermaid代码，不要任何解释、注释或markdown标记
2. 第一行必须是 erDiagram
3. 实体名必须是纯英文，不能有空格或特殊字符（如 User, Order, Product）
4. 关系符号：||--|| 一对一，||--o{{ 一对多，}}o--o{{ 多对多
5. 关系标签用英文：places, has, contains, belongs
6. 属性格式：类型 属性名 "注释"（类型用 int/string/date）
7. 实体定义用花括号，每个属性一行

【正确示例】
erDiagram
    User ||--o{{ Order : places
    User {{
        int id "ID"
        string name "姓名"
    }}
    Order {{
        int id "ID"
        date created "日期"
    }}

描述：{description}

请直接返回Mermaid代码："""
        system_content = '你是Mermaid语法专家。只输出有效的erDiagram代码。实体名和关系标签必须是纯英文，不能有中文或特殊字符。'
    else:
        prompt = f"""请根据以下描述生成Mermaid流程图代码。

【严格要求 - 必须遵守】
1. 只返回纯Mermaid代码，不要任何解释、注释或markdown标记
2. 第一行必须是 flowchart {layout}（{layout_desc}）
3. 节点ID必须是简单英文字母+数字，如 A, B1, C2（不要用中文或特殊字符做ID）
4. 中文内容放在方括号内：A[开始流程]
5. 判断节点用花括号：B{{是否通过}}
6. 连接线用 --> 或带标签 -->|是|
7. 不要使用 :::className、classDef、subgraph、linkStyle 等语法

【正确示例】
flowchart {layout}
    A[开始]
    B{{判断}}
    C[成功]
    D[失败]
    A --> B
    B -->|是| C
    B -->|否| D

描述：{description}

请直接返回Mermaid代码："""
        system_content = '你是Mermaid语法专家。只输出最简单的flowchart代码，不要任何样式类、不要解释。'
    
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
    
    logging.info("正在发送请求到AI API...")
    
    try:
        response = requests.post(
            f'{API_BASE_URL}/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
    except requests.exceptions.Timeout:
        logging.error("API请求超时(30s)")
        raise Exception('API请求超时，请稍后重试')
    except requests.exceptions.ConnectionError as e:
        logging.error(f"API连接失败: {e}")
        raise Exception('API连接失败，请检查网络')
    
    logging.info(f"API响应状态码: {response.status_code}")
    
    if response.status_code != 200:
        logging.error(f"API错误响应: {response.text}")
        raise Exception(f'API调用失败: {response.status_code}')
    
    result = response.json()
    mermaid_code = result['choices'][0]['message']['content'].strip()
    logging.info(f"AI原始返回 ({len(mermaid_code)} 字符)")
    
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
    logging.info("="*50)
    logging.info("🚀 AI 图表生成器启动")
    logging.info(f"API地址: {API_BASE_URL}")
    logging.info(f"模型: {MODEL}")
    logging.info("="*50)
    app.run(debug=True, host='0.0.0.0', port=5000)
