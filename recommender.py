import pandas as pd
from config import RISK_THRESHOLD_CHONG, RISK_THRESHOLD_WEN

class Recommender:
    def __init__(self, data_processor):
        self.data_processor = data_processor
    
    def get_recommendation_type(self, user_rank, cutoff_rank):
        """判断推荐类型：冲/稳/保 - 最终修正版本"""
        if pd.isna(cutoff_rank) or pd.isna(user_rank):
            return "未知"

        try:
            # 正确的志愿填报逻辑：
            # 冲线：选择录取位次比自己好的学校（录取位次更小，更难考上）
            # 稳妥：选择录取位次与自己接近的学校（录取概率适中）
            # 保底：选择录取位次比自己差的学校（录取位次更大，容易考上）

            if cutoff_rank <= user_rank * 0.85:  # 录取位次比用户位次好15%以上 - 冲线
                return "冲"
            elif cutoff_rank <= user_rank * 1.15:  # 录取位次在用户位次的85%-115%范围 - 稳妥
                return "稳"
            else:  # 录取位次比用户位次差15%以上 - 保底
                return "保"
        except:
            return "未知"
    
    def calculate_risk_level(self, user_rank, cutoff_rank):
        """计算风险等级 - 修正逻辑确保准确性"""
        try:
            if pd.isna(cutoff_rank) or pd.isna(user_rank):
                return 0

            # 风险评估逻辑（修正）：
            # 位次越小越好，用户位次与录取位次的比较：
            # user_rank < cutoff_rank：用户更优秀，风险低（负值）
            # user_rank > cutoff_rank：用户较差，风险高（正值）

            # 计算风险比例
            risk_ratio = (user_rank - cutoff_rank) / cutoff_rank

            # 返回风险值：
            # 负值 = 用户位次比录取位次好（低风险，容易录取）
            # 正值 = 用户位次比录取位次差（高风险，难以录取）
            return risk_ratio
        except:
            return 0
    
    def calculate_diff_percentage(self, user_rank, cutoff_rank):
        """计算位次差异百分比"""
        try:
            if pd.isna(cutoff_rank) or pd.isna(user_rank):
                return None
            return (cutoff_rank - user_rank) / user_rank
        except:
            return None
    
    def filter_data(self, user_rank, track, filters=None):
        """根据条件筛选数据 - 适配实际数据结构"""
        if self.data_processor.merged_df is None:
            return pd.DataFrame()

        df = self.data_processor.merged_df.copy()

        # 清理数据：确保位次是数值类型
        df['cutoff_rank'] = pd.to_numeric(df['cutoff_rank'], errors='coerce')
        df = df.dropna(subset=['cutoff_rank'])

        print(f"原始数据量: {len(df)}")

        # 基础筛选：科目要求（如果有track列的话）
        if 'track' in df.columns:
            track_filtered = df[df['track'] == track]
            if len(track_filtered) > 0:
                df = track_filtered
                print(f"科目'{track}'筛选后: {len(df)}条")
            else:
                print(f"警告：科目'{track}'筛选后无数据，使用所有数据")

        # 应用用户筛选条件
        if filters:
            # 985筛选
            if filters.get('is_985') and 'is_985' in df.columns:
                df = df[df['is_985'] == True]
                print(f"985筛选后: {len(df)}条")

            # 211筛选
            if filters.get('is_211') and 'is_211' in df.columns:
                df = df[df['is_211'] == True]
                print(f"211筛选后: {len(df)}条")

            # 专业筛选
            if filters.get('majors') and 'major_name' in df.columns:
                df = df[df['major_name'].str.contains('|'.join(filters['majors']), na=False)]
                print(f"专业筛选后: {len(df)}条")

        # 位次范围筛选 - 考虑年份差异，适当放宽范围
        # 冲线：用户位次的0.5-1.2倍，稳妥：0.8-1.5倍，保底：1.2-3倍
        min_rank = max(1, int(user_rank * 0.3))  # 最小位次
        max_rank = int(user_rank * 3.0)          # 最大位次

        df = df[(df['cutoff_rank'] >= min_rank) & (df['cutoff_rank'] <= max_rank)]

        print(f"位次范围筛选后: {len(df)}条，用户位次: {user_rank}，筛选范围: {min_rank}-{max_rank}")

        # 如果数据太少，放宽范围
        if len(df) < 10:
            print("数据量过少，放宽位次范围...")
            min_rank = max(1, int(user_rank * 0.1))
            max_rank = int(user_rank * 5.0)
            df = self.data_processor.merged_df.copy()
            df['cutoff_rank'] = pd.to_numeric(df['cutoff_rank'], errors='coerce')
            df = df.dropna(subset=['cutoff_rank'])
            df = df[(df['cutoff_rank'] >= min_rank) & (df['cutoff_rank'] <= max_rank)]
            print(f"放宽后数据量: {len(df)}条")

        return df
    
    def generate_recommendations(self, user_rank, track, filters=None, limit_per_type=50):
        """生成推荐结果 - 改进错误提示"""
        try:
            # 筛选数据
            filtered_df = self.filter_data(user_rank, track, filters)
            
            if filtered_df.empty:
                # 提供更详细的失败原因
                total_df = self.data_processor.merged_df.copy() if self.data_processor.merged_df is not None else pd.DataFrame()
                message = f"未找到匹配数据（用户位次：{user_rank}）。建议：\n"
                
                if total_df.empty:
                    message += "1. 请检查数据文件是否正确上传\n"
                else:
                    valid_ranks = total_df.dropna(subset=['cutoff_rank']) if 'cutoff_rank' in total_df.columns else pd.DataFrame()
                    if not valid_ranks.empty:
                        min_rank = int(valid_ranks['cutoff_rank'].min())
                        max_rank = int(valid_ranks['cutoff_rank'].max())
                        message += f"1. 数据库位次范围：{min_rank}-{max_rank}\n"
                        if user_rank < min_rank:
                            message += "2. 您的位次较高，建议关注顶尖院校\n"
                        elif user_rank > max_rank:
                            message += "2. 您的位次较低，建议关注专科或其他批次\n"
                    
                    message += "3. 尝试取消985/211限制\n4. 考虑扩大地区范围\n5. 2025年数据与2024年可能存在差异"
                
                return {
                    'success': False,
                    'message': message,
                    'data': {'冲': [], '稳': [], '保': []}
                }
            
            # 计算推荐类型、风险等级和差异百分比
            filtered_df['recommendation_type'] = filtered_df['cutoff_rank'].apply(
                lambda x: self.get_recommendation_type(user_rank, x)
            )
            filtered_df['risk_level'] = filtered_df['cutoff_rank'].apply(
                lambda x: self.calculate_risk_level(user_rank, x)
            )
            filtered_df['diff_percentage'] = filtered_df['cutoff_rank'].apply(
                lambda x: self.calculate_diff_percentage(user_rank, x)
            )
            
            # 移除未知类型
            filtered_df = filtered_df[filtered_df['recommendation_type'] != '未知']
            
            # 按类型分组
            result = {'冲': [], '稳': [], '保': []}
            
            for rec_type in ['冲', '稳', '保']:
                type_df = filtered_df[filtered_df['recommendation_type'] == rec_type].copy()
                
                # 排序：冲线按差异百分比升序，稳和保按差异百分比降序
                if rec_type == '冲':
                    type_df = type_df.sort_values('diff_percentage', ascending=True)
                else:
                    type_df = type_df.sort_values('diff_percentage', ascending=False)
                
                # 限制数量
                type_df = type_df.head(limit_per_type)
                
                # 转换为字典列表
                for _, row in type_df.iterrows():
                    result[rec_type].append({
                        'school_name': row.get('school_name', ''),
                        'major_group': row.get('major_group', ''),
                        'major_name': row.get('major_name', ''),
                        'cutoff_score': int(row.get('cutoff_score', 0)) if pd.notna(row.get('cutoff_score')) else 0,
                        'cutoff_rank': int(row.get('cutoff_rank', 0)) if pd.notna(row.get('cutoff_rank')) else 0,
                        'plan_count': int(row.get('plan_count', 0)) if pd.notna(row.get('plan_count')) else 0,
                        'is_985': bool(row.get('is_985', False)),
                        'is_211': bool(row.get('is_211', False)),
                        'risk_level': float(row.get('risk_level', 0)) if pd.notna(row.get('risk_level')) else 0,
                        'diff_percentage': round(row.get('diff_percentage', 0) * 100, 2) if pd.notna(row.get('diff_percentage')) else 0
                    })
            
            # 统计信息
            total_count = sum(len(result[key]) for key in result.keys())
            if total_count == 0:
                return {
                    'success': False,
                    'message': f'数据处理完成但无有效推荐（位次{user_rank}）。建议：1.放宽筛选条件 2.考虑年份差异影响 3.联系招生办获取最新信息',
                    'data': {'冲': [], '稳': [], '保': []}
                }
            
            message = f"找到 {total_count} 个推荐结果（冲:{len(result['冲'])}, 稳:{len(result['稳'])}, 保:{len(result['保'])}）\n⚠️ 注意：基于2024年数据，2025年实际情况可能有差异"
            
            return {
                'success': True,
                'message': message,
                'data': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'推荐生成失败: {str(e)}',
                'data': {'冲': [], '稳': [], '保': []}
            }
    
    def get_user_score_from_rank(self, user_rank):
        """根据位次获取大致分数"""
        try:
            if self.data_processor.score_rank_df is None:
                return None
            
            df = self.data_processor.score_rank_df
            # 查找最接近的位次
            if 'cumulative_count' in df.columns:
                closest_row = df.iloc[(df['cumulative_count'] - user_rank).abs().argsort()[:1]]
            elif 'rank' in df.columns:
                closest_row = df.iloc[(df['rank'] - user_rank).abs().argsort()[:1]]
            else:
                return None
            
            return int(closest_row['total_score'].iloc[0]) if not closest_row.empty else None
        except:
            return None

    def get_recommendation_type_new_gaokao(self, user_rank, cutoff_rank):
        """基于广西2025年新高考政策的推荐类型判断"""
        if pd.isna(cutoff_rank) or pd.isna(user_rank):
            return '未知'

        # 计算位次差异比例 - 针对广西新高考调整策略
        diff_ratio = (cutoff_rank - user_rank) / user_rank

        # 广西新高考40个院校专业组志愿，策略更加精细化
        # 冲线：用户位次比录取位次高10-25%（有一定风险但值得尝试）
        # 稳妥：用户位次在录取位次±10%范围内（录取概率较高）
        # 保底：用户位次比录取位次低10%以上（基本确保录取）

        if diff_ratio <= -0.10:  # 录取位次比用户位次高10%以上 - 冲线
            return '冲'
        elif diff_ratio <= 0.10:  # 录取位次在用户位次±10%范围内 - 稳妥
            return '稳'
        else:  # 录取位次比用户位次低10%以上 - 保底
            return '保'

    def optimize_recommendations_for_guangxi(self, recommendations, user_rank):
        """针对广西新高考的推荐优化"""
        optimized = {'冲': [], '稳': [], '保': []}

        # 广西新高考建议的志愿分配比例
        # 冲线：8-12个（20-30%）
        # 稳妥：20-24个（50-60%）
        # 保底：8-12个（20-30%）

        target_counts = {
            '冲': 10,   # 冲线志愿数量
            '稳': 22,   # 稳妥志愿数量
            '保': 8     # 保底志愿数量
        }

        for rec_type in ['冲', '稳', '保']:
            if rec_type in recommendations:
                # 按照录取概率和院校层次排序
                sorted_recs = sorted(
                    recommendations[rec_type],
                    key=lambda x: (
                        x.get('is_985', False),
                        x.get('is_211', False),
                        -x.get('cutoff_rank', float('inf'))
                    ),
                    reverse=True
                )

                # 取目标数量
                optimized[rec_type] = sorted_recs[:target_counts[rec_type]]

        return optimized

    def add_guangxi_specific_advice(self, recommendations, user_rank, track):
        """添加广西新高考特定建议"""
        advice = []

        # 基于选科组合的建议
        if track == '物理':
            advice.append("💡 物理类考生可选择理工类、医学类、部分经管类专业")
            advice.append("🎯 建议重点关注工程类、计算机类、医学类专业组")
        elif track == '历史':
            advice.append("💡 历史类考生可选择文史类、经管类、法学类专业")
            advice.append("🎯 建议重点关注师范类、经济类、法学类专业组")

        # 基于位次的建议
        if user_rank <= 5000:
            advice.append("🏆 您的位次很优秀，可重点冲击985/211院校")
        elif user_rank <= 20000:
            advice.append("📚 建议重点关注一本院校和优质专业")
        elif user_rank <= 50000:
            advice.append("🎓 建议关注二本优质院校和热门专业")

        # 广西新高考特定提醒
        advice.extend([
            "⚠️ 2025年是广西新高考第二年，参考数据需谨慎",
            "📋 建议填满40个院校专业组志愿，增加录取机会",
            "🔍 务必确认选考科目符合专业组要求",
            "📞 重要志愿建议直接联系高校招生办确认"
        ])

        return advice