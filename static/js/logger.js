/**
 * JavaScript 專業日誌工具 - 簡化版本
 * 提供類似 Python logger 的功能
 */

// 檢查是否已經載入
if (typeof window.ResumeClinicLogger !== 'undefined') {
    console.warn('ResumeClinicLogger 已存在，跳過載入');
} else {
    // 建立命名空間
    window.ResumeClinicLogger = {};
    
    // 簡化的日誌類別
    class SimpleLogger {
        constructor(name = 'App') {
            this.name = name;
        }
        
        info(message, data = null) {
            console.info(`ℹ️ [${this.name}] ${message}`, data || '');
        }
        
        debug(message, data = null) {
            console.debug(`🐛 [${this.name}] ${message}`, data || '');
        }
        
        warn(message, data = null) {
            console.warn(`⚠️ [${this.name}] ${message}`, data || '');
        }
        
        error(message, data = null) {
            console.error(`❌ [${this.name}] ${message}`, data || '');
        }
        
        logUserAction(action, details = {}) {
            this.info('User Action', { action, ...details });
        }
        
        logApiRequest(method, url, status, duration) {
            this.info('API Request', { method, url, status, duration: `${duration}ms` });
        }
        
        logPerformance(operation, duration) {
            this.info('Performance', { operation, duration: `${duration}ms` });
        }
    }
    
    // 簡化的效能監控
    class SimplePerformanceMonitor {
        constructor(logger) {
            this.logger = logger;
            this.timers = new Map();
        }
        
        start(operation) {
            this.timers.set(operation, performance.now());
        }
        
        end(operation) {
            const startTime = this.timers.get(operation);
            if (startTime) {
                const duration = performance.now() - startTime;
                this.logger.logPerformance(operation, Math.round(duration));
                this.timers.delete(operation);
            }
        }
    }
    
    // 建立實例
    const simpleLogger = new SimpleLogger('ResumeClinic');
    const simplePerfMonitor = new SimplePerformanceMonitor(simpleLogger);
    
    // 匯出到命名空間
    window.ResumeClinicLogger.SimpleLogger = SimpleLogger;
    window.ResumeClinicLogger.logger = simpleLogger;
    window.ResumeClinicLogger.SimplePerformanceMonitor = SimplePerformanceMonitor;
    window.ResumeClinicLogger.perfMonitor = simplePerfMonitor;
    
    // 為了向後相容，也匯出到全域
    window.appLogger = simpleLogger;
    window.appPerfMonitor = simplePerfMonitor;
    
    // 全域錯誤處理
    window.addEventListener('error', (event) => {
        simpleLogger.error('Global Error', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
        });
    });
    
    // 未處理的 Promise 拒絕
    window.addEventListener('unhandledrejection', (event) => {
        simpleLogger.error('Unhandled Promise Rejection', {
            reason: event.reason
        });
    });
    
    console.log('✅ ResumeClinicLogger 已載入');
} 