/**
 * JavaScript 專業日誌工具 - 優化版本
 * 提供環境變數控制的日誌功能，支援開發和生產環境
 */

// 環境檢測和日誌配置
const LOG_CONFIG = {
    // 環境檢測：支援多種環境變數檢測方式
    isDevelopment: () => {
        // 檢測多種環境變數
        if (typeof process !== 'undefined' && process.env && process.env.NODE_ENV) {
            return process.env.NODE_ENV === 'development';
        }
        // 檢測 URL 參數
        if (typeof window !== 'undefined' && window.location) {
            return window.location.search.includes('debug=true') || 
                   window.location.hostname === 'localhost' ||
                   window.location.hostname === '127.0.0.1';
        }
        // 檢測全域變數
        if (typeof window !== 'undefined' && window.DEBUG_MODE) {
            return window.DEBUG_MODE === true;
        }
        // 預設為生產環境
        return false;
    },
    
    // 日誌級別配置
    levels: {
        ERROR: 0,
        WARN: 1,
        INFO: 2,
        DEBUG: 3
    },
    
    // 當前日誌級別
    currentLevel: () => {
        if (LOG_CONFIG.isDevelopment()) {
            return LOG_CONFIG.levels.DEBUG;
        }
        return LOG_CONFIG.levels.ERROR; // 生產環境只記錄錯誤
    },
    
    // 日誌格式配置
    format: {
        timestamp: () => new Date().toISOString(),
        prefix: (level, name) => {
            const icons = {
                [LOG_CONFIG.levels.ERROR]: '❌',
                [LOG_CONFIG.levels.WARN]: '⚠️',
                [LOG_CONFIG.levels.INFO]: 'ℹ️',
                [LOG_CONFIG.levels.DEBUG]: '🐛'
            };
            return `${icons[level] || '📝'} [${name}]`;
        }
    }
};

// 檢查是否已經載入
if (typeof window.ResumeClinicLogger !== 'undefined') {
    console.warn('ResumeClinicLogger 已存在，跳過載入');
} else {
    // 建立命名空間
    window.ResumeClinicLogger = {};
    
    // 優化的日誌類別
    class OptimizedLogger {
        constructor(name = 'App') {
            this.name = name;
            this._logBuffer = []; // 日誌緩衝區
            this._maxBufferSize = 100; // 最大緩衝區大小
        }
        
        // 核心日誌方法
        _log(level, message, data = null) {
            const currentLevel = LOG_CONFIG.currentLevel();
            
            // 檢查日誌級別
            if (level > currentLevel) {
                return;
            }
            
            const timestamp = LOG_CONFIG.format.timestamp();
            const prefix = LOG_CONFIG.format.prefix(level, this.name);
            const logEntry = {
                timestamp,
                level,
                message,
                data,
                prefix
            };
            
            // 添加到緩衝區
            this._addToBuffer(logEntry);
            
            // 輸出到控制台
            this._outputToConsole(logEntry);
        }
        
        // 添加到緩衝區
        _addToBuffer(logEntry) {
            this._logBuffer.push(logEntry);
            
            // 限制緩衝區大小
            if (this._logBuffer.length > this._maxBufferSize) {
                this._logBuffer.shift();
            }
        }
        
        // 輸出到控制台
        _outputToConsole(logEntry) {
            const { prefix, message, data } = logEntry;
            
            switch (logEntry.level) {
                case LOG_CONFIG.levels.ERROR:
                    console.error(`${prefix} ${message}`, data || '');
                    break;
                case LOG_CONFIG.levels.WARN:
                    console.warn(`${prefix} ${message}`, data || '');
                    break;
                case LOG_CONFIG.levels.INFO:
                    console.info(`${prefix} ${message}`, data || '');
                    break;
                case LOG_CONFIG.levels.DEBUG:
                    console.debug(`${prefix} ${message}`, data || '');
                    break;
            }
        }
        
        // 公開的日誌方法
        error(message, data = null) {
            this._log(LOG_CONFIG.levels.ERROR, message, data);
        }
        
        warn(message, data = null) {
            this._log(LOG_CONFIG.levels.WARN, message, data);
        }
        
        info(message, data = null) {
            this._log(LOG_CONFIG.levels.INFO, message, data);
        }
        
        debug(message, data = null) {
            this._log(LOG_CONFIG.levels.DEBUG, message, data);
        }
        
        // 向後相容的方法
        log(message, data = null) {
            this.info(message, data);
        }
        
        // 特殊用途的日誌方法
        logUserAction(action, details = {}) {
            this.info('User Action', { action, ...details });
        }
        
        logApiRequest(method, url, status, duration) {
            this.info('API Request', { method, url, status, duration: `${duration}ms` });
        }
        
        logPerformance(operation, duration) {
            this.info('Performance', { operation, duration: `${duration}ms` });
        }
        
        // 獲取日誌緩衝區
        getLogBuffer() {
            return [...this._logBuffer];
        }
        
        // 清空日誌緩衝區
        clearLogBuffer() {
            this._logBuffer = [];
        }
        
        // 匯出日誌
        exportLogs() {
            return {
                timestamp: new Date().toISOString(),
                logs: this.getLogBuffer(),
                config: {
                    isDevelopment: LOG_CONFIG.isDevelopment(),
                    currentLevel: LOG_CONFIG.currentLevel()
                }
            };
        }
    }
    
    // 優化的效能監控
    class OptimizedPerformanceMonitor {
        constructor(logger) {
            this.logger = logger;
            this.timers = new Map();
            this.metrics = new Map(); // 效能指標收集
        }
        
        start(operation) {
            this.timers.set(operation, performance.now());
        }
        
        end(operation) {
            const startTime = this.timers.get(operation);
            if (startTime) {
                const duration = performance.now() - startTime;
                const roundedDuration = Math.round(duration);
                
                // 記錄效能日誌
                this.logger.logPerformance(operation, roundedDuration);
                
                // 收集效能指標
                this._collectMetrics(operation, roundedDuration);
                
                this.timers.delete(operation);
                return roundedDuration;
            }
            return 0;
        }
        
        // 收集效能指標
        _collectMetrics(operation, duration) {
            if (!this.metrics.has(operation)) {
                this.metrics.set(operation, {
                    count: 0,
                    totalTime: 0,
                    minTime: Infinity,
                    maxTime: 0,
                    avgTime: 0
                });
            }
            
            const metric = this.metrics.get(operation);
            metric.count++;
            metric.totalTime += duration;
            metric.minTime = Math.min(metric.minTime, duration);
            metric.maxTime = Math.max(metric.maxTime, duration);
            metric.avgTime = Math.round(metric.totalTime / metric.count);
        }
        
        // 獲取效能指標
        getMetrics(operation = null) {
            if (operation) {
                return this.metrics.get(operation) || null;
            }
            return Object.fromEntries(this.metrics);
        }
        
        // 清空效能指標
        clearMetrics() {
            this.metrics.clear();
        }
        
        // 匯出效能報告
        exportReport() {
            return {
                timestamp: new Date().toISOString(),
                metrics: this.getMetrics(),
                summary: this._generateSummary()
            };
        }
        
        // 生成效能摘要
        _generateSummary() {
            const allMetrics = Array.from(this.metrics.values());
            if (allMetrics.length === 0) return null;
            
            const totalOperations = allMetrics.reduce((sum, m) => sum + m.count, 0);
            const totalTime = allMetrics.reduce((sum, m) => sum + m.totalTime, 0);
            const avgTime = totalOperations > 0 ? Math.round(totalTime / totalOperations) : 0;
            
            return {
                totalOperations,
                totalTime,
                avgTime,
                slowestOperation: this._findSlowestOperation(),
                fastestOperation: this._findFastestOperation()
            };
        }
        
        _findSlowestOperation() {
            let slowest = null;
            let maxAvg = 0;
            
            for (const [operation, metric] of this.metrics) {
                if (metric.avgTime > maxAvg) {
                    maxAvg = metric.avgTime;
                    slowest = operation;
                }
            }
            
            return slowest ? { operation: slowest, avgTime: maxAvg } : null;
        }
        
        _findFastestOperation() {
            let fastest = null;
            let minAvg = Infinity;
            
            for (const [operation, metric] of this.metrics) {
                if (metric.avgTime < minAvg) {
                    minAvg = metric.avgTime;
                    fastest = operation;
                }
            }
            
            return fastest ? { operation: fastest, avgTime: minAvg } : null;
        }
    }
    
    // 建立實例
    const optimizedLogger = new OptimizedLogger('ResumeClinic');
    const optimizedPerfMonitor = new OptimizedPerformanceMonitor(optimizedLogger);
    
    // 匯出到命名空間
    window.ResumeClinicLogger.OptimizedLogger = OptimizedLogger;
    window.ResumeClinicLogger.logger = optimizedLogger;
    window.ResumeClinicLogger.OptimizedPerformanceMonitor = OptimizedPerformanceMonitor;
    window.ResumeClinicLogger.perfMonitor = optimizedPerfMonitor;
    
    // 為了向後相容，也匯出到全域
    window.appLogger = optimizedLogger;
    window.appPerfMonitor = optimizedPerfMonitor;
    
    // 全域錯誤處理
    window.addEventListener('error', (event) => {
        optimizedLogger.error('Global Error', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            stack: event.error?.stack
        });
    });
    
    // 未處理的 Promise 拒絕
    window.addEventListener('unhandledrejection', (event) => {
        optimizedLogger.error('Unhandled Promise Rejection', {
            reason: event.reason,
            stack: event.reason?.stack
        });
    });
    
    // 頁面載入完成日誌
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            optimizedLogger.info('DOM Content Loaded');
        });
    } else {
        optimizedLogger.info('DOM Already Loaded');
    }
    
    // 頁面卸載日誌
    window.addEventListener('beforeunload', () => {
        optimizedLogger.info('Page Unloading', {
            logsCount: optimizedLogger.getLogBuffer().length,
            performanceReport: optimizedPerfMonitor.exportReport()
        });
    });
    
    // 只在開發環境顯示載入訊息
    if (LOG_CONFIG.isDevelopment()) {
        console.log('✅ ResumeClinicLogger 已載入 (開發模式)');
    }
} 