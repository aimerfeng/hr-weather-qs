/**
 * 智能助手 - 前端逻辑
 * 
 * Requirements: 6.4, 6.5, 6.6, 7.4, 7.8, 7.9, 7.10, 8.1, 8.3, 8.6
 */

// ========== 配置管理 ==========
class ConfigManager {
    constructor() {
        this.storageKey = 'ai_assistant_config';
        this.defaultConfig = {
            provider: 'openai',
            baseUrl: 'https://api.openai.com/v1',
            apiKey: '',
            model: 'gpt-3.5-turbo'
        };
        this.presets = {
            openai: {
                baseUrl: 'https://api.openai.com/v1',
                models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini']
            },
            deepseek: {
                baseUrl: 'https://api.deepseek.com/v1',
                models: ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner']
            },
            qwen: {
                baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                models: ['qwen-turbo', 'qwen-plus', 'qwen-max', 'qwen-long']
            }
        };
    }

    /**
     * 加载配置
     * Requirements 8.6: 本地持久化配置
     */
    loadConfig() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (saved) {
                return { ...this.defaultConfig, ...JSON.parse(saved) };
            }
        } catch (e) {
            console.error('加载配置失败:', e);
        }
        return { ...this.defaultConfig };
    }

    /**
     * 保存配置
     * Requirements 8.6: 本地持久化配置
     */
    saveConfig(config) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(config));
            return true;
        } catch (e) {
            console.error('保存配置失败:', e);
            return false;
        }
    }

    /**
     * 获取预设配置
     */
    getPreset(provider) {
        return this.presets[provider] || null;
    }

    /**
     * 获取掩码后的 API Key
     * Requirements 8.3: API Key 掩码显示
     */
    getMaskedApiKey(apiKey) {
        if (!apiKey || apiKey.length <= 8) {
            return '*'.repeat(apiKey?.length || 0);
        }
        return `${apiKey.slice(0, 4)}****${apiKey.slice(-4)}`;
    }
}

// ========== 聊天管理 ==========
class ChatManager {
    constructor(configManager) {
        this.configManager = configManager;
        this.conversationHistory = [];
        this.careerState = null;
        this.currentEventSource = null;
        this.isProcessing = false;
    }

    /**
     * 发送消息
     * Requirements 6.4: SSE 连接和消息处理
     */
    async sendMessage(message, onChunk, onComplete, onError) {
        if (this.isProcessing) {
            onError('正在处理上一条消息，请稍候...');
            return;
        }

        this.isProcessing = true;
        const config = this.configManager.loadConfig();

        if (!config.apiKey) {
            onError('请先配置 API Key');
            this.isProcessing = false;
            return;
        }

        // 添加用户消息到历史
        this.conversationHistory.push({
            role: 'user',
            content: message
        });

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    api_key: config.apiKey,
                    base_url: config.baseUrl,
                    model: config.model,
                    provider: config.provider,
                    conversation_history: this.conversationHistory.slice(-10),
                    career_state: this.careerState
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // 处理 SSE 流
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let assistantMessage = '';

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        
                        if (data === '[DONE]') {
                            continue;
                        }

                        try {
                            const message = JSON.parse(data);
                            
                            if (message.type === 'content') {
                                assistantMessage += message.content;
                                onChunk(message.content);
                            } else if (message.type === 'weather') {
                                onChunk(message, 'weather');
                            } else if (message.type === 'career_progress') {
                                this.careerState = {
                                    current_stage: message.stage_index || 0,
                                    progress: message.progress
                                };
                                onChunk(message, 'career_progress');
                            } else if (message.type === 'error') {
                                onError(message.content);
                            } else if (message.type === 'done') {
                                // 完成
                            }
                        } catch (e) {
                            console.error('解析 SSE 消息失败:', e, data);
                        }
                    }
                }
            }

            // 添加助手消息到历史
            if (assistantMessage) {
                this.conversationHistory.push({
                    role: 'assistant',
                    content: assistantMessage
                });
            }

            onComplete();

        } catch (error) {
            console.error('发送消息失败:', error);
            onError(error.message || '发送消息失败');
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * 清空对话历史
     */
    clearHistory() {
        this.conversationHistory = [];
        this.careerState = null;
    }
}

// ========== UI 管理 ==========
class UIManager {
    constructor() {
        this.elements = {
            chatMessages: document.getElementById('chatMessages'),
            chatInput: document.getElementById('chatInput'),
            sendButton: document.getElementById('sendButton'),
            settingsButton: document.getElementById('settingsButton'),
            settingsModal: document.getElementById('settingsModal'),
            closeModal: document.getElementById('closeModal'),
            settingsForm: document.getElementById('settingsForm'),
            testButton: document.getElementById('testButton'),
            testResult: document.getElementById('testResult'),
            statusIndicator: document.getElementById('statusIndicator'),
            weatherTimeline: document.getElementById('weatherTimeline'),
            timelineContent: document.getElementById('timelineContent'),
            historyList: document.getElementById('historyList'),
            provider: document.getElementById('provider'),
            baseUrl: document.getElementById('baseUrl'),
            apiKey: document.getElementById('apiKey'),
            model: document.getElementById('model')
        };

        this.currentAssistantMessage = null;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // 发送按钮
        this.elements.sendButton.addEventListener('click', () => this.handleSend());

        // 输入框回车发送
        this.elements.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });

        // 输入框自动调整高度
        this.elements.chatInput.addEventListener('input', () => {
            this.elements.chatInput.style.height = 'auto';
            this.elements.chatInput.style.height = this.elements.chatInput.scrollHeight + 'px';
        });

        // 设置按钮
        this.elements.settingsButton.addEventListener('click', () => this.openSettings());

        // 关闭模态框
        this.elements.closeModal.addEventListener('click', () => this.closeSettings());
        this.elements.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.elements.settingsModal) {
                this.closeSettings();
            }
        });

        // 提供商切换
        this.elements.provider.addEventListener('change', () => this.handleProviderChange());

        // 测试连接
        this.elements.testButton.addEventListener('click', () => this.testConnection());

        // 保存设置
        this.elements.settingsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSettings();
        });
    }

    handleSend() {
        const message = this.elements.chatInput.value.trim();
        if (!message || app.chatManager.isProcessing) return;

        // 添加用户消息到界面
        this.addUserMessage(message);

        // 清空输入框
        this.elements.chatInput.value = '';
        this.elements.chatInput.style.height = 'auto';

        // 禁用输入
        this.setInputEnabled(false);
        this.setStatus('thinking', '思考中...');

        // 创建助手消息容器
        this.currentAssistantMessage = this.createAssistantMessage();

        // 发送消息
        app.chatManager.sendMessage(
            message,
            (chunk, type) => this.handleChunk(chunk, type),
            () => this.handleComplete(),
            (error) => this.handleError(error)
        );
    }

    handleChunk(chunk, type) {
        if (type === 'weather') {
            // 处理天气数据
            this.displayWeatherData(chunk);
        } else if (type === 'career_progress') {
            // 处理职业规划进度
            this.updateCareerProgress(chunk);
        } else {
            // 处理文本内容
            if (this.currentAssistantMessage) {
                const textElement = this.currentAssistantMessage.querySelector('.message-text');
                textElement.textContent += chunk;
                this.scrollToBottom();
            }
        }
    }

    handleComplete() {
        this.setInputEnabled(true);
        this.setStatus('ready', '就绪');
        this.currentAssistantMessage = null;
        this.elements.chatInput.focus();
        
        // 刷新天气历史
        this.loadWeatherHistory();
    }

    handleError(error) {
        this.setInputEnabled(true);
        this.setStatus('error', '错误');
        
        if (this.currentAssistantMessage) {
            const textElement = this.currentAssistantMessage.querySelector('.message-text');
            textElement.innerHTML = `<p style="color: var(--error);">❌ ${error}</p>`;
        } else {
            this.addAssistantMessage(`❌ ${error}`);
        }
        
        this.currentAssistantMessage = null;
    }

    addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">👤</div>
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(text)}</div>
                <div class="message-time">${this.formatTime(new Date())}</div>
            </div>
        `;
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    createAssistantMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">🌟</div>
            <div class="message-content">
                <div class="message-text"></div>
                <div class="message-time">${this.formatTime(new Date())}</div>
            </div>
        `;
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        return messageDiv;
    }

    addAssistantMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">🌟</div>
            <div class="message-content">
                <div class="message-text">${text}</div>
                <div class="message-time">${this.formatTime(new Date())}</div>
            </div>
        `;
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    displayWeatherData(data) {
        const { weather, forecast } = data;
        
        // 更新天气时间表
        const weatherCard = `
            <div class="weather-card">
                <div class="weather-header">
                    <div class="weather-city">${weather.city}</div>
                    <div class="weather-temp">${weather.temperature}°C</div>
                </div>
                <div class="weather-condition">${weather.condition}</div>
                <div class="weather-details">
                    <div>💧 湿度: ${weather.humidity}%</div>
                    <div>💨 风速: ${weather.wind_speed} km/h</div>
                    <div>🌡️ 体感: ${weather.feels_like}°C</div>
                </div>
                ${forecast && forecast.length > 0 ? `
                    <div class="forecast-list">
                        ${forecast.map(day => `
                            <div class="forecast-item">
                                <span class="forecast-day">${day.day_of_week}</span>
                                <span class="forecast-temp">${day.temp_min}~${day.temp_max}°C</span>
                                <span class="forecast-condition">${day.condition}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        this.elements.timelineContent.innerHTML = weatherCard;
    }

    async loadWeatherHistory() {
        try {
            const response = await fetch('/api/history');
            const result = await response.json();
            
            if (result.success && result.data && result.data.length > 0) {
                const historyHTML = result.data.map(entry => `
                    <div class="history-item ${entry.city === result.most_frequent_city ? 'frequent' : ''}" 
                         onclick="app.ui.handleHistoryClick('${entry.city}')">
                        <div class="history-city">${entry.city}</div>
                        <div class="history-weather">
                            ${entry.last_weather.temperature}°C, ${entry.last_weather.condition}
                        </div>
                        <div class="history-time">
                            ${this.formatTime(new Date(entry.last_query_time))} · 查询${entry.query_count}次
                        </div>
                    </div>
                `).join('');
                
                this.elements.historyList.innerHTML = historyHTML;
            } else {
                this.elements.historyList.innerHTML = '<p class="empty-state">暂无历史记录</p>';
            }
        } catch (error) {
            console.error('加载历史记录失败:', error);
        }
    }

    handleHistoryClick(city) {
        this.elements.chatInput.value = `${city}天气`;
        this.elements.chatInput.focus();
    }

    updateCareerProgress(data) {
        // 可以在这里添加进度条显示
        console.log('职业规划进度:', data.progress);
    }

    setInputEnabled(enabled) {
        this.elements.chatInput.disabled = !enabled;
        this.elements.sendButton.disabled = !enabled;
    }

    setStatus(status, text) {
        const dot = this.elements.statusIndicator.querySelector('.status-dot');
        const statusText = this.elements.statusIndicator.querySelector('.status-text');
        
        dot.className = 'status-dot';
        if (status === 'thinking' || status === 'connecting') {
            dot.classList.add('connecting');
        } else if (status === 'error') {
            dot.classList.add('error');
        }
        
        statusText.textContent = text;
    }

    openSettings() {
        const config = app.configManager.loadConfig();
        
        this.elements.provider.value = config.provider;
        this.elements.baseUrl.value = config.baseUrl;
        this.elements.apiKey.value = config.apiKey;
        this.elements.model.value = config.model;
        
        this.handleProviderChange();
        this.elements.settingsModal.classList.add('active');
    }

    closeSettings() {
        this.elements.settingsModal.classList.remove('active');
        this.elements.testResult.style.display = 'none';
    }

    handleProviderChange() {
        const provider = this.elements.provider.value;
        const preset = app.configManager.getPreset(provider);
        
        if (preset) {
            this.elements.baseUrl.value = preset.baseUrl;
            
            // 更新模型选项
            const modelSelect = this.elements.model;
            modelSelect.innerHTML = preset.models.map(model => 
                `<option value="${model}">${model}</option>`
            ).join('');
        }
    }

    async testConnection() {
        const config = {
            provider: this.elements.provider.value,
            baseUrl: this.elements.baseUrl.value,
            apiKey: this.elements.apiKey.value,
            model: this.elements.model.value
        };

        if (!config.apiKey) {
            this.showTestResult('请输入 API Key', false);
            return;
        }

        this.elements.testButton.disabled = true;
        this.elements.testButton.textContent = '测试中...';
        this.elements.testResult.style.display = 'none';

        try {
            const response = await fetch('/api/config/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    api_key: config.apiKey,
                    base_url: config.baseUrl,
                    model: config.model,
                    provider: config.provider
                })
            });

            const result = await response.json();

            if (result.success && result.is_valid) {
                this.showTestResult(result.message || '连接测试成功！', true);
            } else {
                this.showTestResult(result.error_message || '连接测试失败', false);
            }
        } catch (error) {
            this.showTestResult(`测试失败: ${error.message}`, false);
        } finally {
            this.elements.testButton.disabled = false;
            this.elements.testButton.textContent = '测试连接';
        }
    }

    showTestResult(message, success) {
        this.elements.testResult.textContent = message;
        this.elements.testResult.className = `test-result ${success ? 'success' : 'error'}`;
        this.elements.testResult.style.display = 'block';
    }

    saveSettings() {
        const config = {
            provider: this.elements.provider.value,
            baseUrl: this.elements.baseUrl.value,
            apiKey: this.elements.apiKey.value,
            model: this.elements.model.value
        };

        if (!config.apiKey) {
            this.showTestResult('请输入 API Key', false);
            return;
        }

        if (app.configManager.saveConfig(config)) {
            this.showTestResult('设置已保存！', true);
            setTimeout(() => {
                this.closeSettings();
            }, 1500);
        } else {
            this.showTestResult('保存失败', false);
        }
    }

    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTime(date) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
}

// ========== 应用主类 ==========
class App {
    constructor() {
        this.configManager = new ConfigManager();
        this.chatManager = new ChatManager(this.configManager);
        this.ui = new UIManager();
    }

    async init() {
        // 检查配置
        const config = this.configManager.loadConfig();
        if (!config.apiKey) {
            this.ui.openSettings();
        }

        // 加载天气历史
        await this.ui.loadWeatherHistory();

        // 设置焦点
        this.ui.elements.chatInput.focus();
    }
}

// ========== 初始化应用 ==========
const app = new App();

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => app.init());
} else {
    app.init();
}
