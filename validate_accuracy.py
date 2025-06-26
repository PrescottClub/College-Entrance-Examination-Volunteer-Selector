#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高考志愿填报系统数据准确性验证
这是人生大事，必须确保每个逻辑都正确！
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
from recommender import Recommender
from deepseek_service import DeepSeekService

def validate_risk_calculation():
    """验证风险计算逻辑的准确性"""
    print("🔍 验证风险计算逻辑")
    print("=" * 60)
    
    recommender = Recommender(None)
    
    # 测试用例：用户位次10802
    user_rank = 10802
    test_cases = [
        (5000, "冲线", "高风险"),    # 录取位次更好，应该高风险
        (8000, "冲线", "有风险"),    # 录取位次稍好，应该有风险
        (10000, "稳妥", "适中"),     # 录取位次接近，应该适中
        (12000, "稳妥", "较安全"),   # 录取位次稍差，应该较安全
        (15000, "保底", "安全"),     # 录取位次差很多，应该安全
    ]
    
    print(f"用户位次: {user_rank}")
    print("录取位次 | 类型 | 期望风险 | 实际风险值 | 实际风险等级 | 结果")
    print("-" * 80)
    
    all_correct = True
    for cutoff_rank, expected_type, expected_risk in test_cases:
        # 计算推荐类型
        rec_type = recommender.get_recommendation_type(user_rank, cutoff_rank)
        
        # 计算风险值
        risk_value = recommender.calculate_risk_level(user_rank, cutoff_rank)
        
        # 判断风险等级
        if risk_value <= -0.2:
            risk_level = "安全"
        elif risk_value <= -0.1:
            risk_level = "较安全"
        elif risk_value <= 0.1:
            risk_level = "适中"
        elif risk_value <= 0.3:
            risk_level = "有风险"
        else:
            risk_level = "高风险"
        
        # 检查是否正确
        type_correct = rec_type == expected_type
        risk_correct = risk_level == expected_risk
        overall_correct = type_correct and risk_correct
        
        if not overall_correct:
            all_correct = False
        
        status = "✅" if overall_correct else "❌"
        print(f"{cutoff_rank:8d} | {rec_type:4s} | {expected_risk:8s} | {risk_value:10.3f} | {risk_level:8s} | {status}")
    
    print("-" * 80)
    if all_correct:
        print("✅ 风险计算逻辑完全正确！")
    else:
        print("❌ 风险计算逻辑存在错误，需要修复！")
    
    return all_correct

def validate_recommendation_logic():
    """验证推荐分类逻辑"""
    print("\n🎯 验证推荐分类逻辑")
    print("=" * 60)
    
    recommender = Recommender(None)
    user_rank = 10802
    
    # 测试冲稳保分类逻辑
    test_cases = [
        (5000, "冲"),     # 录取位次比用户位次好很多
        (8000, "冲"),     # 录取位次比用户位次好
        (9500, "冲"),     # 录取位次比用户位次好约12%
        (10000, "稳"),    # 录取位次接近用户位次
        (10500, "稳"),    # 录取位次略差于用户位次
        (11500, "稳"),    # 录取位次差于用户位次约6%
        (12000, "保"),    # 录取位次比用户位次差约11%
        (15000, "保"),    # 录取位次比用户位次差很多
    ]
    
    print(f"用户位次: {user_rank}")
    print("录取位次 | 位次差异 | 期望类型 | 实际类型 | 结果")
    print("-" * 60)
    
    all_correct = True
    for cutoff_rank, expected_type in test_cases:
        actual_type = recommender.get_recommendation_type(user_rank, cutoff_rank)
        diff_pct = (cutoff_rank - user_rank) / user_rank * 100
        
        correct = actual_type == expected_type
        if not correct:
            all_correct = False
        
        status = "✅" if correct else "❌"
        print(f"{cutoff_rank:8d} | {diff_pct:8.1f}% | {expected_type:8s} | {actual_type:8s} | {status}")
    
    print("-" * 60)
    if all_correct:
        print("✅ 推荐分类逻辑完全正确！")
    else:
        print("❌ 推荐分类逻辑存在错误，需要修复！")
    
    return all_correct

def validate_data_processing():
    """验证数据处理的准确性"""
    print("\n📊 验证数据处理准确性")
    print("=" * 60)
    
    processor = DataProcessor()
    
    # 检查文件是否存在
    files = [
        "static/uploads/score_rank_xlsx",
        "static/uploads/cutoff_xlsx", 
        "static/uploads/plan_G--2024_.xlsx"
    ]
    
    for i, file_path in enumerate(files):
        file_names = ["一分一档表", "最低分数线", "招生计划"]
        if os.path.exists(file_path):
            print(f"✅ {file_names[i]}文件存在")
        else:
            print(f"❌ {file_names[i]}文件不存在: {file_path}")
            return False
    
    # 加载和处理数据
    try:
        success, message = processor.load_excel_files(*files)
        if not success:
            print(f"❌ 数据加载失败: {message}")
            return False
        
        success, message = processor.process_data()
        if not success:
            print(f"❌ 数据处理失败: {message}")
            return False
        
        # 验证数据质量
        print(f"✅ 一分一档表: {len(processor.score_rank_df)}行")
        print(f"✅ 最低分数线: {len(processor.cutoff_df)}行")
        print(f"✅ 招生计划: {len(processor.plan_df)}行")
        print(f"✅ 合并数据: {len(processor.merged_df)}行")
        
        # 检查关键列是否存在
        required_columns = ['school_name', 'cutoff_rank', 'cutoff_score', 'major_group']
        missing_columns = []
        for col in required_columns:
            if col not in processor.merged_df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"❌ 缺少关键列: {missing_columns}")
            return False
        
        # 检查数据有效性
        valid_ranks = processor.merged_df['cutoff_rank'].dropna()
        if len(valid_ranks) == 0:
            print("❌ 没有有效的位次数据")
            return False
        
        print(f"✅ 有效位次数据: {len(valid_ranks)}条")
        print(f"✅ 位次范围: {int(valid_ranks.min())} - {int(valid_ranks.max())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据处理过程中出错: {e}")
        return False

def validate_end_to_end():
    """端到端验证推荐系统"""
    print("\n🚀 端到端验证推荐系统")
    print("=" * 60)
    
    # 初始化组件
    processor = DataProcessor()
    deepseek_service = DeepSeekService()
    recommender = Recommender(processor)
    
    # 加载数据
    files = [
        "static/uploads/score_rank_xlsx",
        "static/uploads/cutoff_xlsx", 
        "static/uploads/plan_G--2024_.xlsx"
    ]
    
    success, message = processor.load_excel_files(*files)
    if not success:
        print(f"❌ 数据加载失败: {message}")
        return False
    
    success, message = processor.process_data()
    if not success:
        print(f"❌ 数据处理失败: {message}")
        return False
    
    # 测试推荐生成
    test_cases = [
        (5000, "物理", "高分考生"),
        (10802, "物理", "中等偏上考生"),
        (20000, "历史", "中等考生"),
        (50000, "物理", "中等偏下考生")
    ]
    
    all_passed = True
    for user_rank, track, desc in test_cases:
        print(f"\n测试{desc} (位次: {user_rank}, 科目: {track})")
        
        result = recommender.generate_recommendations(user_rank, track, None)
        
        if not result['success']:
            print(f"❌ 推荐失败: {result['message']}")
            all_passed = False
            continue
        
        data = result.get('data', {})
        chong_count = len(data.get('冲', []))
        wen_count = len(data.get('稳', []))
        bao_count = len(data.get('保', []))
        total_count = chong_count + wen_count + bao_count
        
        print(f"  冲线: {chong_count}个, 稳妥: {wen_count}个, 保底: {bao_count}个")
        print(f"  总计: {total_count}个推荐")
        
        # 验证推荐的合理性
        if total_count == 0:
            print("  ❌ 没有生成任何推荐")
            all_passed = False
        elif total_count < 10:
            print("  ⚠️ 推荐数量较少，可能需要调整筛选条件")
        else:
            print("  ✅ 推荐数量合理")
        
        # 验证每个推荐的风险评估
        for rec_type, recommendations in data.items():
            for rec in recommendations[:3]:  # 检查前3个
                risk_value = rec.get('risk_level', 0)
                cutoff_rank = rec.get('cutoff_rank', 0)
                
                # 验证风险值的合理性
                if rec_type == '冲' and risk_value >= 0:
                    print(f"  ❌ 冲线推荐风险值异常: {risk_value}")
                    all_passed = False
                elif rec_type == '保' and risk_value <= -0.1:
                    print(f"  ❌ 保底推荐风险值异常: {risk_value}")
                    all_passed = False
    
    if all_passed:
        print("\n✅ 端到端验证完全通过！")
    else:
        print("\n❌ 端到端验证发现问题！")
    
    return all_passed

def main():
    """主验证函数"""
    print("🚨 高考志愿填报系统数据准确性验证")
    print("🚨 这是人生大事，必须确保每个逻辑都正确！")
    print("=" * 80)
    
    # 执行所有验证
    validations = [
        ("风险计算逻辑", validate_risk_calculation),
        ("推荐分类逻辑", validate_recommendation_logic),
        ("数据处理准确性", validate_data_processing),
        ("端到端系统验证", validate_end_to_end)
    ]
    
    results = []
    for name, func in validations:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}验证过程中出错: {e}")
            results.append((name, False))
    
    # 总结结果
    print("\n" + "=" * 80)
    print("📋 验证结果总结")
    print("=" * 80)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:20s} | {status}")
        if not passed:
            all_passed = False
    
    print("=" * 80)
    if all_passed:
        print("🎉 所有验证通过！系统数据准确性得到保证！")
        print("💡 可以放心使用系统进行志愿填报推荐")
    else:
        print("🚨 发现问题！请立即修复后再使用！")
        print("⚠️ 在修复所有问题之前，请勿用于实际志愿填报！")
    
    return all_passed

if __name__ == "__main__":
    main()
