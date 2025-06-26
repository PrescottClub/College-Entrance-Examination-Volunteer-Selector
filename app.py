import os
from flask import Flask, request, render_template, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from data_processor import DataProcessor
from recommender import Recommender
from deepseek_service import DeepSeekService
from config import UPLOAD_FOLDER, MAX_FILE_SIZE, allowed_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 全局变量
data_processor = DataProcessor()
deepseek_service = DeepSeekService()
recommender = Recommender(data_processor)
data_loaded = False

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', data_loaded=data_loaded)

@app.route('/upload', methods=['POST'])
def upload_files():
    """文件上传接口"""
    global data_loaded
    
    try:
        # 检查是否有文件
        if 'score_rank_file' not in request.files or \
           'cutoff_file' not in request.files or \
           'plan_file' not in request.files:
            return jsonify({'success': False, 'message': '请上传所有三个Excel文件'})
        
        files = {
            'score_rank': request.files['score_rank_file'],
            'cutoff': request.files['cutoff_file'],
            'plan': request.files['plan_file']
        }
        
        # 检查文件名
        for key, file in files.items():
            if file.filename == '':
                return jsonify({'success': False, 'message': f'{key}文件未选择'})
            if file.filename and not allowed_file(file.filename):
                return jsonify({'success': False, 'message': f'{key}文件格式不正确，请上传Excel文件'})
        
        # 保存文件
        saved_files = {}
        for key, file in files.items():
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{key}_{filename}")
                file.save(filepath)
                saved_files[key] = filepath
        
        # 处理数据
        success, message = data_processor.process_all_data(
            saved_files['score_rank'],
            saved_files['cutoff'], 
            saved_files['plan']
        )
        
        if success:
            data_loaded = True
            return jsonify({'success': True, 'message': '文件上传和数据处理成功！'})
        else:
            return jsonify({'success': False, 'message': f'数据处理失败: {message}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'})

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    """获取推荐结果"""
    if not data_loaded:
        return jsonify({'success': False, 'message': '请先上传数据文件'})
    
    try:
        data = request.json
        user_rank = data.get('rank')
        track = data.get('track')
        
        # 验证必填参数
        if not user_rank or not track:
            return jsonify({'success': False, 'message': '请输入位次和选择科目'})
        
        user_rank = int(user_rank)
        
        # 构建筛选条件
        filters = {}
        if data.get('cities'):
            filters['cities'] = data['cities']
        if data.get('is_985'):
            filters['is_985'] = True
        if data.get('is_211'):
            filters['is_211'] = True
        if data.get('majors'):
            filters['majors'] = data['majors']
        
        # 生成推荐
        result = recommender.generate_recommendations(user_rank, track, filters)
        
        # 如果成功生成推荐，添加AI策略建议
        if result['success']:
            strategy_result = deepseek_service.generate_volunteer_strategy(
                result['data'], user_rank, track
            )
            if strategy_result['success']:
                result['strategy'] = strategy_result['strategy']
        
        return jsonify(result)
        
    except ValueError:
        return jsonify({'success': False, 'message': '位次必须是数字'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'推荐生成失败: {str(e)}'})

@app.route('/analyze_major', methods=['POST'])
def analyze_major():
    """获取专业分析"""
    if not data_loaded:
        return jsonify({'success': False, 'message': '请先上传数据文件'})
    
    try:
        data = request.json
        school_name = data.get('school_name')
        major_name = data.get('major_name')
        user_rank = data.get('user_rank')
        cutoff_rank = data.get('cutoff_rank')
        
        if not all([school_name, major_name, user_rank, cutoff_rank]):
            return jsonify({'success': False, 'message': '缺少必要参数'})
        
        result = deepseek_service.generate_major_analysis(
            school_name, major_name, int(user_rank), int(cutoff_rank)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'专业分析失败: {str(e)}'})

@app.route('/test_deepseek')
def test_deepseek():
    """测试DeepSeek API连接"""
    result = deepseek_service.test_connection()
    return jsonify(result)

@app.route('/score_to_rank', methods=['POST'])
def score_to_rank():
    """分数转位次"""
    if not data_loaded:
        return jsonify({'success': False, 'message': '请先上传数据文件'})
    
    try:
        data = request.json
        score = data.get('score')
        track = data.get('track', '物理')
        
        if not score:
            return jsonify({'success': False, 'message': '请输入分数'})
        
        rank = data_processor.score_to_rank(int(score), track)
        if rank:
            return jsonify({'success': True, 'rank': rank})
        else:
            return jsonify({'success': False, 'message': '找不到对应位次，可能分数超出范围'})
            
    except ValueError:
        return jsonify({'success': False, 'message': '分数必须是数字'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'转换失败: {str(e)}'})

@app.route('/get_filters')
def get_filters():
    """获取筛选选项"""
    if not data_loaded:
        return jsonify({'success': False, 'message': '请先上传数据文件'})
    
    try:
        cities = data_processor.get_available_cities()
        majors = data_processor.get_available_majors()
        
        return jsonify({
            'success': True,
            'cities': cities,
            'majors': majors
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取筛选选项失败: {str(e)}'})

@app.route('/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        'data_loaded': data_loaded,
        'message': '数据已加载' if data_loaded else '请上传数据文件'
    })

if __name__ == '__main__':
    print("高考志愿规划助手启动中...")
    print("请在浏览器中访问: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 