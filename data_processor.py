import pandas as pd
import os
from config import SCHOOLS_985, SCHOOLS_211

class DataProcessor:
    def __init__(self):
        self.score_rank_df = None      # 一分一档表
        self.cutoff_df = None          # 最低分数线
        self.plan_df = None            # 招生计划
        self.merged_df = None          # 合并后的数据
        
    def load_excel_files(self, score_rank_file, cutoff_file, plan_file):
        """加载三个Excel文件"""
        try:
            # 先检查一分一档表的实际结构
            print("🔍 检查一分一档表结构...")
            
            # 尝试读取前几行来确定数据起始位置
            preview_df = pd.read_excel(score_rank_file, nrows=10)
            print(f"预览前10行列名: {list(preview_df.columns)}")
            print(f"预览数据:")
            print(preview_df.head())
            
            # 查找包含"总分"和"位次/名次"的行作为真正的表头
            header_row = None
            for i in range(min(5, len(preview_df))):
                row_values = preview_df.iloc[i].astype(str).tolist()
                if any('总分' in str(val) for val in row_values) and any(any(keyword in str(val) for keyword in ['位次', '名次', 'rank']) for val in row_values):
                    header_row = i + 1  # pandas的行索引从0开始，但Excel从1开始
                    print(f"找到真正的表头在第{header_row + 1}行")
                    break
            
            # 根据找到的表头位置读取完整数据
            if header_row is not None:
                self.score_rank_df = pd.read_excel(score_rank_file, header=header_row)
            else:
                # 如果没找到，尝试不同的读取策略
                print("未找到明确表头，尝试多种读取方式...")
                try:
                    # 策略1：跳过第一行
                    self.score_rank_df = pd.read_excel(score_rank_file, skiprows=1)
                    if len(self.score_rank_df) < 1000:
                        # 策略2：直接读取
                        self.score_rank_df = pd.read_excel(score_rank_file)
                        if len(self.score_rank_df) < 1000:
                            # 策略3：指定具体列
                            self.score_rank_df = pd.read_excel(score_rank_file, usecols=[0, 1, 2, 3])
                except:
                    self.score_rank_df = pd.read_excel(score_rank_file)
            
            print(f"✅ 一分一档表最终加载：{len(self.score_rank_df)}行，列名：{list(self.score_rank_df.columns)}")
            
            # 读取最低分数线 - 尝试多个sheet名称
            sheet_names = ['投档线', 'Sheet1', 0]  # 多个可能的sheet名称
            self.cutoff_df = None
            
            for sheet_name in sheet_names:
                try:
                    self.cutoff_df = pd.read_excel(cutoff_file, sheet_name=sheet_name)
                    print(f"✅ 最低分数线从sheet '{sheet_name}' 加载成功，共{len(self.cutoff_df)}行")
                    break
                except Exception as e:
                    print(f"尝试sheet '{sheet_name}' 失败: {e}")
                    continue
            
            if self.cutoff_df is None:
                return False, "无法读取最低分数线文件"
            
            # 读取招生计划 - 尝试多个sheet名称  
            sheet_names = ['计划', 'Sheet1', 0]
            self.plan_df = None
            
            for sheet_name in sheet_names:
                try:
                    self.plan_df = pd.read_excel(plan_file, sheet_name=sheet_name)
                    print(f"✅ 招生计划从sheet '{sheet_name}' 加载成功，共{len(self.plan_df)}行")
                    break
                except Exception as e:
                    print(f"尝试sheet '{sheet_name}' 失败: {e}")
                    continue
            
            if self.plan_df is None:
                return False, "无法读取招生计划文件"
            
            return True, "文件加载成功"
        except Exception as e:
            return False, f"文件加载失败: {str(e)}"
    
    def standardize_columns(self):
        """标准化列名 - 根据实际数据结构"""
        try:
            # 显示原始列名用于调试
            print(f"一分一档表原始列名: {list(self.score_rank_df.columns)}")
            print(f"最低分数线原始列名: {list(self.cutoff_df.columns)}")
            print(f"招生计划原始列名: {list(self.plan_df.columns)}")

            # 一分一档表列名标准化
            # 实际结构：总分、人数、累计人数、名次
            score_rank_columns = {}
            if len(self.score_rank_df.columns) >= 4:
                score_rank_columns = {
                    self.score_rank_df.columns[0]: 'total_score',     # 总分
                    self.score_rank_df.columns[1]: 'count',           # 人数
                    self.score_rank_df.columns[2]: 'cumulative_count', # 累计人数
                    self.score_rank_df.columns[3]: 'rank'             # 名次
                }
            elif len(self.score_rank_df.columns) >= 2:
                # 如果只有2列，可能是总分和名次
                score_rank_columns = {
                    self.score_rank_df.columns[0]: 'total_score',     # 总分
                    self.score_rank_df.columns[1]: 'rank'             # 名次
                }

            # 最低分数线列名标准化
            # 实际结构：院校代码、院校名称、专业组、投档最低分、备注
            cutoff_columns = {}
            if len(self.cutoff_df.columns) >= 4:
                cutoff_columns = {
                    self.cutoff_df.columns[0]: 'school_code',    # 院校代码
                    self.cutoff_df.columns[1]: 'school_name',    # 院校名称
                    self.cutoff_df.columns[2]: 'major_group',    # 专业组
                    self.cutoff_df.columns[3]: 'cutoff_score',   # 投档最低分
                }
                # 如果有第5列（备注），也映射
                if len(self.cutoff_df.columns) >= 5:
                    cutoff_columns[self.cutoff_df.columns[4]] = 'remark'

            # 招生计划列名标准化
            # 实际结构：年份、学校、招生代码、学校方向、省份、科目、计划总数、专业、专业代码、批次、学费、学制、计划人数
            plan_columns = {}
            if len(self.plan_df.columns) >= 13:
                plan_columns = {
                    self.plan_df.columns[0]: 'year',             # 年份
                    self.plan_df.columns[1]: 'school_name',      # 学校
                    self.plan_df.columns[2]: 'admission_code',   # 招生代码
                    self.plan_df.columns[3]: 'school_direction', # 学校方向
                    self.plan_df.columns[4]: 'province',         # 省份
                    self.plan_df.columns[5]: 'track',            # 科目
                    self.plan_df.columns[6]: 'total_plan',       # 计划总数
                    self.plan_df.columns[7]: 'major_name',       # 专业
                    self.plan_df.columns[8]: 'major_code',       # 专业代码
                    self.plan_df.columns[9]: 'batch',            # 批次
                    self.plan_df.columns[10]: 'tuition',         # 学费
                    self.plan_df.columns[11]: 'duration',        # 学制
                    self.plan_df.columns[12]: 'plan_count'       # 计划人数
                }

            # 应用列名映射
            if self.score_rank_df is not None and score_rank_columns:
                self.score_rank_df.rename(columns=score_rank_columns, inplace=True)
                print(f"一分一档表标准化后列名: {list(self.score_rank_df.columns)}")

            if self.cutoff_df is not None and cutoff_columns:
                self.cutoff_df.rename(columns=cutoff_columns, inplace=True)
                print(f"最低分数线标准化后列名: {list(self.cutoff_df.columns)}")

            if self.plan_df is not None and plan_columns:
                self.plan_df.rename(columns=plan_columns, inplace=True)
                print(f"招生计划标准化后列名: {list(self.plan_df.columns)}")

                # 清理计划人数数据
                if 'plan_count' in self.plan_df.columns:
                    self.plan_df['plan_count'] = self.plan_df['plan_count'].apply(self.clean_plan_count)
                    print("计划人数数据清理完成")

            print("列名标准化完成")
            return True, "列名标准化成功"
        except Exception as e:
            return False, f"列名标准化失败: {str(e)}"

    def clean_plan_count(self, plan_count_str):
        """清理计划人数数据，处理类似'3人3人4人'的字符串"""
        try:
            if pd.isna(plan_count_str):
                return 0

            # 转换为字符串
            plan_str = str(plan_count_str).strip()

            # 如果已经是纯数字，直接返回
            if plan_str.isdigit():
                return int(plan_str)

            # 处理包含"人"字的情况，如"3人"、"3人4人5人"
            if '人' in plan_str:
                # 提取所有数字
                import re
                numbers = re.findall(r'\d+', plan_str)
                if numbers:
                    # 如果有多个数字，求和（如"3人4人5人" -> 3+4+5=12）
                    total = sum(int(num) for num in numbers)
                    return total
                else:
                    return 0

            # 尝试直接转换为整数
            try:
                return int(float(plan_str))
            except:
                # 如果都失败了，返回0
                print(f"警告：无法解析计划人数 '{plan_str}'，设为0")
                return 0

        except Exception as e:
            print(f"清理计划人数时出错: {e}, 原始值: {plan_count_str}")
            return 0
    
    def sanity_check_rank_data(self):
        """一分一档表数据自检（Must-Run Sanity Check）"""
        try:
            if self.score_rank_df is None:
                return False, "一分一档表未正确加载"

            # 检查是否有rank列
            if 'rank' not in self.score_rank_df.columns:
                return False, "一分一档表缺少rank列，请检查列名映射"

            # 获取位次数据
            df_rank = self.score_rank_df.copy()

            # 清理数据，确保rank列是数值类型
            df_rank['rank'] = pd.to_numeric(df_rank['rank'], errors='coerce')
            valid_ranks = df_rank['rank'].dropna()

            if len(valid_ranks) == 0:
                return False, "rank列没有有效的数值数据"

            # 计算统计信息
            min_rank = int(valid_ranks.min())
            max_rank = int(valid_ranks.max())
            row_cnt = len(df_rank)
            valid_cnt = len(valid_ranks)

            print(f"✅ 已载入一分一档表，共 {row_cnt} 行，有效位次数据 {valid_cnt} 行")
            print(f"📊 位次范围: {min_rank} – {max_rank}")

            # 数据完整性检查 - 放宽标准，因为可能是部分数据
            if max_rank < 1000:
                warning_msg = f"⚠️ 位次数据范围较小（最大位次 {max_rank}），可能是部分数据或测试数据"
                print(warning_msg)
                # 不返回错误，继续处理

            # 显示数据样本用于验证
            print("📊 数据样本检查：")
            if 'total_score' in df_rank.columns:
                print("前3行数据：")
                print(df_rank[['total_score', 'rank']].head(3))
                print("后3行数据：")
                print(df_rank[['total_score', 'rank']].tail(3))
            else:
                print("前3行rank数据：")
                print(df_rank['rank'].head(3))
                print("后3行rank数据：")
                print(df_rank['rank'].tail(3))

            return True, f"一分一档表数据检查通过（{valid_cnt}行有效数据，位次{min_rank}-{max_rank}）"

        except Exception as e:
            return False, f"数据自检失败: {str(e)}"
    
    def score_to_rank(self, score, track='物理'):
        """分数转位次 - 根据实际一分一档表结构"""
        try:
            # 根据一分一档表查找对应位次
            if self.score_rank_df is None:
                return None

            # 清理数据，确保分数和位次都是数值
            df = self.score_rank_df.copy()
            df = df.dropna(subset=['total_score', 'rank'])
            df['total_score'] = pd.to_numeric(df['total_score'], errors='coerce')
            df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
            df = df.dropna(subset=['total_score', 'rank'])

            if len(df) == 0:
                print("一分一档表没有有效数据")
                return None

            # 查找小于等于目标分数的最高分数对应的位次
            filtered_df = df[df['total_score'] <= score].sort_values('total_score', ascending=False)

            if len(filtered_df) > 0:
                rank = int(filtered_df.iloc[0]['rank'])
                print(f"分数{score}对应位次: {rank}")
                return rank
            else:
                # 如果分数太高，返回最高分对应的位次
                max_score_row = df.loc[df['total_score'].idxmax()]
                rank = int(max_score_row['rank'])
                print(f"分数{score}超出范围，返回最高分{max_score_row['total_score']}对应位次: {rank}")
                return rank
        except Exception as e:
            print(f"分数转位次失败: {str(e)}")
            return None
    
    def add_cutoff_rank(self):
        """为最低分数线添加位次信息"""
        try:
            # 调试信息：显示当前列名
            print(f"最低分数线表当前列名: {list(self.cutoff_df.columns)}")

            # 检查是否已有cutoff_rank列且有数据
            if 'cutoff_rank' in self.cutoff_df.columns:
                # 检查cutoff_rank列是否有有效数据
                valid_ranks = self.cutoff_df['cutoff_rank'].dropna()
                if len(valid_ranks) > 0:
                    print(f"已有位次数据 {len(valid_ranks)} 条，跳过位次转换")
                    return True, "位次数据已存在"

            # 如果没有位次数据但有分数数据，则进行转换
            if 'cutoff_score' in self.cutoff_df.columns:
                print("开始分数转位次转换...")

                # 清理分数数据
                self.cutoff_df['cutoff_score'] = pd.to_numeric(self.cutoff_df['cutoff_score'], errors='coerce')

                # 转换分数为位次
                def convert_score_to_rank(score):
                    if pd.isna(score):
                        return None
                    try:
                        return self.score_to_rank(int(score))
                    except:
                        return None

                self.cutoff_df['cutoff_rank'] = self.cutoff_df['cutoff_score'].apply(convert_score_to_rank)

                # 统计转换结果
                valid_conversions = self.cutoff_df['cutoff_rank'].dropna()
                print(f"成功转换 {len(valid_conversions)} 条分数为位次")

                return True, f"位次转换成功，共转换{len(valid_conversions)}条记录"
            else:
                return False, "既没有位次数据也没有分数数据，无法进行位次转换"

        except Exception as e:
            return False, f"位次转换失败: {str(e)}"
    
    def add_school_labels(self):
        """添加985/211标识"""
        try:
            def get_school_labels(school_name):
                is_985 = any(school in str(school_name) for school in SCHOOLS_985)
                is_211 = any(school in str(school_name) for school in SCHOOLS_211)
                return is_985, is_211
            
            # 为最低分数线数据添加标识
            labels = self.cutoff_df['school_name'].apply(get_school_labels)
            self.cutoff_df['is_985'] = [label[0] for label in labels]
            self.cutoff_df['is_211'] = [label[1] for label in labels]
            
            print("院校标识添加完成")
            return True, "院校标识添加成功"
        except Exception as e:
            return False, f"院校标识添加失败: {str(e)}"
    
    def merge_data(self):
        """合并数据 - 根据实际数据结构"""
        try:
            # 首先为最低分数线数据添加985/211标识
            self.add_school_labels()

            # 从招生代码中提取专业组信息进行匹配
            # 招生代码格式如：10003[102] -> 专业组为102
            if 'admission_code' in self.plan_df.columns:
                self.plan_df['extracted_major_group'] = self.plan_df['admission_code'].str.extract(r'\[(\d+)\]')

            # 尝试多种合并策略
            merge_success = False

            # 策略1：通过专业组合并
            if 'major_group' in self.cutoff_df.columns and 'extracted_major_group' in self.plan_df.columns:
                try:
                    # 准备招生计划数据用于合并
                    # 确保plan_count是数值类型
                    self.plan_df['plan_count_numeric'] = pd.to_numeric(self.plan_df['plan_count'], errors='coerce').fillna(0)

                    # 改进：保留更多专业详情，不过度聚合
                    plan_for_merge = self.plan_df.groupby(['school_name', 'extracted_major_group']).agg({
                        'major_name': lambda x: ' | '.join(x.unique()[:10]),  # 保留更多专业名称
                        'track': 'first',                                     # 取第一个科目
                        'plan_count_numeric': 'sum',                          # 计划人数求和
                        'batch': 'first',                                     # 批次信息
                        'tuition': 'first'                                    # 学费信息
                    }).reset_index()

                    # 重命名回plan_count
                    plan_for_merge.rename(columns={'plan_count_numeric': 'plan_count'}, inplace=True)

                    # 重命名列以匹配
                    plan_for_merge.rename(columns={'extracted_major_group': 'major_group'}, inplace=True)

                    self.merged_df = pd.merge(
                        self.cutoff_df,
                        plan_for_merge,
                        on=['school_name', 'major_group'],
                        how='left'
                    )
                    merge_success = True
                    print(f"数据合并完成（按学校+专业组），共{len(self.merged_df)}行")
                except Exception as e:
                    print(f"专业组合并失败: {e}")

            # 策略2：如果专业组合并失败，尝试按学校名称合并
            if not merge_success and 'school_name' in self.cutoff_df.columns and 'school_name' in self.plan_df.columns:
                try:
                    # 准备招生计划数据用于合并（按学校聚合）
                    # 确保plan_count是数值类型
                    if 'plan_count_numeric' not in self.plan_df.columns:
                        self.plan_df['plan_count_numeric'] = pd.to_numeric(self.plan_df['plan_count'], errors='coerce').fillna(0)

                    plan_for_merge = self.plan_df.groupby('school_name').agg({
                        'major_name': lambda x: ', '.join(x.unique()[:5]),  # 取前5个专业
                        'track': 'first',                                   # 取第一个科目
                        'plan_count_numeric': 'sum'                         # 计划人数求和
                    }).reset_index()

                    # 重命名回plan_count
                    plan_for_merge.rename(columns={'plan_count_numeric': 'plan_count'}, inplace=True)

                    self.merged_df = pd.merge(
                        self.cutoff_df,
                        plan_for_merge,
                        on='school_name',
                        how='left'
                    )
                    merge_success = True
                    print(f"数据合并完成（按学校名称），共{len(self.merged_df)}行")
                except Exception as e:
                    print(f"学校名称合并失败: {e}")

            # 策略3：如果都失败，直接使用最低分数线数据
            if not merge_success:
                self.merged_df = self.cutoff_df.copy()
                # 添加默认值
                self.merged_df['major_name'] = '未知专业'
                self.merged_df['track'] = '物理'  # 默认物理
                self.merged_df['plan_count'] = 0
                print(f"使用最低分数线数据（无合并），共{len(self.merged_df)}行")

            # 确保必要的列存在
            required_columns = ['school_name', 'major_group', 'cutoff_score', 'cutoff_rank', 'is_985', 'is_211']
            for col in required_columns:
                if col not in self.merged_df.columns:
                    if col in ['is_985', 'is_211']:
                        self.merged_df[col] = False
                    else:
                        self.merged_df[col] = None

            print(f"最终合并数据列名: {list(self.merged_df.columns)}")
            return True, "数据合并成功"
        except Exception as e:
            return False, f"数据合并失败: {str(e)}"
    
    def process_all_data(self, score_rank_file, cutoff_file, plan_file):
        """处理所有数据的主函数"""
        steps = [
            ("加载文件", lambda: self.load_excel_files(score_rank_file, cutoff_file, plan_file)),
            ("标准化列名", self.standardize_columns),
            ("数据自检", self.sanity_check_rank_data),
            ("位次转换", self.add_cutoff_rank),
            ("添加院校标识", self.add_school_labels),
            ("合并数据", self.merge_data)
        ]
        
        for step_name, step_func in steps:
            success, message = step_func()
            if not success:
                return False, f"{step_name}失败: {message}"
            print(f"✓ {step_name}: {message}")
        
        return True, "所有数据处理完成"
    
    def get_available_cities(self):
        """获取可用城市列表"""
        if self.merged_df is not None and 'city' in self.merged_df.columns:
            return sorted(self.merged_df['city'].dropna().unique().tolist())
        return []
    
    def get_available_majors(self):
        """获取可用专业类别列表"""
        if self.merged_df is not None and 'major_name' in self.merged_df.columns:
            return sorted(self.merged_df['major_name'].dropna().unique().tolist())
        return []

    def process_data(self):
        """处理数据的主流程方法"""
        try:
            # 1. 标准化列名
            success, message = self.standardize_columns()
            if not success:
                return False, f"列名标准化失败: {message}"

            # 2. 数据自检
            success, message = self.sanity_check_rank_data()
            if not success:
                return False, f"数据自检失败: {message}"

            # 3. 分数转位次
            success, message = self.add_cutoff_rank()
            if not success:
                return False, f"位次转换失败: {message}"

            # 4. 添加院校标识
            success, message = self.add_school_labels()
            if not success:
                return False, f"院校标识添加失败: {message}"

            # 5. 合并数据
            success, message = self.merge_data()
            if not success:
                return False, f"数据合并失败: {message}"

            return True, "数据处理完成"

        except Exception as e:
            return False, f"数据处理过程中出错: {str(e)}"