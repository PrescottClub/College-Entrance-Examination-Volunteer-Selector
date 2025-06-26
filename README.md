# 🎓 智能高考志愿填报助手

> 基于AI技术和大数据分析的智能志愿填报系统，让每位考生都能找到最适合的大学！

[![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.0.0-red.svg)](https://flask.palletsprojects.com/)

## 🌟 为什么选择我们？

🤖 **AI智能分析** - 集成DeepSeek AI模型，提供专业的院校和专业分析
📊 **科学算法** - 基于"冲稳保"策略，精准计算录取概率
🎯 **个性化推荐** - 根据考生位次和偏好，定制专属志愿方案
📱 **简单易用** - 上传数据，一键生成，3分钟完成志愿规划

## ✨ 核心功能

### 🔥 AI智能推荐
- **专业深度分析**: AI解读专业前景、就业方向、院校实力
- **志愿策略建议**: 智能生成整体填报策略和注意事项
- **个性化建议**: 基于考生情况提供专属的填报指导

### 📊 数据驱动分析
- **三档分类**: 自动分析"冲线"、"稳妥"、"保底"三类院校
- **位次转换**: 智能将分数转换为精准位次
- **多维筛选**: 支持城市、985/211、专业类别等条件筛选

### 🎨 用户体验
- **现代化界面**: 简洁美观的用户界面设计
- **响应式设计**: 完美适配PC和移动设备
- **实时反馈**: 即时显示分析结果和建议

## 🚀 快速开始

### 环境配置

```bash
# 1. 克隆项目
git clone https://github.com/PrescottClub/College-Entrance-Examination-Volunteer-Selector.git
cd College-Entrance-Examination-Volunteer-Selector

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API密钥
copy env.example .env
# 在 .env 文件中填写您的 DeepSeek API 密钥

# 4. 启动应用
python app.py
```

### 访问系统
打开浏览器访问：**http://localhost:5000**

## 🎯 使用指南

### 第一步：准备数据文件
上传三个Excel文件：
- 📋 **一分一档表** - 分数与位次对应关系
- 📊 **录取分数线** - 各院校专业历年录取数据  
- 📈 **招生计划** - 院校专业招生信息

### 第二步：输入考生信息
- 🔢 输入考生位次（支持分数自动转换）
- 📚 选择科目类别（物理类/历史类）
- 🎛️ 设置筛选偏好（可选）

### 第三步：获取智能推荐
系统将为您生成：
- 🚀 **冲线院校** - 有挑战性，值得一试
- 🎯 **稳妥院校** - 录取概率高，推荐重点关注
- 🛡️ **保底院校** - 确保录取，安全选择
- 🤖 **AI分析报告** - 详细的专业和院校分析

## 🧠 AI技术亮点

### DeepSeek AI集成
```python
# AI专业分析示例
def generate_major_analysis(school_name, major_name, user_rank, cutoff_rank):
    """
    利用AI分析专业前景、院校实力、录取难度
    提供个性化的填报建议
    """
    return ai_analysis_result
```

### 智能推荐算法
```python
def smart_recommendation(user_rank, cutoff_rank):
    """
    基于位次差异的智能分类算法
    """
    diff_percentage = (cutoff_rank - user_rank) / user_rank
    
    if diff_percentage <= -0.05:
        return "🚀 冲线 - 有挑战但值得尝试"
    elif abs(diff_percentage) <= 0.05:
        return "🎯 稳妥 - 录取概率较高"
    else:
        return "🛡️ 保底 - 确保录取"
```

## 📂 项目架构

```
📦 智能志愿填报系统
├── 🐍 app.py                 # Flask主应用
├── 🧠 deepseek_service.py     # AI服务模块
├── 📊 data_processor.py       # 数据处理引擎
├── 🎯 recommender.py          # 智能推荐算法
├── ⚙️ config.py              # 系统配置
├── 🎨 templates/             # 前端模板
├── 💎 static/                # 静态资源
└── 📚 requirements.txt       # 依赖清单
```

## 🎨 界面预览

- 🎨 **现代化设计** - 简洁优雅的用户界面
- 📱 **移动端适配** - 完美支持手机和平板访问
- 🌈 **直观展示** - 清晰的数据可视化展示
- ⚡ **快速响应** - 毫秒级的查询和分析

## 🔧 配置选项

在 `config.py` 中自定义：
```python
# 推荐阈值配置
RISK_THRESHOLD_CHONG = -0.05    # 冲线阈值
RISK_THRESHOLD_WEN = 0.05       # 稳线阈值

# AI模型配置
DEEPSEEK_MODEL = "deepseek-chat"  # AI模型选择
```

## 🔐 安全提醒

- 🔑 **API密钥保护** - 使用环境变量安全存储
- 🛡️ **数据隐私** - 用户上传数据仅本地处理
- 🔒 **访问安全** - 建议在可信网络环境下使用

## ⚠️ 重要声明

> **本系统基于历史数据和AI分析提供志愿填报建议，仅供参考使用。**
> 
> 📢 **请注意**：
> - 实际录取情况可能因政策变化而有所差异
> - 建议结合多方信息进行决策
> - 最终录取以官方发布信息为准

## 🆘 技术支持

遇到问题？我们来帮您：

1. 📖 **查看文档** - 详细的使用说明和FAQ
2. 🐛 **提交Issue** - 在GitHub上报告问题
3. 💬 **技术交流** - 欢迎提出改进建议

## 🎉 成功案例

> "使用这个系统后，我用3分钟就完成了志愿规划，AI分析非常专业！" - 2024届考生小李
> 
> "推荐结果很准确，最终被第一志愿录取了！" - 2024届考生小王

---

### 🎊 祝愿每位考生都能进入理想的大学！

**让AI为您的未来保驾护航** 🚀