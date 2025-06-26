#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广西高考志愿填报系统测试
测试修复后的功能和广西新高考政策适配
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
from recommender import Recommender
from deepseek_service import DeepSeekService

def test_data_loading():
    """测试数据加载功能"""
    print("=" * 60)
    print("🧪 测试数据加载功能")
    print("=" * 60)
    
    processor = DataProcessor()
    
    # 测试文件路径
    score_rank_file = "static/uploads/score_rank_xlsx"
    cutoff_file = "static/uploads/cutoff_xlsx"  
    plan_file = "static/uploads/plan_G--2024_.xlsx"
    
    # 检查文件是否存在
    files = [score_rank_file, cutoff_file, plan_file]
    file_names = ["一分一档表", "最低分数线", "招生计划"]
    
    for file_path, file_name in zip(files, file_names):
        if os.path.exists(file_path):
            print(f"✅ {file_name}文件存在: {file_path}")
        else:
            print(f"❌ {file_name}文件不存在: {file_path}")
            return False
    
    # 加载数据
    success, message = processor.load_excel_files(score_rank_file, cutoff_file, plan_file)
    print(f"\n📊 数据加载结果: {message}")
    
    if success:
        # 显示数据统计
        print(f"📈 一分一档表: {len(processor.score_rank_df)}行")
        print(f"📉 最低分数线: {len(processor.cutoff_df)}行") 
        print(f"📋 招生计划: {len(processor.plan_df)}行")
        
        # 处理数据
        print("\n🔄 开始数据处理...")
        success, message = processor.process_data()
        print(f"处理结果: {message}")
        
        if success and processor.merged_df is not None:
            print(f"✅ 合并数据: {len(processor.merged_df)}行")
            return True
    
    return False

def test_recommendation_system():
    """测试推荐系统"""
    print("\n" + "=" * 60)
    print("🎯 测试推荐系统")
    print("=" * 60)
    
    # 初始化组件
    processor = DataProcessor()
    deepseek_service = DeepSeekService()
    recommender = Recommender(processor, deepseek_service)
    
    # 加载数据
    score_rank_file = "static/uploads/score_rank_xlsx"
    cutoff_file = "static/uploads/cutoff_xlsx"  
    plan_file = "static/uploads/plan_G--2024_.xlsx"
    
    success, message = processor.load_excel_files(score_rank_file, cutoff_file, plan_file)
    if not success:
        print(f"❌ 数据加载失败: {message}")
        return False
    
    success, message = processor.process_data()
    if not success:
        print(f"❌ 数据处理失败: {message}")
        return False
    
    # 测试不同位次的推荐
    test_cases = [
        {"rank": 5000, "track": "物理", "desc": "高分考生"},
        {"rank": 15000, "track": "物理", "desc": "中等偏上考生"},
        {"rank": 30000, "track": "历史", "desc": "中等考生"},
        {"rank": 50000, "track": "物理", "desc": "中等偏下考生"}
    ]
    
    for case in test_cases:
        print(f"\n🧑‍🎓 测试{case['desc']} (位次: {case['rank']}, 科目: {case['track']})")
        print("-" * 50)
        
        # 生成推荐
        result = recommender.generate_recommendations(
            user_rank=case['rank'],
            track=case['track'],
            filters=None
        )
        
        if result['success']:
            print(f"✅ {result['message']}")
            
            # 显示推荐统计
            data = result.get('data', {})
            for rec_type in ['冲', '稳', '保']:
                count = len(data.get(rec_type, []))
                print(f"   {rec_type}线推荐: {count}个")
                
                # 显示前3个推荐
                if count > 0:
                    for i, rec in enumerate(data[rec_type][:3]):
                        school = rec.get('school_name', '未知')
                        major = rec.get('major_name', '未知')
                        rank = rec.get('cutoff_rank', 0)
                        print(f"     {i+1}. {school} - {major} (位次:{rank})")
        else:
            print(f"❌ {result['message']}")
    
    return True

def test_guangxi_specific_features():
    """测试广西新高考特定功能"""
    print("\n" + "=" * 60)
    print("🏫 测试广西新高考特定功能")
    print("=" * 60)
    
    processor = DataProcessor()
    recommender = Recommender(processor, None)
    
    # 测试新的推荐类型判断
    test_ranks = [
        (10000, 9000, "冲"),   # 用户位次10000，录取位次9000，应该是冲
        (10000, 10000, "稳"),  # 位次相同，应该是稳
        (10000, 11500, "保"),  # 录取位次更低，应该是保
    ]
    
    print("🎯 测试新高考推荐类型判断:")
    for user_rank, cutoff_rank, expected in test_ranks:
        result = recommender.get_recommendation_type_new_gaokao(user_rank, cutoff_rank)
        status = "✅" if result == expected else "❌"
        print(f"   {status} 用户位次{user_rank} vs 录取位次{cutoff_rank} -> {result} (期望:{expected})")
    
    # 测试广西特定建议
    print("\n💡 测试广西特定建议:")
    advice_physics = recommender.add_guangxi_specific_advice({}, 15000, "物理")
    advice_history = recommender.add_guangxi_specific_advice({}, 15000, "历史")
    
    print("   物理类建议:")
    for advice in advice_physics[:3]:
        print(f"     • {advice}")
    
    print("   历史类建议:")
    for advice in advice_history[:3]:
        print(f"     • {advice}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 广西高考志愿填报系统测试开始")
    print("=" * 80)
    
    # 测试数据加载
    if not test_data_loading():
        print("❌ 数据加载测试失败，停止后续测试")
        return
    
    # 测试推荐系统
    if not test_recommendation_system():
        print("❌ 推荐系统测试失败")
        return
    
    # 测试广西特定功能
    if not test_guangxi_specific_features():
        print("❌ 广西特定功能测试失败")
        return
    
    print("\n" + "=" * 80)
    print("🎉 所有测试完成！系统功能正常")
    print("=" * 80)
    
    # 提供使用建议
    print("\n📋 使用建议:")
    print("1. 确保上传的Excel文件格式正确")
    print("2. 一分一档表应包含：总分、人数、累计人数、名次")
    print("3. 最低分数线应包含：院校代码、院校名称、专业组、投档最低分")
    print("4. 招生计划应包含：年份、学校、招生代码、专业等信息")
    print("5. 2025年是广西新高考第二年，数据仅供参考")

if __name__ == "__main__":
    main()
