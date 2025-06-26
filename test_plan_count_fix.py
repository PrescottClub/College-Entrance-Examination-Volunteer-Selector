#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试计划人数数据清理功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor

def test_clean_plan_count():
    """测试计划人数清理功能"""
    print("🧪 测试计划人数清理功能")
    print("=" * 50)
    
    processor = DataProcessor()
    
    # 测试用例
    test_cases = [
        ("3人", 3),
        ("3人4人5人", 12),  # 3+4+5=12
        ("3人3人4人5人3人5人4人3人3人4人3人3人3人6人4人4人2人7人4人4人4人3人6人3人", 91),  # 实际错误数据
        ("5", 5),
        ("", 0),
        (None, 0),
        ("10人", 10),
        ("abc", 0),
        ("2.5", 2),
        (15, 15)
    ]
    
    print("测试结果:")
    for input_val, expected in test_cases:
        result = processor.clean_plan_count(input_val)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_val}' -> {result} (期望: {expected})")
    
    print("\n" + "=" * 50)
    print("✅ 计划人数清理功能测试完成")

def test_data_loading_with_fix():
    """测试修复后的数据加载"""
    print("\n🔄 测试修复后的数据加载")
    print("=" * 50)
    
    processor = DataProcessor()
    
    # 测试文件路径
    score_rank_file = "static/uploads/score_rank_xlsx"
    cutoff_file = "static/uploads/cutoff_xlsx"  
    plan_file = "static/uploads/plan_G--2024_.xlsx"
    
    # 检查文件是否存在
    files = [score_rank_file, cutoff_file, plan_file]
    file_names = ["一分一档表", "最低分数线", "招生计划"]
    
    all_exist = True
    for file_path, file_name in zip(files, file_names):
        if os.path.exists(file_path):
            print(f"✅ {file_name}文件存在")
        else:
            print(f"❌ {file_name}文件不存在: {file_path}")
            all_exist = False
    
    if not all_exist:
        print("⚠️ 部分文件不存在，跳过数据加载测试")
        return
    
    # 加载数据
    try:
        success, message = processor.load_excel_files(score_rank_file, cutoff_file, plan_file)
        print(f"\n📊 数据加载结果: {message}")
        
        if success:
            print(f"📈 一分一档表: {len(processor.score_rank_df)}行")
            print(f"📉 最低分数线: {len(processor.cutoff_df)}行") 
            print(f"📋 招生计划: {len(processor.plan_df)}行")
            
            # 检查计划人数列
            if 'plan_count' in processor.plan_df.columns:
                print(f"\n🔍 计划人数列检查:")
                print(f"  数据类型: {processor.plan_df['plan_count'].dtype}")
                print(f"  样本数据: {processor.plan_df['plan_count'].head().tolist()}")
                
                # 检查是否还有问题数据
                problematic = processor.plan_df[processor.plan_df['plan_count'].astype(str).str.contains('人.*人', na=False)]
                if len(problematic) > 0:
                    print(f"  ⚠️ 仍有{len(problematic)}条问题数据")
                else:
                    print(f"  ✅ 计划人数数据已清理")
            
            # 处理数据
            print("\n🔄 开始数据处理...")
            success, message = processor.process_data()
            print(f"处理结果: {message}")
            
            if success and processor.merged_df is not None:
                print(f"✅ 合并数据: {len(processor.merged_df)}行")
                return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    print("🚀 计划人数修复测试开始")
    print("=" * 60)
    
    # 测试清理功能
    test_clean_plan_count()
    
    # 测试数据加载
    test_data_loading_with_fix()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
