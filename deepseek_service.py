from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
import json

class DeepSeekService:
    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
    
    def generate_major_analysis(self, school_name, major_name, user_rank, cutoff_rank):
        """生成专业分析和建议"""
        try:
            prompt = f"""
作为一名专业的高考志愿填报顾问，请为以下情况提供分析和建议：

院校：{school_name}
专业：{major_name}
考生2025年位次：{user_rank}
该专业2024年录取位次：{cutoff_rank}（用于预测2025年录取难度）

请从以下几个角度进行分析：
1. 专业介绍（主要学什么、就业方向）
2. 院校实力分析（该专业在学校的地位、师资力量）
3. 录取难度分析（基于2024年数据预测2025年录取可能性）
4. 就业前景和发展建议
5. 是否建议填报此专业

请用简洁专业的语言回答，字数控制在200字以内。
            """
            
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位专业的高考志愿填报顾问，具有丰富的院校专业知识和招生经验。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                temperature=0.7
            )
            
            return {
                'success': True,
                'analysis': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'analysis': f'专业分析生成失败: {str(e)}'
            }
    
    def generate_volunteer_strategy(self, recommendations_data, user_rank, track):
        """生成整体志愿填报策略建议"""
        try:
            # 统计推荐结果
            chong_count = len(recommendations_data.get('冲', []))
            wen_count = len(recommendations_data.get('稳', []))
            bao_count = len(recommendations_data.get('保', []))
            
            prompt = f"""
作为高考志愿填报专家，请为以下考生提供2025年志愿填报策略：

考生情况：
- 2025年位次：{user_rank}
- 科目：{track}
- 基于2024年数据的推荐结果：冲线{chong_count}个，稳妥{wen_count}个，保底{bao_count}个

请提供：
1. 志愿填报整体策略（冲稳保比例建议）
2. 选择院校时的注意事项
3. 专业选择建议
4. 填报顺序建议
5. 基于历史数据预测的风险提醒

要求简洁实用，字数控制在300字以内。
            """
            
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位经验丰富的高考志愿填报专家，善于为考生制定科学的填报策略。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                temperature=0.7
            )
            
            return {
                'success': True,
                'strategy': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'strategy': f'策略建议生成失败: {str(e)}'
            }
    
    def test_connection(self):
        """测试DeepSeek API连接"""
        try:
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "user", "content": "请回复'连接成功'"}
                ],
                stream=False
            )
            
            return {
                'success': True,
                'message': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'API连接失败: {str(e)}'
            } 