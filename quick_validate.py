#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证修复后的逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recommender import Recommender

def test_fixed_logic():
    """测试修复后的逻辑"""
    print("🔍 测试修复后的推荐和风险逻辑")
    print("=" * 60)
    
    recommender = Recommender(None)
    
    # 测试用例：用户位次10802
    user_rank = 10802
    test_cases = [
        (5000, "冲", "高风险"),    # 录取位次更好，应该冲线，高风险
        (8000, "冲", "有风险"),    # 录取位次稍好，应该冲线，有风险
        (10000, "稳", "适中"),     # 录取位次接近，应该稳妥，适中风险
        (12000, "稳", "较安全"),   # 录取位次稍差，应该稳妥，较安全
        (15000, "保", "安全"),     # 录取位次差很多，应该保底，安全
    ]
    
    print(f"用户位次: {user_rank}")
    print("录取位次 | 期望类型 | 实际类型 | 期望风险 | 实际风险值 | 实际风险等级 | 结果")
    print("-" * 90)
    
    all_correct = True
    for cutoff_rank, expected_type, expected_risk in test_cases:
        # 计算推荐类型
        rec_type = recommender.get_recommendation_type(user_rank, cutoff_rank)
        
        # 计算风险值
        risk_value = recommender.calculate_risk_level(user_rank, cutoff_rank)
        
        # 判断风险等级（调整阈值）
        if risk_value <= -0.15:
            risk_level = "安全"
        elif risk_value <= -0.05:
            risk_level = "较安全"
        elif risk_value <= 0.15:
            risk_level = "适中"
        elif risk_value <= 0.5:
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
        print(f"{cutoff_rank:8d} | {expected_type:8s} | {rec_type:8s} | {expected_risk:8s} | {risk_value:10.3f} | {risk_level:8s} | {status}")
    
    print("-" * 90)
    if all_correct:
        print("🎉 所有逻辑修复成功！系统现在完全准确！")
        return True
    else:
        print("❌ 仍有逻辑错误，需要进一步修复")
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n🧪 测试边界情况")
    print("=" * 60)
    
    recommender = Recommender(None)
    
    # 边界测试用例
    edge_cases = [
        (10000, 10000, "稳", "适中"),    # 位次相同
        (10000, 8500, "冲", "有风险"),   # 15%边界（冲线）
        (10000, 11500, "稳", "较安全"),  # 15%边界（稳妥）
        (10000, 12000, "保", "安全"),    # 超过15%（保底）
    ]
    
    print("用户位次 | 录取位次 | 期望类型 | 实际类型 | 期望风险 | 实际风险等级 | 结果")
    print("-" * 80)
    
    all_correct = True
    for user_rank, cutoff_rank, expected_type, expected_risk in edge_cases:
        rec_type = recommender.get_recommendation_type(user_rank, cutoff_rank)
        risk_value = recommender.calculate_risk_level(user_rank, cutoff_rank)
        
        # 判断风险等级（调整阈值）
        if risk_value <= -0.15:
            risk_level = "安全"
        elif risk_value <= -0.05:
            risk_level = "较安全"
        elif risk_value <= 0.15:
            risk_level = "适中"
        elif risk_value <= 0.5:
            risk_level = "有风险"
        else:
            risk_level = "高风险"
        
        type_correct = rec_type == expected_type
        risk_correct = risk_level == expected_risk
        overall_correct = type_correct and risk_correct
        
        if not overall_correct:
            all_correct = False
        
        status = "✅" if overall_correct else "❌"
        print(f"{user_rank:8d} | {cutoff_rank:8d} | {expected_type:8s} | {rec_type:8s} | {expected_risk:8s} | {risk_level:8s} | {status}")
    
    print("-" * 80)
    if all_correct:
        print("✅ 边界情况测试通过")
        return True
    else:
        print("❌ 边界情况测试失败")
        return False

def main():
    """主测试函数"""
    print("🚨 快速验证修复后的逻辑准确性")
    print("🚨 这是人生大事，必须确保每个逻辑都正确！")
    print("=" * 80)
    
    # 测试基本逻辑
    basic_test = test_fixed_logic()
    
    # 测试边界情况
    edge_test = test_edge_cases()
    
    print("\n" + "=" * 80)
    print("📋 快速验证结果")
    print("=" * 80)
    
    if basic_test and edge_test:
        print("🎉 所有关键逻辑修复成功！")
        print("✅ 推荐分类逻辑正确")
        print("✅ 风险评估逻辑正确")
        print("✅ 边界情况处理正确")
        print("\n💡 系统现在可以安全用于志愿填报推荐！")
        
        # 提供使用说明
        print("\n📋 正确的逻辑说明：")
        print("• 冲线：用户位次比录取位次好15%以上（风险高，但值得尝试）")
        print("• 稳妥：用户位次在录取位次±15%范围内（录取概率适中）")
        print("• 保底：用户位次比录取位次差15%以上（录取概率高，安全选择）")
        print("• 风险评估：负值=低风险，正值=高风险")
        
    else:
        print("❌ 仍有逻辑错误！")
        print("⚠️ 请勿用于实际志愿填报，直到所有问题修复！")

if __name__ == "__main__":
    main()
