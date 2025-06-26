#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件上传功能
"""

import requests
import os

def test_upload():
    """测试文件上传"""
    print("🧪 测试文件上传功能")
    print("=" * 50)
    
    # 检查文件是否存在
    files_to_check = [
        "static/uploads/score_rank_xlsx",
        "static/uploads/cutoff_xlsx", 
        "static/uploads/plan_G--2024_.xlsx"
    ]
    
    file_names = ["一分一档表", "最低分数线", "招生计划"]
    
    for file_path, file_name in zip(files_to_check, file_names):
        if os.path.exists(file_path):
            print(f"✅ {file_name}文件存在: {file_path}")
        else:
            print(f"❌ {file_name}文件不存在: {file_path}")
            return False
    
    # 模拟文件上传
    try:
        url = 'http://localhost:5000/upload'
        
        # 准备文件
        files = {
            'score_rank_file': ('score_rank.xlsx', open(files_to_check[0], 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            'cutoff_file': ('cutoff.xlsx', open(files_to_check[1], 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            'plan_file': ('plan.xlsx', open(files_to_check[2], 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        print("\n🔄 开始上传文件...")
        response = requests.post(url, files=files)
        
        # 关闭文件
        for file_tuple in files.values():
            file_tuple[1].close()
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 上传成功!")
                return True
            else:
                print(f"❌ 上传失败: {result.get('message')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 上传过程中出错: {e}")
        return False

def test_recommend():
    """测试推荐功能"""
    print("\n🎯 测试推荐功能")
    print("=" * 50)
    
    try:
        url = 'http://localhost:5000/recommend'
        data = {
            'rank': 10802,
            'track': '物理'
        }
        
        print("🔄 开始获取推荐...")
        response = requests.post(url, json=data)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 推荐成功!")
                data = result.get('data', {})
                for rec_type in ['冲', '稳', '保']:
                    count = len(data.get(rec_type, []))
                    print(f"   {rec_type}线推荐: {count}个")
                return True
            else:
                print(f"❌ 推荐失败: {result.get('message')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 推荐过程中出错: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 文件上传和推荐功能测试")
    print("=" * 60)
    
    # 测试上传
    upload_success = test_upload()
    
    if upload_success:
        # 测试推荐
        recommend_success = test_recommend()
        
        if recommend_success:
            print("\n🎉 所有测试通过！")
        else:
            print("\n❌ 推荐测试失败")
    else:
        print("\n❌ 上传测试失败，跳过推荐测试")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
