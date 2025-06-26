#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试DeepSeek API和数据处理功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from deepseek_service import DeepSeekService
from data_processor import DataProcessor
from recommender import VolunteerRecommender

def test_deepseek_connection():
    """测试DeepSeek API连接"""
    print("🤖 测试DeepSeek API连接...")
    ds = DeepSeekService()
    result = ds.test_connection()
    
    if result['success']:
        print(f"✅ DeepSeek API连接成功: {result['message']}")
        return True
    else:
        print(f"❌ DeepSeek API连接失败: {result['message']}")
        return False

def test_volunteer_strategy():
    """测试志愿填报策略生成"""
    print("\n📋 测试志愿填报策略生成...")
    ds = DeepSeekService()
    
    # 模拟推荐数据
    test_data = {
        '冲': [
            {'school_name': '北京大学', 'major_group': '理科试验班'},
            {'school_name': '清华大学', 'major_group': '理科试验班'}
        ],
        '稳': [
            {'school_name': '华南理工大学', 'major_group': '计算机类'},
            {'school_name': '中山大学', 'major_group': '数学类'}
        ],
        '保': [
            {'school_name': '广西大学', 'major_group': '工科试验班'},
            {'school_name': '桂林电子科技大学', 'major_group': '计算机类'}
        ]
    }
    
    result = ds.generate_volunteer_strategy(test_data, 50000, '物理')
    
    if result['success']:
        print("✅ 策略生成成功!")
        print("💡 AI建议:")
        print(result['strategy'])
        return True
    else:
        print(f"❌ 策略生成失败: {result['strategy']}")
        return False

def test_major_analysis():
    """测试专业分析"""
    print("\n🔍 测试专业分析...")
    ds = DeepSeekService()
    
    result = ds.generate_major_analysis(
        school_name="北京大学",
        major_name="计算机科学与技术",
        user_rank=10000,
        cutoff_rank=8000
    )
    
    if result['success']:
        print("✅ 专业分析成功!")
        print("📊 分析结果:")
        print(result['analysis'])
        return True
    else:
        print(f"❌ 专业分析失败: {result['analysis']}")
        return False

def test_data_processing():
    """测试数据处理功能"""
    print("\n📊 测试数据处理功能...")
    
    dp = DataProcessor()
    
    # 检查示例数据文件是否存在
    test_files = [
        'static/uploads/score_rank_xlsx',
        'static/uploads/cutoff_xlsx', 
        'static/uploads/plan_G--2024_.xlsx'
    ]
    
    available_files = []
    for file_path in test_files:
        if os.path.exists(file_path):
            available_files.append(file_path)
            print(f"✅ 找到数据文件: {file_path}")
        else:
            print(f"⚠️  未找到数据文件: {file_path}")
    
    if len(available_files) >= 1:
        print("✅ 数据处理组件可用")
        return True
    else:
        print("❌ 缺少必要的数据文件")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试高考志愿规划助手AI功能\n")
    
    results = []
    
    # 测试各个功能
    results.append(test_deepseek_connection())
    results.append(test_volunteer_strategy())
    results.append(test_major_analysis())
    results.append(test_data_processing())
    
    # 总结
    print("\n" + "="*50)
    print("📋 测试总结:")
    print(f"✅ 成功: {sum(results)}/{len(results)}")
    print(f"❌ 失败: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 所有功能测试通过！DeepSeek API配置正确，系统运行正常。")
    else:
        print("\n⚠️  部分功能存在问题，请检查配置。")
    
    print("\n💡 使用建议:")
    print("1. 打开浏览器访问 http://localhost:5000")
    print("2. 上传一分一档表、最低分数线、招生计划三个Excel文件")
    print("3. 输入考生位次，获取推荐并体验AI分析功能")

if __name__ == "__main__":
    main() 