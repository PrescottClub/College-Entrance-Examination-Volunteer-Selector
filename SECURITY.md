# 安全配置说明

## 环境变量配置

为了保护API密钥等敏感信息，本项目使用环境变量进行配置。

### 设置步骤

1. **复制配置模板**
   ```bash
   copy env.example .env
   ```

2. **编辑 `.env` 文件**
   在 `.env` 文件中填写您的真实API密钥：
   ```
   DEEPSEEK_API_KEY=your_actual_api_key_here
   DEEPSEEK_BASE_URL=https://api.deepseek.com
   DEEPSEEK_MODEL=deepseek-chat
   ```

3. **重要提醒**
   - `.env` 文件已被添加到 `.gitignore` 中，不会被提交到版本控制
   - 请勿在任何代码文件中硬编码API密钥
   - 请勿将 `.env` 文件分享给他人

### API密钥获取

请访问 [DeepSeek API](https://api.deepseek.com) 获取您的API密钥。

### 安全最佳实践

- 定期更换API密钥
- 使用具有最小权限的API密钥
- 监控API使用情况
- 不要在公共代码仓库中暴露敏感信息 