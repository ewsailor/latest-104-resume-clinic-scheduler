// =================================================================
const CONFIG = {
  // 全域實例
  INSTANCES: {
    GIVER_MODAL: null
  },
  
  // API 配置
  API: {
    BASE_URL: 'https://gist.githubusercontent.com/ewsailor/ddb890d50f572c10842c3f731a6eeb06/raw/bd8ffb58a836cd7f0ecea4f4b52c1bc1bbc7fd00/gistfile1.txt',
    POSTER_URL: 'https://randomuser.me/api/portraits/',
    TIMEOUT: 10000,
    RETRY_DELAY: 1000,
    MAX_RETRIES: 3
  },
  
  // 分頁配置：每頁顯示 12 筆資料
  PAGINATION: {
    GIVERS_PER_PAGE: 12,
    MAX_PAGES_DISPLAY: 10
  },
  
  // UI 配置
  UI: {
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 250,
    THROTTLE_LIMIT: 100,
    LOADING_TIMEOUT: 5000,
    ERROR_DISPLAY_TIME: 5000
  },
  
  // 聊天配置
  CHAT: {
    MAX_MESSAGE_LENGTH: 2000,
    TYPING_INDICATOR_DELAY: 1000,
    MESSAGE_DISPLAY_TIME: 3000,
    AUTO_SCROLL_DELAY: 100
  },
  
  // 快取配置
  CACHE: {
    EXPIRY_TIME: 5 * 60 * 1000, // 5分鐘
    MAX_SIZE: 100,
    CLEANUP_INTERVAL: 10 * 60 * 1000 // 10分鐘
  },
  
  // DOM 選擇器配置
  SELECTORS: {
    GIVER_PANEL: '#giver-panel',
    PAGINATOR: '#paginator',
    CHAT_INPUT: '#chat-input-message',
    CHAT_SEND_BTN: '#chat-send-btn',
    CHAT_MESSAGES: '#chat-messages',
    GIVER_MODAL: '#giver-modal',
    CONFIRM_MODAL: '#confirm-modal',
    CHAT_MODAL_LABEL: '#chatModalLabel'
  },
  
  // CSS 類別配置
  CLASSES: {
    GIVER_CARD: 'giverCard',
    GIVER_CARD_WRAPPER: 'mb-4',
    GIVER_CARD_POINTER: 'giverCard__pointer',
    GIVER_CARD_AVATAR: 'giverCard__avatar',
    GIVER_CARD_AVATAR_CONTAINER: 'giverCard__avatar-container',
    GIVER_CARD_AVATAR_IMG: 'giverCard__avatar-img',
    GIVER_CARD_USER_INFO: 'giverCard__user-info',
    GIVER_CARD_NAME: 'giverCard__name',
    GIVER_CARD_ICON_GRAY: 'giverCard__icon-gray',
    GIVER_CARD_TITLE: 'giverCard__title',
    GIVER_CARD_COMPANY: 'giverCard__company',
    GIVER_CARD_COUNT: 'giverCard__count',
    GIVER_CARD_COUNT_ITEM: 'giverCard__count-item',
    GIVER_CARD_COUNT_VALUE: 'giverCard__count-value',
    GIVER_CARD_COUNT_LABEL: 'giverCard__count-label',
    GIVER_CARD_DIVIDER: 'giverCard__divider',
    GIVER_CARD_TOPIC: 'giverCard__topic',
    GIVER_CARD_TOPIC_BUTTON: 'btn-topic-sm',
    GIVER_CARD_ACTION: 'giverCard__action',
    GIVER_CARD_ACTION_BUTTON: 'giverCard__action-button',
    PAGINATOR_ITEM: 'pagination__item',
    PAGINATOR_ITEM_ACTIVE: 'pagination__item--active',
    PAGINATOR_ITEM_DISABLED: 'pagination__item--disabled',
    PAGINATOR_LINK: 'pagination__link',
    PAGINATOR_LINK_PREV: 'pagination__link--prev',
    PAGINATOR_LINK_NEXT: 'pagination__link--next',
    PAGINATOR_LINK_PAGE: 'pagination__link--page'
  },
  
  // 預設值配置
  DEFAULTS: {
    GIVER: {
      NAME: '未知用戶',
      TITLE: '職位未填寫',
      COMPANY: '公司未填寫',
      CONSULTED: '0',
      RESPONDING_TIME: '未知',
      EXPERIENCE: '未知',
      IMAGE: 'men/1.jpg'
    }
  },
  
  // 錯誤訊息配置
  MESSAGES: {
    ERROR: {
      NETWORK: '網路連線異常，請檢查網路設定',
      LOADING: '資料載入失敗，請稍後再試',
      VALIDATION: '資料驗證失敗',
      UNKNOWN: '發生未知錯誤'
    },
    SUCCESS: {
      LOADING: '資料載入成功',
      SAVE: '資料儲存成功',
      UPDATE: '資料更新成功'
    },
    INFO: {
      LOADING: '載入中...',
      NO_DATA: '暫無資料',
      EMPTY_RESULT: '搜尋結果為空'
    }
  }
};

// =================================================================
//   全域常數設定 (Global Constants) - 為了向後相容，保留舊的常數引用
// =================================================================

const BASE_URL = CONFIG.API.BASE_URL;
const POSTER_URL = CONFIG.API.POSTER_URL;
const GIVERS_PER_PAGE = CONFIG.PAGINATION.GIVERS_PER_PAGE;

// =================================================================
//   應用程式狀態管理 (Application State Management)
// =================================================================

// 全域應用程式狀態
const appState = {
  // Giver 資料
  givers: [],
  
  // 當前頁面
  currentPage: 1,
  
  // 載入狀態
  isLoading: false,
  
  // 錯誤狀態
  error: null,
  
  // 聊天對話框實例
  giverModalInstance: null
};

// =================================================================
//   業務邏輯模組 (Business Logic Module)
// =================================================================

const BusinessLogic = {
  chat: {
    // 驗證訊息
    validateMessage: (message) => {
      console.log('BusinessLogic.chat.validateMessage called', { message });
      if (!message || typeof message !== 'string') return false;
      if (message.trim().length === 0) return false;
      if (message.length > CONFIG.CHAT.MAX_MESSAGE_LENGTH) return false;
      return true;
    },
    // 生成回應
    generateResponse: (userMessage) => {
      console.log('BusinessLogic.chat.generateResponse called', { userMessage });
      const responses = [
        '謝謝您的諮詢！我會盡快回覆您。',
        '您的問題很有價值，讓我為您詳細說明。',
        '根據我的經驗，我建議您可以這樣做...',
        '這是一個很好的問題，讓我分享一些實用的建議。',
        '我理解您的需求，讓我為您提供專業的建議。'
      ];
      const randomIndex = Math.floor(Math.random() * responses.length);
      return responses[randomIndex];
    }
  }
};

// =================================================================
//   日期時間處理模組 (Date Time Utilities Module)
// =================================================================

const DateUtils = {
  // 格式化選項
  FORMATS: {
    DATE: 'YYYY/MM/DD',
    TIME: 'HH:MM',
    DATETIME: 'YYYY/MM/DD HH:MM',
    TIMESTAMP: 'HH:MM:SS'
  },
  
  // 格式化日期為 YYYY/MM/DD
  formatDate: (date) => {
    console.log('DateUtils.formatDate called', { date });
    if (!date) return '';
    
    const d = new Date(date);
    if (isNaN(d.getTime())) return '';
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    const formatted = `${year}/${month}/${day}`;
    console.log('DateUtils.formatDate: 格式化結果', { original: date, formatted });
    return formatted;
  },
  
  // 格式化時間為 HH:MM
  formatTime: (date) => {
    console.log('DateUtils.formatTime called', { date });
    if (!date) return '';
    
    const d = new Date(date);
    if (isNaN(d.getTime())) return '';
    
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    
    const formatted = `${hours}:${minutes}`;
    console.log('DateUtils.formatTime: 格式化結果', { original: date, formatted });
    return formatted;
  },
  
  // 格式化為本地時間字串
  formatToLocalTime: (date) => {
    console.log('DateUtils.formatToLocalTime called', { date });
    if (!date) return '';
    
    const d = new Date(date);
    if (isNaN(d.getTime())) return '';
    
    const formatted = d.toLocaleTimeString('zh-TW', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
    
    console.log('DateUtils.formatToLocalTime: 格式化結果', { original: date, formatted });
    return formatted;
  },
  
  // 獲取今天的日期
  getToday: () => {
    console.log('DateUtils.getToday called');
    const today = new Date();
    console.log('DateUtils.getToday: 今天日期', today);
    return today;
  },
  
  // 比較兩個時間字串 (HH:MM 格式)
  compareTimes: (time1, time2) => {
    console.log('DateUtils.compareTimes called', { time1, time2 });
    
    if (!time1 || !time2) {
      console.warn('DateUtils.compareTimes: 時間參數為空', { time1, time2 });
      return 0;
    }
    
    // 將時間字串轉換為分鐘數（內部工具函式）
    const parseTime = (timeStr) => {
      console.log('DateUtils.compareTimes.parseTime called', { timeStr });
      const [hours, minutes] = timeStr.split(':').map(Number);
      return hours * 60 + minutes;
    };
    
    const minutes1 = parseTime(time1);
    const minutes2 = parseTime(time2);
    
    const result = minutes1 - minutes2;
    console.log('DateUtils.compareTimes: 比較結果', { time1, time2, minutes1, minutes2, result });
    return result;
  },
  
  // 驗證時間格式 (HH:MM)
  isValidTimeFormat: (timeStr) => {
    console.log('DateUtils.isValidTimeFormat called', { timeStr });
    
    if (!timeStr || typeof timeStr !== 'string') {
      console.log('DateUtils.isValidTimeFormat: 驗證結果', { isValid: false, reason: '空值或非字串' });
      return false;
    }
    
    const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
    const isValid = timeRegex.test(timeStr);
    
    console.log('DateUtils.isValidTimeFormat: 驗證結果', { isValid });
    return isValid;
  },
  
  // 驗證日期格式 (YYYY/MM/DD)
  isValidDateFormat: (dateStr) => {
    console.log('DateUtils.isValidDateFormat called', { dateStr });
    
    if (!dateStr || typeof dateStr !== 'string') {
      console.log('DateUtils.isValidDateFormat: 驗證結果', { isValid: false, reason: '空值或非字串' });
      return false;
    }
    
    const dateRegex = /^\d{4}\/\d{2}\/\d{2}$/;
    if (!dateRegex.test(dateStr)) {
      console.log('DateUtils.isValidDateFormat: 驗證結果', { isValid: false, reason: '格式不符' });
      return false;
    }
    
    const [year, month, day] = dateStr.split('/').map(Number);
    const date = new Date(year, month - 1, day);
    
    const isValid = date.getFullYear() === year &&
                   date.getMonth() === month - 1 &&
                   date.getDate() === day;
    
    console.log('DateUtils.isValidDateFormat: 驗證結果', { isValid });
    return isValid;
  },
  
  // 解析多筆時段字串
  parseMultipleSchedules: (message) => {
    console.log('DateUtils.parseMultipleSchedules called', { message });
    
    if (!message || typeof message !== 'string') {
      console.log('DateUtils.parseMultipleSchedules: 無效訊息', { message });
      return { isValid: false, schedules: [] };
    }
    
    const lines = message.split('\n').filter(line => line.trim());
    const schedules = [];
    
    for (const line of lines) {
      const trimmedLine = line.trim();
      if (!trimmedLine) continue;
      
      // 匹配格式：日期 時間範圍
      // 例如：2024/01/15 14:00-16:00
      const scheduleRegex = /(\d{4}\/\d{2}\/\d{2})\s+(\d{2}:\d{2})-(\d{2}:\d{2})/;
      const match = trimmedLine.match(scheduleRegex);
      
      if (match) {
        const [, date, startTime, endTime] = match;
        
        // 驗證日期和時間格式
        if (DateUtils.isValidDateFormat(date) && 
            DateUtils.isValidTimeFormat(startTime) && 
            DateUtils.isValidTimeFormat(endTime)) {
          
          // 驗證時間邏輯
          if (DateUtils.compareTimes(startTime, endTime) < 0) {
            const formattedSchedule = `${date} ${startTime}~${endTime}`;
            schedules.push({
              date,
              startTime,
              endTime,
              formattedSchedule,
              timestamp: new Date()
            });
          }
        }
      }
    }
    
    const isValid = schedules.length > 0;
    console.log('DateUtils.parseMultipleSchedules: 解析結果', { isValid, schedules });
    return { isValid, schedules };
  },
  
  // 新增：取得今天日期的格式化字串
  getTodayFormatted: function() {
    return this.formatDate(this.getToday());
  }
};

// =================================================================
//   表單驗證模組 (Form Validation Module)
// =================================================================

const FormValidator = {
  // 驗證規則配置
  RULES: {
    // 聊天訊息驗證規則
    CHAT_MESSAGE: {
      MAX_LENGTH: CONFIG.CHAT.MAX_MESSAGE_LENGTH,
      MIN_LENGTH: 1,
      ALLOWED_CHARS: /^[\s\S]*$/, // 允許所有字符
      FORBIDDEN_PATTERNS: [
        /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, // 防止 XSS
        /javascript:/gi,
        /on\w+\s*=/gi
      ]
    },
    
    // 時段表單驗證規則
    SCHEDULE_FORM: {
      DATE: {
        REQUIRED: true,
        FORMAT: 'YYYY/MM/DD',
        MIN_DATE: 'today', // 不能選擇過去的日期
        MAX_DATE: '+1year' // 最多預約一年後
      },
      TIME: {
        REQUIRED: true,
        FORMAT: 'HH:MM',
        MIN_TIME: '00:00',
        MAX_TIME: '23:59',
        BUSINESS_HOURS: {
          START: '09:00',
          END: '22:00'
        }
      },
      NOTES: {
        MAX_LENGTH: 500,
        ALLOWED_CHARS: /^[\s\S]*$/ // 允許所有字符
      }
    },
    
    // 多筆時段驗證規則
    MULTIPLE_SCHEDULES: {
      MAX_SCHEDULES: 10, // 最多一次提交 10 個時段
      MIN_SCHEDULES: 1,
      FORMAT_PATTERN: /^\d{4}\/\d{2}\/\d{2}\s+\d{2}:\d{2}-\d{2}:\d{2}$/,
      TIME_SEPARATOR: '-',
      LINE_SEPARATOR: '\n'
    }
  },
  
  // 錯誤訊息配置
  ERROR_MESSAGES: {
    // 聊天訊息錯誤
    CHAT_MESSAGE: {
      EMPTY: '訊息不能為空',
      TOO_LONG: `訊息長度不能超過 ${CONFIG.CHAT.MAX_MESSAGE_LENGTH} 個字符`,
      INVALID_CHARS: '訊息包含無效字符',
      FORBIDDEN_PATTERN: '訊息包含禁止的內容'
    },
    
    // 時段表單錯誤
    SCHEDULE_FORM: {
      DATE_REQUIRED: '請選擇日期',
      DATE_INVALID: '日期格式不正確，請使用 YYYY/MM/DD 格式',
      DATE_PAST: '不能選擇過去的日期',
      DATE_TOO_FAR: '不能預約超過一年後的日期',
      START_TIME_REQUIRED: '請選擇開始時間',
      END_TIME_REQUIRED: '請選擇結束時間',
      TIME_INVALID: '時間格式不正確，請使用 HH:MM 格式',
      TIME_LOGIC: '結束時間必須晚於開始時間',
      TIME_BUSINESS_HOURS: '時間必須在營業時間內（09:00-22:00）',
      NOTES_TOO_LONG: '備註不能超過 500 個字符',
      NOTES_INVALID: '備註包含無效字符',
      DUPLICATE_SCHEDULE: '您正輸入的時段，和您之前曾輸入的{{EXISTING_SCHEDULE}}時段重複或重疊，請重新輸入'
    },
    
    // 多筆時段錯誤
    MULTIPLE_SCHEDULES: {
      EMPTY: '請輸入時段資料',
      INVALID_FORMAT: '時段格式不正確，請使用：日期 時間範圍\n例如：2024/01/15 14:00-16:00',
      TOO_MANY: '一次最多只能提交 10 個時段',
      NO_VALID_SCHEDULES: '沒有有效的時段資料'
    }
  },

  // 生成重複時段詳細錯誤訊息
  generateDuplicateScheduleMessage: (newSchedule, existingSchedules) => {
    console.log('FormValidator.generateDuplicateScheduleMessage called', { newSchedule, existingSchedules });
    const conflictingSchedules = [];
    
    existingSchedules.forEach((schedule, index) => {
      // 檢查是否為完全相同的時段
      const isExactDuplicate = schedule.date === newSchedule.date && 
        schedule.startTime === newSchedule.startTime && 
        schedule.endTime === newSchedule.endTime;
      
      if (isExactDuplicate) {
        conflictingSchedules.push({
          type: 'exact',
          schedule: schedule,
          index: index
        });
        return;
      }
      
      // 檢查是否為重疊時段（相同日期且時間有重疊）
      if (schedule.date === newSchedule.date) {
        const existingStart = schedule.startTime;
        const existingEnd = schedule.endTime;
        const newStart = newSchedule.startTime;
        const newEnd = newSchedule.endTime;
        
        // 檢查時間重疊：新時段的開始時間 < 現有時段的結束時間 且 新時段的結束時間 > 現有時段的開始時間
        const isOverlapping = newStart < existingEnd && newEnd > existingStart;
        
        if (isOverlapping) {
          conflictingSchedules.push({
            type: 'overlapping',
            schedule: schedule,
            index: index
          });
        }
      }
    });
    
    if (conflictingSchedules.length === 0) {
      return null;
    }
    
    // 生成詳細錯誤訊息
    const conflictingList = conflictingSchedules.map(conflict => {
      const schedule = conflict.schedule;
      const formattedSchedule = `${schedule.date} ${schedule.startTime}~${schedule.endTime}`;
      return formattedSchedule;
    });
    
    if (conflictingList.length === 1) {
      return FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.DUPLICATE_SCHEDULE.replace('{{EXISTING_SCHEDULE}}', conflictingList[0]);
    } else {
      const scheduleList = conflictingList.join('、');
      return `您正輸入的時段，和您之前曾輸入的以下時段重複或重疊，請重新輸入：\n${scheduleList}`;
    }
  },

  // 驗證聊天訊息
  validateChatMessage: (message) => {
    console.log('FormValidator.validateChatMessage called', { message });
    
    const rules = FormValidator.RULES.CHAT_MESSAGE;
    const errors = [];
    
    // 檢查是否為空
    if (!message || typeof message !== 'string') {
      errors.push(FormValidator.ERROR_MESSAGES.CHAT_MESSAGE.EMPTY);
    } else {
      const trimmedMessage = message.trim();
      
      // 檢查長度
      if (trimmedMessage.length === 0) {
        errors.push(FormValidator.ERROR_MESSAGES.CHAT_MESSAGE.EMPTY);
      } else if (trimmedMessage.length > rules.MAX_LENGTH) {
        errors.push(FormValidator.ERROR_MESSAGES.CHAT_MESSAGE.TOO_LONG);
      }
      
      // 檢查禁止的模式
      for (const pattern of rules.FORBIDDEN_PATTERNS) {
        if (pattern.test(trimmedMessage)) {
          errors.push(FormValidator.ERROR_MESSAGES.CHAT_MESSAGE.FORBIDDEN_PATTERN);
          break;
        }
      }
    }
    
    const isValid = errors.length === 0;
    console.log('FormValidator.validateChatMessage: 驗證結果', { isValid, errors });
    
    return {
      isValid,
      errors,
      message: errors.length > 0 ? errors[0] : null
    };
  },
  
  // 驗證時段表單
  validateScheduleForm: (formData) => {
    console.log('FormValidator.validateScheduleForm called', { formData });
    
    const rules = FormValidator.RULES.SCHEDULE_FORM;
    const errors = [];
    
    // 驗證日期
    if (rules.DATE.REQUIRED && (!formData.date || !formData.date.trim())) {
      errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.DATE_REQUIRED);
    } else if (formData.date) {
      if (!DateUtils.isValidDateFormat(formData.date)) {
        errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.DATE_INVALID);
      } else {
        // 檢查是否為過去日期
        const today = DateUtils.getToday();
        const selectedDate = new Date(formData.date.replace(/\//g, '-'));
        if (selectedDate < new Date(today.getFullYear(), today.getMonth(), today.getDate())) {
          errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.DATE_PAST);
        }
        
        // 檢查是否超過一年
        const oneYearLater = new Date(today.getFullYear() + 1, today.getMonth(), today.getDate());
        if (selectedDate > oneYearLater) {
          errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.DATE_TOO_FAR);
        }
      }
    }
    
    // 驗證開始時間
    if (rules.TIME.REQUIRED && (!formData.startTime || !formData.startTime.trim())) {
      errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.START_TIME_REQUIRED);
    } else if (formData.startTime && !DateUtils.isValidTimeFormat(formData.startTime)) {
      errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.TIME_INVALID);
    }
    
    // 驗證結束時間
    if (rules.TIME.REQUIRED && (!formData.endTime || !formData.endTime.trim())) {
      errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.END_TIME_REQUIRED);
    } else if (formData.endTime && !DateUtils.isValidTimeFormat(formData.endTime)) {
      errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.TIME_INVALID);
    }
    
    // 驗證時間邏輯
    if (formData.startTime && formData.endTime && 
        DateUtils.isValidTimeFormat(formData.startTime) && 
        DateUtils.isValidTimeFormat(formData.endTime)) {
      
      if (DateUtils.compareTimes(formData.startTime, formData.endTime) >= 0) {
        errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.TIME_LOGIC);
      }
      
      // 檢查營業時間
      const businessStart = rules.TIME.BUSINESS_HOURS.START;
      const businessEnd = rules.TIME.BUSINESS_HOURS.END;
      
      if (DateUtils.compareTimes(formData.startTime, businessStart) < 0 ||
          DateUtils.compareTimes(formData.endTime, businessEnd) > 0) {
        errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.TIME_BUSINESS_HOURS);
      }
    }
    
    // 驗證備註
    if (formData.notes && formData.notes.trim()) {
      const notes = formData.notes.trim();
      
      if (notes.length > rules.NOTES.MAX_LENGTH) {
        errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.NOTES_TOO_LONG);
      }
      
      if (!rules.NOTES.ALLOWED_CHARS.test(notes)) {
        errors.push(FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.NOTES_INVALID);
      }
    }
    
    const isValid = errors.length === 0;
    console.log('FormValidator.validateScheduleForm: 驗證結果', { isValid, errors });
    
    return {
      isValid,
      errors,
      message: errors.length > 0 ? errors[0] : null
    };
  },
  
  // 驗證多筆時段
  validateMultipleSchedules: (message) => {
    console.log('FormValidator.validateMultipleSchedules called', { message });
    
    const rules = FormValidator.RULES.MULTIPLE_SCHEDULES;
    const errors = [];
    
    // 檢查是否為空
    if (!message || typeof message !== 'string' || !message.trim()) {
      errors.push(FormValidator.ERROR_MESSAGES.MULTIPLE_SCHEDULES.EMPTY);
    } else {
      // 使用 DateUtils 解析多筆時段
      const { isValid, schedules } = DateUtils.parseMultipleSchedules(message);
      
      if (!isValid) {
        errors.push(FormValidator.ERROR_MESSAGES.MULTIPLE_SCHEDULES.INVALID_FORMAT);
      } else if (schedules.length > rules.MAX_SCHEDULES) {
        errors.push(FormValidator.ERROR_MESSAGES.MULTIPLE_SCHEDULES.TOO_MANY);
      } else if (schedules.length < rules.MIN_SCHEDULES) {
        errors.push(FormValidator.ERROR_MESSAGES.MULTIPLE_SCHEDULES.NO_VALID_SCHEDULES);
      }
    }
    
    const isValid = errors.length === 0;
    console.log('FormValidator.validateMultipleSchedules: 驗證結果', { isValid, errors });
    
    return {
      isValid,
      errors,
      message: errors.length > 0 ? errors[0] : null
    };
  },
  
  // 驗證表單欄位（即時驗證）
  validateField: (fieldName, value, formType = 'schedule') => {
    console.log('FormValidator.validateField called', { fieldName, value, formType });
    
    let isValid = true;
    let errorMessage = null;
    
    switch (formType) {
      case 'schedule':
        switch (fieldName) {
          case 'date':
            if (!value || !value.trim()) {
              isValid = false;
              errorMessage = FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.DATE_REQUIRED;
            } else if (!DateUtils.isValidDateFormat(value)) {
              isValid = false;
              errorMessage = FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.DATE_INVALID;
            }
            break;
            
          case 'startTime':
          case 'endTime':
            if (!value || !value.trim()) {
              isValid = false;
              errorMessage = fieldName === 'startTime' 
                ? FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.START_TIME_REQUIRED
                : FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.END_TIME_REQUIRED;
            } else if (!DateUtils.isValidTimeFormat(value)) {
              isValid = false;
              errorMessage = FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.TIME_INVALID;
            }
            break;
            
          case 'notes':
            if (value && value.trim().length > FormValidator.RULES.SCHEDULE_FORM.NOTES.MAX_LENGTH) {
              isValid = false;
              errorMessage = FormValidator.ERROR_MESSAGES.SCHEDULE_FORM.NOTES_TOO_LONG;
            }
            break;
        }
        break;
        
      case 'chat':
        if (fieldName === 'message') {
          const result = FormValidator.validateChatMessage(value);
          isValid = result.isValid;
          errorMessage = result.message;
        }
        break;
    }
    
    console.log('FormValidator.validateField: 驗證結果', { isValid, errorMessage });
    
    return {
      isValid,
      errorMessage
    };
  },
  
  // 顯示驗證錯誤
  showValidationError: (message, element = null) => {
    console.log('FormValidator.showValidationError called', { message, element });
    
    if (element) {
      // 在特定元素上顯示錯誤
      const errorElement = element.querySelector('.validation-error') || 
                          element.parentNode.querySelector('.validation-error');
      
      if (errorElement) {
        errorElement.textContent = message;
        if (message) {
          errorElement.classList.remove('error-hidden');
          errorElement.classList.add('error-visible');
        } else {
          errorElement.classList.remove('error-visible');
          errorElement.classList.add('error-hidden');
        }
      } else {
        // 創建錯誤元素
        const errorDiv = document.createElement('div');
        errorDiv.className = 'validation-error text-danger small mt-1';
        errorDiv.textContent = message;
        if (message) {
          errorDiv.classList.add('error-visible');
        } else {
          errorDiv.classList.add('error-hidden');
        }
        element.parentNode.appendChild(errorDiv);
      }
    } else {
      // 使用 alert 顯示錯誤
      if (message) {
        alert(message);
      }
    }
  },
  
  // 清除驗證錯誤
  clearValidationError: (element) => {
    console.log('FormValidator.clearValidationError called', { element });
    
    if (element) {
      const errorElement = element.querySelector('.validation-error') || 
                          element.parentNode.querySelector('.validation-error');
      
      if (errorElement) {
        errorElement.classList.remove('error-visible');
        errorElement.classList.add('error-hidden');
        errorElement.textContent = '';
      }
    }
  },
  
  // 驗證整個表單並返回結果
  validateForm: (formElement, formType = 'schedule') => {
    console.log('FormValidator.validateForm called', { formElement, formType });
    
    const formData = {};
    const errors = [];
    
    // 收集表單資料
    const inputs = formElement.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      if (input.name || input.id) {
        const fieldName = input.name || input.id.replace(/^schedule-/, '');
        formData[fieldName] = input.value;
      }
    });
    
    console.log('FormValidator.validateForm: 收集的表單資料', formData);
    
    // 根據表單類型進行驗證
    let validationResult;
    switch (formType) {
      case 'schedule':
        validationResult = FormValidator.validateScheduleForm(formData);
        break;
      case 'chat':
        validationResult = FormValidator.validateChatMessage(formData.message || '');
        break;
      case 'multiple-schedules':
        validationResult = FormValidator.validateMultipleSchedules(formData.message || '');
        break;
      default:
        validationResult = { isValid: false, errors: ['未知的表單類型'] };
    }
    
    // 清除所有錯誤顯示
    inputs.forEach(input => {
      FormValidator.clearValidationError(input);
    });
    
    // 顯示錯誤
    if (!validationResult.isValid) {
      validationResult.errors.forEach(error => {
        FormValidator.showValidationError(error);
      });
    }
    
    console.log('FormValidator.validateForm: 驗證結果', validationResult);
    
    return validationResult;
  }
};

// =================================================================
//   UI 互動模組 (UI Interaction Module)
// =================================================================

const UIInteraction = {
  // 開啟聊天對話框
  openChatDialog: (giver) => {
    console.log('UIInteraction.openChatDialog called', { giver });
    DOM.chat.init(giver);
  },
  
  // 顯示確認對話框
  showConfirmDialog: (options) => {
    console.log('UIInteraction.showConfirmDialog called', { options });
    const { // options 是一個物件，預設為以下屬性：
      title = '確認',
      message = '您確定要執行此操作嗎？',
      confirmText = '確定',
      cancelText = '取消',
      onConfirm = () => {}, // 預設為空函式
      onCancel = () => {}, // 預設為空函式
      cleanupBackdrop = true // 預設為 true，控制是否清理 backdrop 背景遮罩
    } = options;
    
    // 更新確認對話框內容
    const modalTitle = DOM.confirm.title();
    const modalMessage = DOM.confirm.message();
    const confirmBtn = DOM.confirm.confirmBtn();
    const cancelBtn = DOM.confirm.cancelBtn();
    
    if (modalTitle) DOM.utils.setTextContent(modalTitle, title);
    if (modalMessage) DOM.utils.setTextContent(modalMessage, message);
    if (confirmBtn) DOM.utils.setTextContent(confirmBtn, confirmText);
    if (cancelBtn) DOM.utils.setTextContent(cancelBtn, cancelText);
    
    // 確認按鈕事件監聽器（內部函式）：當使用者點擊確認按鈕時，會執行 onConfirm 函式，這通常是實際要執行的業務邏輯（如刪除資料、取消預約等）
    const confirmHandler = () => {
      console.log('confirmHandler called');
      onConfirm(); // 執行傳入的 onConfirm 函式，這通常是實際要執行的業務邏輯（如刪除資料、取消預約等）
      const modal = bootstrap.Modal.getInstance(DOM.confirm.modal());
      if (modal) {
        modal.hide(); // 隱藏對話框
        // 只有在需要清理 backdrop 時才清理
        if (cleanupBackdrop) {
          setTimeout(() => {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) backdrop.remove();
            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = ''; // paddingRight 樣式是 Bootstrap 為防止頁面跳動而添加的樣式
            // 強制處理焦點問題
            document.body.focus();
          }, 150);
        }
      }
    };
    
    // 取消按鈕事件監聽器（內部函式）：當使用者點擊取消按鈕時，會執行 onCancel 函式，這通常是實際要執行的業務邏輯（如取消預約等）
    const cancelHandler = () => {
      console.log('cancelHandler called');
      onCancel(); // 執行傳入的 onCancel 函式，這通常是實際要執行的業務邏輯（如取消預約等）
      const modal = bootstrap.Modal.getInstance(DOM.confirm.modal());
      if (modal) {
        modal.hide();
        // 確保 backdrop 被清理
        setTimeout(() => {
          const backdrop = document.querySelector('.modal-backdrop');
          if (backdrop) backdrop.remove();
          document.body.classList.remove('modal-open');
          document.body.style.paddingRight = '';
          // 強制處理焦點問題
          document.body.focus();
        }, 150);
      }
    };
    
    // 移除舊的事件監聽器：解決重覆綁定事件監聽器
    if (confirmBtn) { // 如果確認按鈕存在
      // 使用 cloneNode 來移除所有舊的事件監聽器
      const newConfirmBtn = confirmBtn.cloneNode(true); // 複製確認按鈕
      confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn); // 替換確認按鈕
      newConfirmBtn.addEventListener('click', confirmHandler); // 綁定確認按鈕的事件監聽器
    }
    
    if (cancelBtn) { // 如果取消按鈕存在
      const newCancelBtn = cancelBtn.cloneNode(true); // 複製取消按鈕
      cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn); // 替換取消按鈕
      newCancelBtn.addEventListener('click', cancelHandler); // 綁定取消按鈕的事件監聽器
    }
    
    // 顯示確認對話框，讓使用者可以看到確認對話框並進行相應的操作。
    const modal = new bootstrap.Modal(DOM.confirm.modal());
    modal.show();
  }
};

// =================================================================
//   模板管理 (Template Management)
// =================================================================

const TEMPLATES = {
  // Giver 卡片模板
  giverCard: (giver) => {
    console.log('TEMPLATES.giverCard called', { giver });
      const {
        id,
        name = CONFIG.DEFAULTS.GIVER.NAME,
        title = CONFIG.DEFAULTS.GIVER.TITLE,
        company = CONFIG.DEFAULTS.GIVER.COMPANY,
        consulted = CONFIG.DEFAULTS.GIVER.CONSULTED,
        average_responding_time = CONFIG.DEFAULTS.GIVER.RESPONDING_TIME,
        experience = CONFIG.DEFAULTS.GIVER.EXPERIENCE,
        image,
        giverCard__topic = []
      } = giver;
    console.log('giverCard template variables:', {
      id,
      name,
      title,
      company,
      consulted,
      average_responding_time,
      experience,
      image,
      giverCard__topic
    });

    // 生成服務項目按鈕 HTML
      const topicButtonsHTML = Array.isArray(giverCard__topic) 
        ? giverCard__topic.map(topic => 
            `<span class="${CONFIG.CLASSES.GIVER_CARD_TOPIC_BUTTON}" data-topic="${topic}">${topic}</span>`
          ).join('')
        : '';

      const imageUrl = image || CONFIG.API.POSTER_URL + CONFIG.DEFAULTS.GIVER.IMAGE;

      return `
        <article class="${CONFIG.CLASSES.GIVER_CARD_WRAPPER}"> 
          <button class="${CONFIG.CLASSES.GIVER_CARD} ${CONFIG.CLASSES.GIVER_CARD_POINTER}" data-id="${id}" type="button" aria-label="選擇${name}進行諮詢">
            <div class="${CONFIG.CLASSES.GIVER_CARD_AVATAR}"> 
              <div class="${CONFIG.CLASSES.GIVER_CARD_AVATAR_CONTAINER}">
                <img
                  src="${imageUrl}"
                  alt="${name} 的頭像" 
                  class="${CONFIG.CLASSES.GIVER_CARD_AVATAR_IMG}"
                >
              </div>

              <div class="${CONFIG.CLASSES.GIVER_CARD_USER_INFO}">
                <div class="${CONFIG.CLASSES.GIVER_CARD_NAME}">
                  <span>${name}</span>
                  <i class="fa-solid fa-chevron-right ${CONFIG.CLASSES.GIVER_CARD_ICON_GRAY}" aria-hidden="true"></i>
                </div>
                <div class="${CONFIG.CLASSES.GIVER_CARD_TITLE}">${title}</div>
                <div class="${CONFIG.CLASSES.GIVER_CARD_COMPANY}">${company}</div>
              </div> 
            </div>

            <div class="${CONFIG.CLASSES.GIVER_CARD_COUNT}">
              <div class="${CONFIG.CLASSES.GIVER_CARD_COUNT_ITEM}">
                <span class="${CONFIG.CLASSES.GIVER_CARD_COUNT_VALUE}">${consulted} 人</span>
                <p class="${CONFIG.CLASSES.GIVER_CARD_COUNT_LABEL}">已諮詢</p>
              </div>
              <div class="${CONFIG.CLASSES.GIVER_CARD_DIVIDER}" aria-hidden="true"></div>
              <div class="${CONFIG.CLASSES.GIVER_CARD_COUNT_ITEM}">
                <span class="${CONFIG.CLASSES.GIVER_CARD_COUNT_VALUE}">${average_responding_time} 天</span>
                <p class="${CONFIG.CLASSES.GIVER_CARD_COUNT_LABEL}">平均回覆時間</p>
              </div>
              <div class="${CONFIG.CLASSES.GIVER_CARD_DIVIDER}" aria-hidden="true"></div>
              <div class="${CONFIG.CLASSES.GIVER_CARD_COUNT_ITEM}">
                <span class="${CONFIG.CLASSES.GIVER_CARD_COUNT_VALUE}">${experience} 年</span>
                <p class="${CONFIG.CLASSES.GIVER_CARD_COUNT_LABEL}">工作經驗</p>
              </div>
            </div>

            <div class="${CONFIG.CLASSES.GIVER_CARD_TOPIC}">                            
              ${topicButtonsHTML}
              <i class="fa-solid fa-chevron-right ${CONFIG.CLASSES.GIVER_CARD_ICON_GRAY}" aria-hidden="true"></i>
          </div>

          <div class="${CONFIG.CLASSES.GIVER_CARD_ACTION}">
            <button 
              data-gtm-check="Giver列表_我要諮詢" 
              class="btn btn-orange ${CONFIG.CLASSES.GIVER_CARD_ACTION_BUTTON}"
              data-id="${id}" aria-label="我要諮詢${name}">
              我要諮詢
            </button>
          </div>
        </button>
      </article>
    `;
  },

  // Giver 卡片包裝器模板
  giverCardWrapper: (cardHTML) => `
  <div class="col-sm-3">${cardHTML}</div>
  `,

  // 分頁導覽模板
  paginator: {
    // 頁碼按鈕模板
    item: (pageNumber) => `
      <li class="${CONFIG.CLASSES.PAGINATOR_ITEM} ${pageNumber === appState.currentPage ? CONFIG.CLASSES.PAGINATOR_ITEM_ACTIVE : CONFIG.CLASSES.PAGINATOR_ITEM_DISABLED}">
        <a class="${CONFIG.CLASSES.PAGINATOR_LINK} ${CONFIG.CLASSES.PAGINATOR_LINK_PAGE}" href="#" data-page="${pageNumber}" aria-label="第 ${pageNumber} 頁">${pageNumber}</a>
      </li>
    `,

    // 分頁導覽容器模板
    container: () => '<ul class="pagination paginator-container" role="navigation" aria-label="分頁導覽">',

    // 上一頁按鈕模板
    prevButton: () => `
      <li class="${CONFIG.CLASSES.PAGINATOR_ITEM} ${CONFIG.CLASSES.PAGINATOR_ITEM_DISABLED}">
        <a class="${CONFIG.CLASSES.PAGINATOR_LINK} ${CONFIG.CLASSES.PAGINATOR_LINK_PREV}" href="#" data-page="prev" aria-label="前往上一頁" aria-disabled="true">
          <i class="fas fa-chevron-left"></i>
        </a>
      </li>
    `,

    // 下一頁按鈕模板
    nextButton: () => `
      <li class="${CONFIG.CLASSES.PAGINATOR_ITEM}">
        <a class="${CONFIG.CLASSES.PAGINATOR_LINK} ${CONFIG.CLASSES.PAGINATOR_LINK_NEXT}" href="#" data-page="next" aria-label="前往下一頁">
          <i class="fas fa-chevron-right"></i>
        </a>
      </li>
    `,

    // 省略號模板
    ellipsis: () => `
      <li class="${CONFIG.CLASSES.PAGINATOR_ITEM} ${CONFIG.CLASSES.PAGINATOR_ITEM_ACTIVE}">
        <span class="${CONFIG.CLASSES.PAGINATOR_LINK} ${CONFIG.CLASSES.PAGINATOR_LINK_PAGE}" aria-hidden="true">...</span>
      </li>
    `,

    // 頁碼按鈕模板
    pageNumber: (pageNumber, isActive) => `
      <li class="${CONFIG.CLASSES.PAGINATOR_ITEM} ${isActive ? CONFIG.CLASSES.PAGINATOR_ITEM_ACTIVE : CONFIG.CLASSES.PAGINATOR_ITEM_DISABLED}">
        <a class="${CONFIG.CLASSES.PAGINATOR_LINK} ${CONFIG.CLASSES.PAGINATOR_LINK_PAGE}" href="#" data-page="${pageNumber}" aria-label="第 ${pageNumber} 頁" ${isActive ? 'aria-current="page"' : ''}>${pageNumber}</a>
      </li>
    `,
  },

  // 無資料提示模板
  noDataMessage: () => `
    <div class="text-center py-5">
      <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
      <p class="text-muted">${CONFIG.MESSAGES.INFO.NO_DATA}</p>
    </div>
  `,

  // 聊天相關模板
  chat: {
    // 初始聊天訊息模板
    initialMessage: () => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
          <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">如想與 Giver 進行諮詢，例如線上模擬面試、即時文字訊息往返，請點此預約 Giver 時間。</p>
          <!-- 直接顯示的選項按鈕 -->
          <div class="chat-options-buttons">
            <button class="btn btn-outline btn-option" data-option="schedule">
              我想預約 Giver 時間
            </button>
            <button class="btn btn-outline btn-option" data-option="skip">
              暫不預約 Giver 時間
            </button>
          </div>
        </div>
      </div>
    `,

    // 預約選項按鈕模板
    scheduleOptions: () => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
            <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">好的！我來幫您安排預約時間。請選擇以下選項：</p>
          <div class="chat-options-buttons mt-2">
            <button class="btn btn-outline btn-option chat-option-btn" data-option="view-times">查看 Giver 方便的時間</button>
            <button class="btn btn-outline btn-option chat-option-btn" data-option="single-time">提供單筆方便時段</button>
            <button class="btn btn-outline btn-option chat-option-btn" data-option="multiple-times">提供多筆方便時段</button>
            <button class="btn btn-outline-secondary btn-option chat-option-btn" data-option="cancel">取消本次預約 Giver 時間</button>
          </div>
        </div>
      </div>
    `,

    // 預約表單模板
    scheduleForm: () => `
      <div id="schedule-form" class="message user-message schedule-form-visible">
        <div class="message-content-giver">
          <p class="message-title">請提供您的方便時段：</p>
          <form id="time-schedule-form" class="schedule-form">
            <div class="form-group mb-3">
              <label for="schedule-date" class="form-label">日期 <span class="text-danger">*</span></label>
              <input type="text" id="schedule-date" class="form-control" placeholder="請選擇日期" required>
            </div>
            <div class="row">
              <div class="col-md-6">
                <div class="form-group mb-3">
                  <label for="schedule-start-time" class="form-label">起（幾時幾分）<span class="text-danger">*</span></label>
                  <input type="text" id="schedule-start-time" class="form-control" placeholder="例：14:30" required>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-group mb-3">
                  <label for="schedule-end-time" class="form-label">迄（幾時幾分）<span class="text-danger">*</span></label>
                  <input type="text" id="schedule-end-time" class="form-control" placeholder="例：15:30" required>
                </div>
              </div>
            </div>
            <div class="form-group mb-3">
              <label for="schedule-notes" class="form-label">備註</label>
              <textarea id="schedule-notes" class="form-control" rows="3" placeholder="請輸入備註（非必填）"></textarea>
            </div>
            <div class="d-flex justify-content-end">
              <button type="submit" class="btn btn-orange">輸入完成</button>
            </div>
          </form>
        </div>
      </div>
    `,

    // 表單提交後選項按鈕模板
    afterScheduleOptions: (formattedSchedule, notes) => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
          <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">您已成功提供方便時段：${formattedSchedule}${notes ? `<br>備註：${notes}` : ''}<br><br>請選擇接下來的動作：</p>
          <div class="chat-options-buttons mt-2" id="after-schedule-options">
            <button class="btn btn-outline btn-option" data-option="single-time">繼續提供單筆方便時段</button>
            <button class="btn btn-outline btn-option" data-option="multiple-times">繼續提供多筆方便時段</button>
            <button class="btn btn-outline btn-option" data-option="view-all">查看所有我已提供的時段</button>
            <button class="btn btn-orange btn-option" data-option="finish">已新增完成所有時段，請協助送出給 Giver</button>
            <button class="btn btn-outline-secondary btn-option" data-option="cancel">取消本次預約 Giver 時間</button>
          </div>
        </div>
      </div>
    `,

    // 多筆時段提交後選項按鈕模板
    afterMultipleScheduleOptions: () => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
          <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">已成功記錄以下時段：<br>{{SCHEDULE_LIST}}<br>共 {{SCHEDULE_COUNT}} 個時段已記錄。<br><br>請選擇接下來的動作：</p>
          <div class="chat-options-buttons mt-2" id="after-multiple-schedule-options">
            <button class="btn btn-outline btn-option" data-option="single-time">繼續提供單筆方便時段</button>
            <button class="btn btn-outline btn-option" data-option="multiple-times">繼續提供多筆方便時段</button>
            <button class="btn btn-outline btn-option" data-option="view-all">查看所有我已提供的時段</button>
            <button class="btn btn-orange btn-option" data-option="finish">已新增完成所有時段，請協助送出給 Giver</button>
            <button class="btn btn-outline-secondary btn-option" data-option="cancel">取消本次預約 Giver 時間</button>
          </div>
        </div>
      </div>
    `,

    // 查看所有時段選項按鈕模板
    viewAllSchedulesOptions: (scheduleList, scheduleCount) => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
          <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">您目前已提供 ${scheduleCount} 個時段如下：<br>${scheduleList}<br>請選擇接下來的動作：</p>
          <div class="chat-options-buttons mt-2" id="after-view-all-options">
            <button class="btn btn-outline btn-option" data-option="single-time">繼續提供單筆方便時段</button>
            <button class="btn btn-outline btn-option" data-option="multiple-times">繼續提供多筆方便時段</button>
            <button class="btn btn-orange btn-option" data-option="finish">已新增完成所有時段，請協助送出給 Giver</button>
            <button class="btn btn-outline-secondary btn-option" data-option="cancel">取消本次預約 Giver 時間</button>
          </div>
        </div>
      </div>
    `,

    // 時段表格模板
    scheduleTable: (schedules) => {
      console.log('TEMPLATES.chat.scheduleTable called', { schedules });
      let tableRows = '';
      schedules.forEach((schedule, index) => {
        const scheduleNumber = index + 1;
        const dateObj = new Date(schedule.date);
        const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
        const weekday = weekdays[dateObj.getDay()];
        const formattedDate = schedule.date;
        const startTime = schedule.startTime || '';
        const endTime = schedule.endTime || '';
        const notes = schedule.notes || '';
        const period = `${formattedDate}（週${weekday}）${startTime}~${endTime}`;
        tableRows += `
          <tr data-index="${index}">
            <td class="text-center">${scheduleNumber}</td>
            <td>${period}</td>
            <td><span class="schedule-notes-text">${notes}</span></td>
            <td class="text-center">
              <div class="d-flex gap-1 justify-content-center">
                <button class="btn btn-link btn-sm p-0 schedule-edit-btn">修改</button>
                <button class="btn btn-link btn-sm text-danger p-0 schedule-delete-btn">刪除</button>
              </div>
            </td>
          </tr>
        `;
      });
      const scheduleCount = schedules.length;
      return `
        <div class="message giver-message">
          <div class="d-flex align-items-center">
            <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
          </div>
          <div class="message-content">
            <p class="message-title">您目前已提供 ${scheduleCount} 個時段如下：</p>
            <div class="table-responsive mt-2">
              <table class="table table-sm table-bordered table-hover schedule-table">
                <thead class="table-light">
                  <tr>
                    <th class="text-center">序</th>
                    <th class="text-center">時段</th>
                    <th class="text-center">備註</th>
                    <th class="text-center">調整</th>
                  </tr>
                </thead>
                <tbody>
                  ${tableRows}
                </tbody>
              </table>
            </div>
            <p class="mt-2">請選擇接下來的動作：</p>
            <div class="chat-options-buttons mt-2" id="after-view-all-options">
              <button class="btn btn-outline btn-option" data-option="single-time">繼續提供單筆方便時段</button>
              <button class="btn btn-outline btn-option" data-option="multiple-times">繼續提供多筆方便時段</button>
              <button class="btn btn-orange btn-option" data-option="finish">已新增完成所有時段，請協助送出給 Giver</button>
              <button class="btn btn-outline-secondary btn-option" data-option="cancel">取消本次預約 Giver 時間</button>
            </div>
          </div>
        </div>
      `;
    },

    // 新增 5 按鈕版本模板
    scheduleOptionsWithViewAll: () => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
            <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">好的！我來幫您安排預約時間。請選擇以下選項：</p>
          <div class="chat-options-buttons mt-2">
            <button class="btn btn-outline btn-option chat-option-btn" data-option="view-times">查看 Giver 方便的時間</button>
            <button class="btn btn-outline btn-option chat-option-btn" data-option="single-time">提供單筆方便時段</button>
            <button class="btn btn-outline btn-option chat-option-btn" data-option="multiple-times">提供多筆方便時段</button>
            <button class="btn btn-outline btn-option chat-option-btn" data-option="view-all">查看所有我已提供的時段</button>
            <button class="btn btn-outline-secondary btn-option chat-option-btn" data-option="cancel">取消本次預約 Giver 時間</button>
          </div>
        </div>
      </div>
    `,

    onlyScheduleButtons: () => `
      <div class="chat-options-buttons mt-2">
        <button class="btn btn-outline btn-option chat-option-btn" data-option="view-times">查看 Giver 方便的時間</button>
        <button class="btn btn-outline btn-option chat-option-btn" data-option="single-time">提供單筆方便時段</button>
        <button class="btn btn-outline btn-option chat-option-btn" data-option="multiple-times">提供多筆方便時段</button>
        <button class="btn btn-outline-secondary btn-option chat-option-btn" data-option="cancel">取消本次預約 Giver 時間</button>
      </div>
    `,

    noSchedulesWithButtons: () => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
          <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">您目前還沒有提供任何時段，請先提供方便時段，然後再查看。</p>
          <div class="chat-options-buttons mt-2">
            <button class="btn btn-outline btn-option chat-option-btn" data-option="view-times">查看 Giver 方便的時間</button>
            <button class="btn btn-outline btn-option chat-option-btn" data-option="single-time">提供單筆方便時段</button>
            <button class="btn btn-outline btn-option chat-option-btn" data-option="multiple-times">提供多筆方便時段</button>
            <button class="btn btn-outline-secondary btn-option chat-option-btn" data-option="cancel">取消本次預約 Giver 時間</button>
          </div>
        </div>
      </div>
    `,

    // 新增：Giver 尚末提供方便時間的模板
    noGiverTimesWithButtons: () => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
          <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">Giver 尚末提供方便的時間。請選擇以下選項：</p>
          <div class="chat-options-buttons mt-2">
            <button class="btn btn-outline btn-option chat-option-btn" data-option="single-time">提供單筆方便時段</button>
            <button class="btn btn-outline btn-option chat-option-btn" data-option="multiple-times">提供多筆方便時段</button>
            <button class="btn btn-outline-secondary btn-option chat-option-btn" data-option="cancel">取消本次預約 Giver 時間</button>
          </div>
        </div>
      </div>
    `,

    // 新增：多筆時段功能在建置中的模板
    multipleTimesUnderConstruction: () => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
          <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">此功能仍在建置中，請先使用「提供單筆方便時段」方式新增時間，謝謝。</p>
          <div class="chat-options-buttons mt-2" id="multiple-times-under-construction-options">
            <button class="btn btn-outline btn-option chat-option-btn" data-option="single-time">提供單筆方便時段</button>
            <button class="btn btn-outline-secondary btn-option chat-option-btn" data-option="cancel">取消本次預約 Giver 時間</button>
          </div>
        </div>
      </div>
    `,

    // 新增：成功提供時間的模板
    successProvideTime: (schedules) => {
      console.log('TEMPLATES.chat.successProvideTime called', { schedules });
      let tableRows = '';
      schedules.forEach((schedule, index) => {
        const scheduleNumber = index + 1;
        const dateObj = new Date(schedule.date);
        const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
        const weekday = weekdays[dateObj.getDay()];
        const formattedDate = schedule.date;
        const startTime = schedule.startTime || '';
        const endTime = schedule.endTime || '';
        const notes = schedule.notes || '';
        const period = `${formattedDate}（週${weekday}）${startTime}~${endTime}`;
        tableRows += `
          <tr data-index="${index}">
            <td class="text-center">${scheduleNumber}</td>
            <td class="text-center text-warning">成功提供時間，待 Giver 回覆</td>
            <td class="text-center">${period}</td>
            <td class="text-center">${notes}</td>
            <td class="text-center">
              <div class="d-flex gap-1 justify-content-center">
                <button class="btn btn-link btn-sm p-0 edit-provide-btn" data-option="edit-provide-${index}">修改</button>
                <button class="btn btn-link btn-sm text-danger p-0 delete-provide-btn" data-option="delete-provide-${index}">刪除</button>
              </div>
            </td>
          </tr>
        `;
      });
      const scheduleCount = schedules.length;
      return `
        <div class="message giver-message">
          <div class="d-flex align-items-center">
            <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
          </div>
          <div class="message-content">
            <p class="message-title">✅ 成功提供時間！您目前已提供 Giver 以下 ${scheduleCount} 個時段，請耐心等待對方確認回覆。</p>
            <div class="table-responsive mt-2">
              <table class="table table-sm table-bordered table-hover success-provide-table">
                <thead class="table-light">
                  <tr>
                    <th class="text-center">序</th>
                    <th class="text-center">狀態</th>
                    <th class="text-center">時段</th>
                    <th class="text-center">備註</th>
                    <th class="text-center">調整</th>
                  </tr>
                </thead>
                <tbody>
                  ${tableRows}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      `;
    },

    // 新增：Giver 已提供時間的複選模板
    giverAvailableTimesWithCheckboxes: () => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
          <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">以下是 Giver 已提供、尚未被預約的日期：</p>
          <div class="chat-checkbox-options mt-2">
            <div class="form-check mb-2">
              <input class="form-check-input" type="checkbox" id="time-option-1" data-option="demo-time-1">
              <label class="form-check-label" for="time-option-1">
                【Demo】預約 2025/07/07（週一）20:00~22:00
              </label>
            </div>
            <div class="form-check mb-2">
              <input class="form-check-input" type="checkbox" id="time-option-2" data-option="demo-time-2">
              <label class="form-check-label" for="time-option-2">
                【Demo】預約 2025/07/08（週二）20:00~22:00
              </label>
            </div>
            <div class="form-check mb-2">
              <input class="form-check-input" type="checkbox" id="time-option-3" data-option="provide-my-time">
              <label class="form-check-label" for="time-option-3">
                可惜 Giver 提供的時間目前我都不方便，讓我提供我方便的時間給 Giver
              </label>
            </div>
            <div class="form-check mb-2">
              <input class="form-check-input" type="checkbox" id="time-option-4" data-option="cancel">
              <label class="form-check-label" for="time-option-4">
                取消本次預約 Giver 時間
              </label>
            </div>
          </div>
          <div class="chat-options-buttons mt-3">
            <button class="btn btn-orange btn-option" id="confirm-selection-btn" disabled>
              確認
            </button>
          </div>
        </div>
      </div>
    `,

    // 新增：提供我的時間選項模板（3個按鈕）
    provideMyTimeOptions: () => `
      <div class="message giver-message">
        <div class="d-flex align-items-center">
          <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
        </div>
        <div class="message-content">
          <p class="message-title">好的！請選擇以下選項，提供您方便的時段：</p>
          <div class="chat-options-buttons mt-2">
            <button class="btn btn-outline btn-option chat-option-btn" data-option="single-time">提供單筆方便時段</button>
            <button class="btn btn-outline btn-option chat-option-btn" data-option="multiple-times">提供多筆方便時段</button>
            <button class="btn btn-outline-secondary btn-option chat-option-btn" data-option="cancel">取消本次預約 Giver 時間</button>
          </div>
        </div>
      </div>
    `,
    
    // 新增：預約成功訊息和表格模板
    reservationSuccessMessageAndTable: (demoTimeOptions, provideMyTimeOption) => {
      console.log('TEMPLATES.chat.reservationSuccessMessageAndTable called', { demoTimeOptions, provideMyTimeOption });
      const totalCount = demoTimeOptions.length + (provideMyTimeOption ? 1 : 0);
      
      // 生成表格行
      let tableRows = '';
      let rowIndex = 1;
      
      // Demo 時間選項
      demoTimeOptions.forEach(option => {
        const timeSlot = option.option === 'demo-time-1' 
          ? '【Demo】預約 2025/07/07（週一）20:00~22:00'
          : '【Demo】預約 2025/07/08（週二）20:00~22:00';
        
        tableRows += `
          <tr>
            <td class="text-center">${rowIndex}</td>
            <td class="text-center text-warning">預約 Giver 時間成功，待 Giver 回覆</td>
            <td class="text-center">${timeSlot}</td>
            <td class="text-center">-</td>
            <td class="text-center">
              <button class="btn btn-sm btn-outline-danger cancel-reservation-btn" data-option="${option.option}">
                取消預約此時段
              </button>
            </td>
          </tr>
        `;
        rowIndex++;
      });
      
      // 提供我的時間選項
      if (provideMyTimeOption) {
        tableRows += `
          <tr>
            <td class="text-center">${rowIndex}</td>
            <td class="text-center text-warning">預約 Giver 時間成功，待 Giver 回覆</td>
            <td class="text-center">提供我方便的時間給 Giver</td>
            <td class="text-center">-</td>
            <td class="text-center">
              <button class="btn btn-sm btn-outline-danger cancel-reservation-btn" data-option="provide-my-time">
                取消此選項
              </button>
            </td>
          </tr>
        `;
      }
      
      return `
        <div class="message giver-message">
          <div class="d-flex align-items-center">
            <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
          </div>
          <div class="message-content">
            <p class="message-title">✅ 預約已送出！<br><br>Giver 已收到您對上述時段的預約通知，請耐心等待對方確認回覆。<br><br>⚠️貼心提醒：<br><br>Giver 可能因臨時狀況無法如期面談，請以對方回覆確認為準，謝謝您的體諒！<br><br>以下是您的預約時段：</p>
            <div class="table-responsive mt-2">
              <table class="table table-sm table-bordered table-hover reservation-success-table">
                <thead class="table-light">
                  <tr>
                    <th class="text-center">序</th>
                    <th class="text-center">狀態</th>
                    <th class="text-center">時段</th>
                    <th class="text-center">備註</th>
                    <th class="text-center">調整</th>
                  </tr>
                </thead>
                <tbody>
                  ${tableRows}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      `;
    },

    // 新增：預約成功表格模板
    reservationSuccessTable: (demoTimeOptions, provideMyTimeOption, isUpdate = false) => {
      console.log('TEMPLATES.chat.reservationSuccessTable called', { demoTimeOptions, provideMyTimeOption, isUpdate });
      const totalCount = demoTimeOptions.length + (provideMyTimeOption ? 1 : 0);
      
      // 根據是否為更新模式選擇訊息
      const messageTitle = isUpdate 
        ? `取消預約成功！您目前已預約 Giver 以下 ${totalCount} 個時段：`
        : `預約成功！您目前已預約 Giver 以下 ${totalCount} 個時段：`;
      
      // 生成表格行
      let tableRows = '';
      let rowIndex = 1;
      
      // Demo 時間選項
      demoTimeOptions.forEach(option => {
        const timeSlot = option.option === 'demo-time-1' 
          ? '【Demo】預約 2025/07/07（週一）20:00~22:00'
          : '【Demo】預約 2025/07/08（週二）20:00~22:00';
        
        tableRows += `
          <tr>
            <td class="text-center">${rowIndex}</td>
            <td class="text-center">${timeSlot}</td>
            <td class="text-center text-success">預約成功</td>
            <td class="text-center">
              <button class="btn btn-sm btn-outline-danger cancel-reservation-btn" data-option="${option.option}">
                取消預約此時段
              </button>
            </td>
          </tr>
        `;
        rowIndex++;
      });
      
      // 提供我的時間選項
      if (provideMyTimeOption) {
        tableRows += `
          <tr>
            <td class="text-center">${rowIndex}</td>
            <td class="text-center">提供我方便的時間給 Giver</td>
            <td class="text-center text-warning">待提供</td>
            <td class="text-center">
              <button class="btn btn-sm btn-outline-danger cancel-reservation-btn" data-option="provide-my-time">
                取消此選項
              </button>
            </td>
          </tr>
        `;
      }
      
      return `
        <div class="message giver-message">
          <div class="d-flex align-items-center">
            <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
          </div>
          <div class="message-content">
            <p class="message-title">${messageTitle}</p>
            <div class="table-responsive mt-2">
              <table class="table table-sm table-bordered table-hover reservation-table">
                <thead class="table-light">
                  <tr>
                    <th class="text-center">序</th>
                    <th class="text-center">時段</th>
                    <th class="text-center">狀態</th>
                    <th class="text-center">調整</th>
                  </tr>
                </thead>
                <tbody>
                  ${tableRows}
                </tbody>
              </table>
            </div>
            <p class="mt-3">請選擇接下來的動作：</p>
            <div class="chat-options-buttons mt-2" id="reservation-success-options">
              <button class="btn btn-orange btn-option" data-option="confirm-all">確認完畢，請協助送出給 Giver</button>
              <button class="btn btn-outline-secondary btn-option" data-option="cancel-all">取消本次預約 Giver 時間</button>
            </div>
          </div>
        </div>
      `;
    },

    // 新增：取消成功訊息和表格模板
    cancelSuccessMessageAndTable: (demoTimeOptions, provideMyTimeOption) => {
      console.log('TEMPLATES.chat.cancelSuccessMessageAndTable called', { demoTimeOptions, provideMyTimeOption });
      const totalCount = demoTimeOptions.length + (provideMyTimeOption ? 1 : 0);
      
      // 生成表格行
      let tableRows = '';
      let rowIndex = 1;
      
      // Demo 時間選項
      demoTimeOptions.forEach(option => {
        const timeSlot = option.option === 'demo-time-1' 
          ? '【Demo】預約 2025/07/07（週一）20:00~22:00'
          : '【Demo】預約 2025/07/08（週二）20:00~22:00';
        
        tableRows += `
          <tr>
            <td class="text-center">${rowIndex}</td>
            <td class="text-center text-warning">預約 Giver 時間成功，待 Giver 回覆</td>
            <td class="text-center">${timeSlot}</td>
            <td class="text-center">-</td>
            <td class="text-center">
              <button class="btn btn-sm btn-outline-danger cancel-reservation-btn" data-option="${option.option}">
                取消預約此時段
              </button>
            </td>
          </tr>
        `;
        rowIndex++;
      });
      
      // 提供我的時間選項
      if (provideMyTimeOption) {
        tableRows += `
          <tr>
            <td class="text-center">${rowIndex}</td>
            <td class="text-center text-warning">預約 Giver 時間成功，待 Giver 回覆</td>
            <td class="text-center">提供我方便的時間給 Giver</td>
            <td class="text-center">-</td>
            <td class="text-center">
              <button class="btn btn-sm btn-outline-danger cancel-reservation-btn" data-option="provide-my-time">
                取消此選項
              </button>
            </td>
          </tr>
        `;
      }
      
      return `
        <div class="message giver-message">
          <div class="d-flex align-items-center">
            <img id="chat-giver-avatar-small" src="/static/chat-avatar.svg" alt="Giver" class="chat-avatar-modal">
          </div>
          <div class="message-content">
            <p class="message-title">取消預約成功！您目前已預約 Giver 以下 ${totalCount} 個時段：</p>
            <div class="table-responsive mt-2">
              <table class="table table-sm table-bordered table-hover reservation-success-table">
                <thead class="table-light">
                  <tr>
                    <th class="text-center">序</th>
                    <th class="text-center">狀態</th>
                    <th class="text-center">時段</th>
                    <th class="text-center">備註</th>
                    <th class="text-center">調整</th>
                  </tr>
                </thead>
                <tbody>
                  ${tableRows}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      `;
    },
  },
};

// =================================================================
//   DOM 元素查詢工具 (DOM Element Query Utilities)
// =================================================================

const DOM = {
  // 基礎查詢方法
  getElement: (selector) => document.querySelector(selector),
  getElements: (selector) => document.querySelectorAll(selector),
  getById: (id) => document.getElementById(id),
  
  // 創建元素
  createElement: (tag, className = '', innerHTML = '') => {
    console.log('DOM.createElement called', { tag, className, innerHTML });
    
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (innerHTML) element.innerHTML = innerHTML;
    
    console.log('元素創建完成:', element);
    return element;
  },
  
  // 元素操作工具
  utils: {
    // 安全地設置文字內容（防止 XSS）
    setTextContent: (element, text) => {
      console.log('DOM.utils.setTextContent called', { element, text });
      if (element) {
        element.textContent = text;
      } else {
        console.error('無法設置文字內容，元素不存在');
      }
    },
    
    // 安全地設置 HTML 內容
    setInnerHTML: (element, html) => {
      console.log('DOM.utils.setInnerHTML called', { element, html });
      if (element) {
        element.innerHTML = html;
      } else {
        console.error('無法設置 HTML 內容，元素不存在');
      }
    },
    
    // 添加事件監聽器
    addEventListener: (element, event, handler, options = {}) => {
      console.log('DOM.utils.addEventListener called', { element, event, handler, options });
      if (element) {
        element.addEventListener(event, handler, options);
      } else {
        console.error('無法添加事件監聽器，元素不存在');
      }
    },
    
    // 移除事件監聽器
    removeEventListener: (element, event, handler, options = {}) => {
      console.log('DOM.utils.removeEventListener called', { element, event, handler, options });
      if (element) {
        element.removeEventListener(event, handler, options);
      } else {
        console.error('無法移除事件監聽器，元素不存在');
      }    
    },
    
    // 顯示元素
    show: (element) => {
      console.log('DOM.utils.show called', { element });
      if (element) {
        element.classList.remove('hidden');
        element.classList.add('visible');
      } else {
        console.error('無法顯示元素，元素不存在');
      }
    },
    
    // 隱藏元素
    hide: (element) => {
      console.log('DOM.utils.hide called', { element });
      if (element) {
        element.classList.remove('visible');
        element.classList.add('hidden');
      } else {
        console.error('無法隱藏元素，元素不存在');
      }
    },
    
    // 切換 CSS 類別
    toggleClass: (element, className) => {
      console.log('DOM.utils.toggleClass called', { element, className });
      if (element) {
        element.classList.toggle(className);
      } else {
        console.error(`[toggleClass] 元素不存在：無法切換 ${className} 類別`);
      }
    },
    
    // 添加 CSS 類別 
    addClass: (element, className) => {
      console.log('DOM.utils.addClass called', { element, className });
      if (element) {
        element.classList.add(className);
      } else {
        console.error(`[addClass] 無法添加 CSS 類別：元素不存在`);
      }
    },
    
    // 移除 CSS 類別
    removeClass: (element, className) => {
      console.log('DOM.utils.removeClass called', { element, className });
      if (element) {
        element.classList.remove(className);
      } else {
        console.error(`[removeClass] 無法移除 CSS 類別：元素不存在`);
      }
    },

    // 檢查橫向滾動是否超出容器
    checkTopicOverflow: (container, chevron) => {
      console.log('DOM.utils.checkTopicOverflow called', { container, chevron });
      if (!container || !chevron) {
        console.error(`[checkTopicOverflow] 無法檢查是否超出範圍：元素不存在`);
        return false;
      }
      const scrollWidth = container.scrollWidth;
      const clientWidth = container.clientWidth;
      return scrollWidth > clientWidth;
    },
    
    // 滾動到底部
    scrollToBottom: (element) => {
      console.log('DOM.utils.scrollToBottom called', { element });
      if (element) {
        element.scrollTo({
          top: element.scrollHeight,
          behavior: 'smooth'
        });
      } else {
        console.error(`[scrollToBottom] 無法滾動到底部：元素不存在`);
      }
    },
    
    // 清理 Modal
    cleanupModal: (modal) => {
      console.log('DOM.utils.cleanupModal called', { modal });
      if (modal) { 
        // 不要清空 modal 內容，只清理狀態
        modal.classList.remove('show');                // 移除 Bootstrap 的顯示 class
        modal.style.display = 'none';                  // 隱藏 modal 元素
        modal.removeAttribute('tabindex');             // 移除 tabindex 屬性
        modal.setAttribute('inert', '');               // 使用 inert 屬性
        
        document.body.classList.remove('modal-open');  // 移除 Bootstrap 的背景滾動鎖定
        document.body.style.paddingRight = '';         // 清除 Bootstrap 動畫期間加的 padding
        
        // 移除 backdrop 元素
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) backdrop.remove();
        
        // 強制處理焦點問題
        if (DOM.chat && DOM.chat.forceFocusToBody) {
          DOM.chat.forceFocusToBody();
        } else {
          // 備用方案
          document.body.focus();
        }
      } else {
        console.error(`[cleanupModal] 無法清理 Modal：元素不存在`);
      }
    }
  },
  
  // 聊天相關元素
  chatElements: {
    input: () => document.getElementById('chat-input-message'),
    sendBtn: () => document.getElementById('chat-send-btn'),
    messages: () => document.getElementById('chat-messages'),
    modal: () => document.getElementById('giver-modal'),
    header: () => document.querySelector('#giver-modal .modal-header'),
    title: () => document.getElementById('chatModalLabel'),
    modalElement: () => document.getElementById('giver-modal')
  },
  
  // 確認對話框相關元素
  confirm: {
    modal: () => document.getElementById('confirm-modal'),
    title: () => document.querySelector('#confirm-modal .modal-title'),
    message: () => document.querySelector('#confirm-modal .modal-body p.text-muted'),
    confirmBtn: () => document.getElementById('continue-btn'),
    cancelBtn: () => document.getElementById('leave-btn')
  },
  
  // Modal 相關元素
  modal: {
    backdrop: () => document.querySelector('.modal-backdrop'),
    giverModal: () => document.getElementById('giver-modal'),
    confirmModal: () => document.getElementById('confirm-modal')
  },
  
  // 服務項目相關元素
  topic: {
    containers: () => document.querySelectorAll('.giverCard__topic'),
    buttons: (container) => container.querySelectorAll('.btn-topic-sm'),
    chevron: (container) => container.querySelector('.fa-chevron-right')
  },
      
  // 聊天訊息建立工具
  message: {
    // 建立基礎訊息結構
    createBaseMessage: (type = 'user') => {
      const messageDiv = DOM.createElement('div', `message ${type}-message`);
      const messageContent = DOM.createElement('div', 'message-content');
      
      console.log('基礎訊息結構創建完成:', { messageDiv, messageContent });
      return { messageDiv, messageContent };
    },
    
    // 建立訊息文字內容
    createTextContent: (text, allowHTML = false) => {
      console.log('DOM.message.createTextContent called', { text, allowHTML });
      const p = DOM.createElement('p', 'mb-1');
      if (allowHTML) {
        p.innerHTML = text;
      } else if (text && text.includes('\n')) {
        const lines = text.split('\n');
        lines.forEach((line, index) => {
          if (index > 0) {
            p.appendChild(document.createElement('br'));
          }
          if (line.trim()) {
            const textNode = document.createTextNode(line);
            p.appendChild(textNode);
          }
        });
      } else {
        DOM.utils.setTextContent(p, text);
      }
      console.log('文字內容創建完成:', p);
      return p;
    },
    
    // 創建時間戳記
    createTimestamp: (timeString) => {
      console.log('DOM.message.createTimestamp called', { timeString });
      
      const timestampDiv = DOM.createElement('div', 'message-time');
      DOM.utils.setTextContent(timestampDiv, timeString);
      
      console.log('DOM.message.createTimestamp: 時間戳記創建完成', timestampDiv);
      return timestampDiv;
    },
    
    // 獲取當前時間字串
    getCurrentTimeString: () => {
      console.log('DOM.message.getCurrentTimeString called');
      const now = DateUtils.getToday();
      return DateUtils.formatToLocalTime(now);
    },
    
    // 建立 Giver 頭像
    createGiverAvatar: () => {
      console.log('DOM.message.createGiverAvatar called');
      
      const avatarContainer = DOM.createElement('div', 'd-flex align-items-center');
      const avatarImg = DOM.createElement('img');
      avatarImg.id = 'chat-giver-avatar-small';
      avatarImg.src = '/static/chat-avatar.svg';
      avatarImg.alt = 'Giver';
      avatarImg.className = 'avatar-modal';
      avatarContainer.appendChild(avatarImg);
      
      console.log('Giver 頭像創建完成:', avatarContainer);
      return avatarContainer;
    },
    
    // 建立完整訊息
    createMessage: (text, type = 'user', allowHTML = false) => {
      console.log('DOM.message.createMessage called', { text, type, allowHTML });
      const { messageDiv, messageContent } = DOM.message.createBaseMessage(type);
      // 添加文字內容
      const textElement = DOM.message.createTextContent(text, allowHTML);
      messageContent.appendChild(textElement);
      // 創建時間戳記
      const timeString = DOM.message.getCurrentTimeString();
      const timestampElement = DOM.message.createTimestamp(timeString);
      console.log('DOM.message.createMessage: 時間戳記創建完成', timestampElement);
      messageContent.appendChild(timestampElement);
      // 如果是 Giver 訊息，添加頭像
      if (type === 'giver') {
        const avatar = DOM.message.createGiverAvatar();
        messageDiv.appendChild(avatar);
      }
      // 組合最終結構
      messageDiv.appendChild(messageContent);
      console.log('DOM.message.createMessage completed', { messageDiv });
      return messageDiv;
    },
    
    // 添加訊息到聊天區域
    addToChat: (messageElement) => {
      const chatMessages = DOM.chatElements.messages();
      if (!chatMessages) {
        console.error('聊天訊息區域未找到');
        return;
      }
      
      console.log('DOM.message.addToChat called', { messageElement });
      chatMessages.appendChild(messageElement);
      
      // 滾動到底部
      DOM.utils.scrollToBottom(chatMessages);
      console.log('DOM.message.addToChat completed');
    },
    
    // 清空聊天區域（保留初始訊息）
    clearChat: () => {
      const chatMessages = DOM.chatElements.messages();
      if (chatMessages) {
        // 清空聊天區域
        chatMessages.innerHTML = '';
        
        // 重新創建初始訊息
        const initialMessageHTML = TEMPLATES.chat.initialMessage();
        
        // 添加初始訊息到聊天區域
        chatMessages.innerHTML = initialMessageHTML;
        
        // 重新設定選項按鈕事件監聽器
        DOM.chat.setupOptionButtons();
        
        console.log('DOM.message.clearChat completed');
      }
    },
    
    // 獲取聊天區域中的所有訊息
    getAllMessages: () => {
      const chatMessages = DOM.chatElements.messages();
      console.log('DOM.message.getAllMessages called', { chatMessages });
      return chatMessages ? Array.from(chatMessages.children) : [];
    },
    
    // 獲取最後一條訊息
    getLastMessage: () => {
      const messages = DOM.message.getAllMessages();
      console.log('DOM.message.getLastMessage called', { messages });
      return messages.length > 0 ? messages[messages.length - 1] : null;
    },
    
    // 檢查訊息是否為特定類型
    isMessageType: (messageElement, type) => {
      console.log('DOM.message.isMessageType called', { messageElement, type });
      return messageElement && messageElement.classList.contains(`${type}-message`);
    },
    
    // 為訊息添加額外的 CSS 類別
    addMessageClass: (messageElement, className) => {
      console.log('DOM.message.addMessageClass called', { messageElement, className });
      if (messageElement) {
        DOM.utils.addClass(messageElement, className);
      }
    },
    
    // 移除訊息的 CSS 類別
    removeMessageClass: (messageElement, className) => {
      console.log('DOM.message.removeMessageClass called', { messageElement, className });
      if (messageElement) {
        DOM.utils.removeClass(messageElement, className);
      }
    }
  },
  
  // 事件監聽器管理工具
  events: {
    // 事件監聽器儲存
    listeners: new Map(),
    
    // 添加事件監聽器（帶管理功能）
    add: (element, event, handler, options = {}) => {
      console.log('DOM.events.add called', { element, event, handler, options });
      if (!element) return;
      
      // 生成唯一的事件識別碼
      const eventId = `${element.id || 'anonymous'}_${event}_${Date.now()}`;
      
      // 儲存事件監聽器資訊
      DOM.events.listeners.set(eventId, {
        element,
        event,
        handler,
        options,
        active: true
      });
      
      // 添加事件監聽器
      element.addEventListener(event, handler, options);
      
      return eventId;
    },
    
    // 移除事件監聽器
    remove: (eventId) => {
      console.log('DOM.events.remove called', { eventId });
      const listenerInfo = DOM.events.listeners.get(eventId);
      if (listenerInfo && listenerInfo.active) {
        listenerInfo.element.removeEventListener(
          listenerInfo.event, 
          listenerInfo.handler, 
          listenerInfo.options
        );
        listenerInfo.active = false;
        DOM.events.listeners.delete(eventId);
      }
    },
    
    // 移除元素的所有事件監聽器
    removeAll: (element) => {
      console.log('DOM.events.removeAll called', { element });
      for (const [eventId, listenerInfo] of DOM.events.listeners) {
        if (listenerInfo.element === element && listenerInfo.active) {
          DOM.events.remove(eventId);
        }
      }
    },
    
    // 移除特定事件類型的所有監聽器
    removeByEvent: (event) => {
      console.log('DOM.events.removeByEvent called', { event });
      for (const [eventId, listenerInfo] of DOM.events.listeners) {
        if (listenerInfo.event === event && listenerInfo.active) {
          DOM.events.remove(eventId);
        }
      }
    },
    
    // 移除特定元素的所有監聽器
    removeByElement: (element) => {
      console.log('DOM.events.removeByElement called', { element });
      for (const [eventId, listenerInfo] of DOM.events.listeners) {
        if (listenerInfo.element === element && listenerInfo.active) {
          DOM.events.remove(eventId);
        }
      }
    },
    
    // 獲取所有活動的事件監聽器
    getAll: () => {
      console.log('DOM.events.getAll called');
      return Array.from(DOM.events.listeners.entries())
        .filter(([_, info]) => info.active)
        .map(([id, info]) => ({ id, ...info }));
    },
    
    // 獲取元素的事件監聽器
    getByElement: (element) => {
      console.log('DOM.events.getByElement called', { element });
      return Array.from(DOM.events.listeners.entries())
        .filter(([_, info]) => info.element === element && info.active)
        .map(([id, info]) => ({ id, ...info }));
    },
    
    // 事件委派工具
    delegate: (parentElement, selector, event, handler, options = {}) => {
      console.log('DOM.events.delegate called', { parentElement, selector, event, handler, options });
      // 委派事件處理器（內部函式）
      const delegatedHandler = (e) => {
        const target = e.target.closest(selector);
        if (target && parentElement.contains(target)) {
          handler.call(target, e, target);
        }
      };
      
      return DOM.events.add(parentElement, event, delegatedHandler, options);
    },
    
    // 一次性事件監聽器
    once: (element, event, handler, options = {}) => {
      console.log('DOM.events.once called', { element, event, handler, options });
      // 一次性事件處理器（內部函式）
      const onceHandler = (e) => {
        handler(e);
        DOM.events.removeByElement(element);
      };
      
      return DOM.events.add(element, event, onceHandler, options);
    },
    
    // 防抖事件監聽器
    debounce: (element, event, handler, delay = 300, options = {}) => {
      console.log('DOM.events.debounce called', { element, event, handler, delay, options });
      let timeoutId;
      
      // 防抖事件處理器（內部函式）
      const debouncedHandler = (e) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => handler(e), delay);
      };
      
      return DOM.events.add(element, event, debouncedHandler, options);
    },
    
    // 節流事件監聽器
    throttle: (element, event, handler, limit = 300, options = {}) => {
      console.log('DOM.events.throttle called', { element, event, handler, limit, options });
      let inThrottle;
      
      // 節流事件處理器（內部函式）
      const throttledHandler = (e) => {
        if (!inThrottle) {
          handler(e);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
      
      return DOM.events.add(element, event, throttledHandler, options);
    },
    
    // 事件監聽器管理工具
    utils: {
      // 獲取事件監聽器統計資訊
      getStats: () => {
        console.log('DOM.events.utils.getStats called');
        const allListeners = DOM.events.getAll();
        const stats = {
          total: allListeners.length,
          byEvent: {},
          byElement: {}
        };
        
        allListeners.forEach(listener => {
          // 按事件類型統計
          stats.byEvent[listener.event] = (stats.byEvent[listener.event] || 0) + 1;
          
          // 按元素統計
          const elementId = listener.element.id || listener.element.tagName || 'anonymous';
          stats.byElement[elementId] = (stats.byElement[elementId] || 0) + 1;
        });
        
        return stats;
      },
      
      // 清理所有事件監聽器
      clearAll: () => {
        console.log('DOM.events.utils.clearAll called');
        const allListeners = DOM.events.getAll();
        allListeners.forEach(listener => {
          DOM.events.remove(listener.id);
        });
      },
      
      // 清理特定元素的所有事件監聽器
      clearElement: (element) => {
        console.log('DOM.events.utils.clearElement called', { element });
        DOM.events.removeAll(element);
      },
      
      // 清理特定事件類型的所有監聽器
      clearEvent: (event) => {
        console.log('DOM.events.utils.clearEvent called', { event });
        DOM.events.removeByEvent(event);
      },
      
      // 檢查元素是否有特定事件類型的監聽器
      hasEvent: (element, event) => {
        console.log('DOM.events.utils.hasEvent called', { element, event });
        const elementListeners = DOM.events.getByElement(element);
        return elementListeners.some(listener => listener.event === event);
      },
      
      // 獲取元素的事件監聽器數量
      getElementCount: (element) => {
        console.log('DOM.events.utils.getElementCount called', { element });
        return DOM.events.getByElement(element).length;
      },
      
      // 獲取特定事件類型的監聽器數量
      getEventCount: (event) => {
        console.log('DOM.events.utils.getEventCount called', { event });
        return DOM.events.getAll().filter(listener => listener.event === event).length;
      },
      
      // 調試：輸出所有事件監聽器資訊
      debug: () => {
        console.log('DOM.events.utils.debug called');
        const allListeners = DOM.events.getAll();
        console.group('事件監聽器調試資訊');
        console.log('總數量:', allListeners.length);
        
        allListeners.forEach(listener => {
          console.log(`- ${listener.id}: ${listener.element.tagName}(${listener.element.id || 'no-id'}) -> ${listener.event}`);
        });
        
        console.groupEnd();
        return allListeners;
      }
    }
  },
  
  // 聊天功能管理工具
  chat: {
    // 聊天狀態管理
    state: {
      currentGiver: null,
      isActive: false,
      messageHistory: [],
      lastMessageTime: null,
      providedSchedules: []
    },
    
    // 聊天初始化
    init: (giver) => {
      console.log('DOM.chat.init called', { giver });
      
      // 使用 ChatStateManager 初始化聊天會話
      ChatStateManager.initChatSession(giver);
      
      // 更新對話框標題
      const modalTitle = DOM.chatElements.title();
      if (!modalTitle) {
        console.error('DOM.chat.init: 聊天對話框標題元素未找到');
        return;
      }
      
      const titleText = `邀請 Giver - ${giver.name || '未知用戶'} 協助諮詢`;
      console.log('DOM.chat.init: 設定對話框標題:', titleText);
      DOM.utils.setTextContent(modalTitle, titleText);
      
      // 重新設定聊天區域的初始狀態
      DOM.message.clearChat();
      
      // 開啟 modal，設定 backdrop 為 static
      const modalElement = DOM.chatElements.modal();
      const modal = new bootstrap.Modal(modalElement, {
        backdrop: 'static',
        keyboard: false
      });
      modal.show();
      
      // 設定聊天功能
      DOM.chat.setup();
    },
    
    // 設定聊天功能
    setup: () => {
      console.log('DOM.chat.setup called');
      // 清理舊的事件監聽器
      DOM.chat.cleanup();
      
      // 重新獲取元素引用
      const chatInput = DOM.chatElements.input();
      const sendBtn = DOM.chatElements.sendBtn();
      
      // 設定 UI 控制項
      DOM.chat.setupUIControls();
      
      // 設定輸入控制項
      DOM.chat.setupInputControls(chatInput, sendBtn);
      
      // 設定模態框事件
      DOM.chat.setupModalEvents();
      
      // 聚焦到輸入框
      chatInput.focus();
    },
    
    // 設定 UI 控制項
    setupUIControls: () => {
      const modalHeader = DOM.chatElements.header();
      if (!modalHeader) {
        console.error('DOM.chat.setupUIControls: 聊天對話框標題區域未找到');
        return;
      }
      
      console.log('DOM.chat.setupUIControls: 設定聊天 UI 控制項');
      
      // 檢查是否已經有關閉按鈕，避免重複添加
      const existingCloseBtn = DOM.getElement('.btn-close-header');
      if (!existingCloseBtn) {
        // 創建關閉按鈕 - 使用 CSS 類別而非內聯樣式
        const closeBtn = DOM.createElement('button', 'btn-close-base btn-close-header', '<i class="fa-solid fa-xmark"></i>');
        
        // 點擊關閉按鈕時顯示確認對話框
        DOM.events.add(closeBtn, 'click', () => {
          console.log('DOM.chat.setupUIControls: 關閉按鈕被點擊');
          DOM.chat.showCloseConfirmation();
        });
        
        // 將關閉按鈕添加到 modal-header 的右側
        modalHeader.appendChild(closeBtn);
        
        console.log('DOM.chat.setupUIControls: 關閉按鈕已添加');
      } else {
        console.log('DOM.chat.setupUIControls: 關閉按鈕已存在，重新綁定事件監聽器');
        // 使用 cloneNode 來移除所有舊的事件監聽器
        const newCloseBtn = existingCloseBtn.cloneNode(true);
        existingCloseBtn.parentNode.replaceChild(newCloseBtn, existingCloseBtn);
        
        // 重新綁定事件監聽器
        DOM.events.add(newCloseBtn, 'click', () => {
          console.log('DOM.chat.setupUIControls: 關閉按鈕被點擊');
          DOM.chat.showCloseConfirmation();
        });
      }
      
      // 設定選項按鈕事件監聽器
      DOM.chat.setupOptionButtons();
    },
    
    // 處理預約時間選項
    handleScheduleOption: () => {
      console.log('DOM.chat.handleScheduleOption called');
      // 顯示 Giver 已提供的時間選項
      setTimeout(() => {
        DOM.chat.showGiverAvailableTimes();
      }, 500);
    },
    
    // 處理暫不預約選項
    handleSkipOption: () => {
      console.log('DOM.chat.handleSkipOption called：處理暫不預約選項');
      
      // 模擬 Giver 回覆
      setTimeout(() => {
        const response = '好的，您選擇暫不預約 Giver 時間。<br><br>如未來有需要預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。<br><br>有其他問題需要協助嗎？';
        DOM.chat.addGiverResponse(response);
      }, 1000);
    },
    
    // 顯示預約選項按鈕
    showScheduleOptions: () => {
      console.log('DOM.chat.showScheduleOptions called：顯示預約選項按鈕');
      
      // 將訊息與按鈕組合在同一個訊息框
      const scheduleOptionsHTML = TEMPLATES.chat.scheduleOptions();
      
      // 插入到聊天區域
      const chatMessages = document.getElementById('chat-messages');
      if (chatMessages) {
        chatMessages.insertAdjacentHTML('beforeend', scheduleOptionsHTML);
        // 綁定事件
        DOM.chat.setupScheduleOptionButtons();
        // 滾動到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    },
    
    // 顯示 Giver 已提供的時間選項
    showGiverAvailableTimes: () => {
      console.log('DOM.chat.showGiverAvailableTimes called：顯示 Giver 已提供的時間選項');
      
      // 將訊息與複選選項組合在同一個訊息框
      const giverAvailableTimesHTML = TEMPLATES.chat.giverAvailableTimesWithCheckboxes();
      
      // 插入到聊天區域
      const chatMessages = document.getElementById('chat-messages');
      if (chatMessages) {
        chatMessages.insertAdjacentHTML('beforeend', giverAvailableTimesHTML);
        // 綁定複選選項事件
        DOM.chat.setupCheckboxOptions();
        // 滾動到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    },

    // 顯示提供我的時間選項（3個按鈕）
    showProvideMyTimeOptions: () => {
      console.log('DOM.chat.showProvideMyTimeOptions called：顯示提供我的時間選項');
      
      // 將訊息與按鈕組合在同一個訊息框
      const provideMyTimeOptionsHTML = TEMPLATES.chat.provideMyTimeOptions();
      
      // 插入到聊天區域
      const chatMessages = document.getElementById('chat-messages');
      if (chatMessages) {
        chatMessages.insertAdjacentHTML('beforeend', provideMyTimeOptionsHTML);
        // 綁定事件
        DOM.chat.setupScheduleOptionButtons();
        // 滾動到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    },
    
    // 設定聊天輸入區域的額外功能按鈕事件監聽器
    setupChatExtraButtons: () => {
      console.log('DOM.chat.setupChatExtraButtons called：設定聊天輸入區域的額外功能按鈕');
      const extraButtons = document.querySelectorAll('.chat-extra-buttons .btn[data-option]');
      
      extraButtons.forEach(button => {
        // 先移除舊的事件監聽器，避免重複綁定
        const newBtn = button.cloneNode(true);
        button.parentNode.replaceChild(newBtn, button);
        
        // 重新綁定事件監聽器
        DOM.events.add(newBtn, 'click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          
          const option = newBtn.getAttribute('data-option');
          const optionText = newBtn.textContent.trim();
          console.log('聊天額外功能按鈕被點擊:', { option, optionText });
          
          // 添加使用者選擇的訊息
          DOM.chat.addUserMessage(optionText);
          
          // 處理不同的選項
          switch (option) {
            case 'view-giver-times':
              DOM.chat.handleViewTimes();
              break;
            case 'provide-single-time':
              DOM.chat.handleSingleTime();
              break;
            case 'provide-multiple-times':
              DOM.chat.handleMultipleTimes();
              break;
            case 'view-my-times':
              DOM.chat.handleViewAllSchedules();
              break;
            default:
              console.warn('未知的聊天額外功能選項:', option);
          }
        });
      });
    },

    // 設定預約選項按鈕事件監聽器
    setupScheduleOptionButtons: () => {
      console.log('DOM.chat.setupScheduleOptionButtons called：設定預約選項按鈕');
      const scheduleOptionButtons = document.querySelectorAll('.chat-option-btn[data-option]');
      
      scheduleOptionButtons.forEach(button => {
        const newBtn = button.cloneNode(true);
        button.parentNode.replaceChild(newBtn, button);
        
        // 再綁定新的事件監聽器
        DOM.events.add(newBtn, 'click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          
          const option = newBtn.getAttribute('data-option');
          const optionText = newBtn.textContent.trim();
          console.log('預約選項按鈕被點擊:', { option, optionText });
          
          // 添加使用者選擇的訊息
          DOM.chat.addUserMessage(optionText);
          
          // 處理不同的選項
          switch (option) {
            case 'view-times':
              DOM.chat.handleViewTimes();
              break;
            case 'single-time':
              DOM.chat.handleSingleTime();
              break;
            case 'multiple-times':
              DOM.chat.handleMultipleTimes();
              break;
            case 'view-all':
              DOM.chat.handleViewAllSchedules();
              break;
            case 'cancel':
              DOM.chat.handleCancelSchedule();
              break;
            default:
              console.warn('未知的預約選項:', option);
          }
          
          // 隱藏選項按鈕
          const optionsContainer = newBtn.closest('.chat-options-buttons');
          if (optionsContainer) {
            optionsContainer.classList.remove('container-visible');
            optionsContainer.classList.add('chat-options-hidden');
          }
        });
      });
    },
    
    // 設定複選選項事件監聽器
    setupCheckboxOptions: () => {
      console.log('DOM.chat.setupCheckboxOptions called：設定複選選項');
      
      const checkboxes = document.querySelectorAll('.chat-checkbox-options input[type="checkbox"]');
      const confirmBtn = document.getElementById('confirm-selection-btn');
      
      // 為每個複選框添加事件監聽器
      checkboxes.forEach(checkbox => {
        DOM.events.add(checkbox, 'change', (e) => {
          console.log('複選框狀態改變:', { 
            id: checkbox.id, 
            option: checkbox.getAttribute('data-option'), 
            checked: checkbox.checked 
          });
          
          // 處理互斥選擇邏輯
          DOM.chat.handleMutualExclusion(checkbox);
          
          // 更新確認按鈕狀態
          DOM.chat.updateConfirmButtonState();
        });
      });
      
      // 為確認按鈕添加事件監聽器
      if (confirmBtn) {
        DOM.events.add(confirmBtn, 'click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          
          console.log('確認選擇按鈕被點擊');
          
          // 獲取選中的選項
          const selectedOptions = DOM.chat.getSelectedCheckboxOptions();
          console.log('選中的選項:', selectedOptions);
          
          // 處理選中的選項
          DOM.chat.handleSelectedOptions(selectedOptions);
          
          // 隱藏選項區域
          const optionsContainer = confirmBtn.closest('.message');
          if (optionsContainer) {
            optionsContainer.style.display = 'none';
          }
        });
      }
    },

    // 設定預約成功表格按鈕事件監聽器
    setupReservationTableButtons: () => {
      console.log('DOM.chat.setupReservationTableButtons called：設定預約成功表格按鈕');
      
      // 綁定取消預約時段按鈕
      const cancelReservationBtns = document.querySelectorAll('.cancel-reservation-btn');
      cancelReservationBtns.forEach(btn => {
        DOM.events.add(btn, 'click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          
          const option = btn.getAttribute('data-option');
          console.log('取消預約時段按鈕被點擊:', { option });
          
          // 處理取消預約時段
          DOM.chat.handleCancelReservationTime(option, btn);
        });
      });
      
      // 綁定確認完畢和取消全部按鈕
      const confirmAllBtn = document.querySelector('[data-option="confirm-all"]');
      const cancelAllBtn = document.querySelector('[data-option="cancel-all"]');
      
      if (confirmAllBtn) {
        DOM.events.add(confirmAllBtn, 'click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          
          console.log('確認完畢按鈕被點擊');
          DOM.chat.handleConfirmAllReservations();
        });
      }
      
      if (cancelAllBtn) {
        DOM.events.add(cancelAllBtn, 'click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          
          console.log('取消全部預約按鈕被點擊');
          DOM.chat.handleCancelAllReservations();
        });
      }
    },

    // 取消預約時段
    handleCancelReservationTime: (option, button) => {
      console.log('DOM.chat.handleCancelReservationTime called：取消預約時段', { option });
      
      // 獲取時段名稱：根據 option 的值，設定 timeSlot 的值
      let timeSlot = '';
      if (option === 'demo-time-1') {
        timeSlot = '【Demo】預約 2025/07/07（週一）20:00~22:00';
      } else if (option === 'demo-time-2') {
        timeSlot = '【Demo】預約 2025/07/08（週二）20:00~22:00';
      } else if (option === 'provide-my-time') {
        timeSlot = '提供我方便的時間給 Giver';
      }
      
      // 跳出確認 modal：使用 UIComponents.confirmDialog 函式，顯示一個確認對話框，讓使用者可以確認是否取消預約。
      UIComponents.confirmDialog({
        title: '確認取消預約',
        message: `確定取消預約此時段嗎？${timeSlot}`,
        confirmText: '取消預約',
        cancelText: '保留',
        onConfirm: () => {
          // 使用者確認取消預約
          console.log('使用者確認取消預約:', timeSlot);
          
          // 添加使用者訊息
          DOM.chat.addUserMessage(`我要取消：${timeSlot}`);
                    
          // 從 DOM 移除該行
          const tableRow = button.closest('tr');
          if (tableRow) {
            tableRow.remove();
          }

          // 檢查是否還有其他預約
          setTimeout(() => {
            // 直接獲取現存的所有預約行（因為已取消的行已被移除）
            const allRows = document.querySelectorAll('.reservation-success-table tbody tr, .reservation-table tbody tr');
            
            console.log('檢查剩餘預約時段:', {
              totalRows: allRows.length
            });

            if (allRows.length === 0) {
              // 如果沒有其他預約，顯示取消訊息
              DOM.chat.addGiverResponse('您已取消所有預約時段。<br><br>如果仍想預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。');
            } else {
              // 如果還有其他預約，直接使用現存的行
              DOM.chat.addCancelSuccessMessage(allRows);
            }
          }, 500);          
        },
        onCancel: () => {
          // 使用者選擇保留，不做任何動作
          console.log('使用者選擇保留預約:', timeSlot);
        }
      });
    },

    // 在聊天對話框最下方新增一個新的訊息泡泡，顯示取消成功和剩餘的預約時段
    addCancelSuccessMessage: (visibleRows) => {
      console.log('DOM.chat.addCancelSuccessMessage called：新增取消成功訊息泡泡');
      
      // 分析剩餘的預約選項（直接使用現存的行，因為已取消的行已被移除）
      const remainingOptions = [];
      visibleRows.forEach(row => {
        const cancelBtn = row.querySelector('.cancel-reservation-btn');
        if (cancelBtn) {
          const option = cancelBtn.getAttribute('data-option');
          // 從正確的欄位獲取時段資訊
          const timeSlotCell = row.querySelector('td:nth-child(3)'); // 時段欄位
          const timeSlot = timeSlotCell ? timeSlotCell.textContent.trim() : '';
          
          if (option && timeSlot) {
            remainingOptions.push({ option, label: timeSlot });
          }
        }
      });
      
      // 分類剩餘選項
      const demoTimeOptions = remainingOptions.filter(option => 
        option.option === 'demo-time-1' || option.option === 'demo-time-2'
      );
      console.log('demoTimeOptions:', demoTimeOptions);
      const provideMyTimeOption = remainingOptions.find(option => 
        option.option === 'provide-my-time'
      );
      console.log('provideMyTimeOption:', provideMyTimeOption);
      console.log('remainingOptions:', remainingOptions);
      // 檢查是否還有剩餘時段
      const totalCount = demoTimeOptions.length + (provideMyTimeOption ? 1 : 0);
      console.log('totalCount:', totalCount);

      if (totalCount === 0) {
        // 如果沒有剩餘時段，不生成任何訊息泡泡
        console.log('沒有剩餘時段，顯示取消所有預約時段訊息');
        DOM.chat.addGiverResponse('您已取消所有預約時段。<br><br>如果仍想預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。');
        return;
      }
      
      // 生成取消成功訊息泡泡 HTML
      const cancelSuccessHTML = TEMPLATES.chat.cancelSuccessMessageAndTable(demoTimeOptions, provideMyTimeOption);
      
      // 在聊天對話框最下方插入新的訊息泡泡
      const chatMessages = document.getElementById('chat-messages');
      if (chatMessages) {
        chatMessages.insertAdjacentHTML('beforeend', cancelSuccessHTML);
        // 綁定新的表格按鈕事件
        DOM.chat.setupReservationTableButtons();
        // 滾動到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    },

    // 處理確認完畢所有預約
    handleConfirmAllReservations: () => {
      console.log('DOM.chat.handleConfirmAllReservations called：處理確認完畢所有預約');
      
      DOM.chat.addUserMessage('確認完畢，請協助送出給 Giver');
      
      setTimeout(() => {
        const response = '✅ 預約已送出！<br><br>Giver 已收到您對上述時段的預約通知，請耐心等待對方確認回覆。<br><br>⚠️ 貼心提醒：<br><br>Giver 可能因臨時狀況無法如期面談，請以對方回覆確認為準，謝謝您的體諒！<br><br>以下是您的預約時段：';
        DOM.chat.addGiverResponse(response);
      }, 1000);
    },

    // 處理取消全部預約
    handleCancelAllReservations: () => {
      console.log('DOM.chat.handleCancelAllReservations called：處理取消全部預約');
      
      DOM.chat.handleCancelSchedule();
    },

    // 更新預約表格
    updateReservationTable: (visibleRows) => {
      console.log('DOM.chat.updateReservationTable called：更新預約表格', { visibleRowsCount: visibleRows.length });
      
      // 分析剩餘的預約選項
      const remainingOptions = [];
      visibleRows.forEach(row => {
        const cancelBtn = row.querySelector('.cancel-reservation-btn');
        if (cancelBtn) {
          const option = cancelBtn.getAttribute('data-option');
          const timeSlotCell = row.querySelector('td:nth-child(2)');
          const timeSlot = timeSlotCell ? timeSlotCell.textContent.trim() : '';
          
          if (option && timeSlot) {
            remainingOptions.push({ option, label: timeSlot });
          }
        }
      });
      
      // 分類剩餘選項
      const demoTimeOptions = remainingOptions.filter(option => 
        option.option === 'demo-time-1' || option.option === 'demo-time-2'
      );
      const provideMyTimeOption = remainingOptions.find(option => 
        option.option === 'provide-my-time'
      );
      
      // 生成更新後的表格 HTML
      const updatedTableHTML = TEMPLATES.chat.reservationSuccessTable(demoTimeOptions, provideMyTimeOption, true);
      
      // 移除舊的表格訊息
      const oldTableMessage = document.querySelector('.reservation-table').closest('.message');
      if (oldTableMessage) {
        oldTableMessage.remove();
      }
      
      // 在聊天對話框最下方插入新的表格
      const chatMessages = document.getElementById('chat-messages');
      if (chatMessages) {
        chatMessages.insertAdjacentHTML('beforeend', updatedTableHTML);
        // 綁定新的表格按鈕事件
        DOM.chat.setupReservationTableButtons();
        // 滾動到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    },

    // 更新確認按鈕狀態
    updateConfirmButtonState: () => {
      const checkboxes = document.querySelectorAll('.chat-checkbox-options input[type="checkbox"]:not(:disabled)');
      const confirmBtn = document.getElementById('confirm-selection-btn');
      
      if (confirmBtn) {
        const hasSelection = Array.from(checkboxes).some(checkbox => checkbox.checked);
        confirmBtn.disabled = !hasSelection;
        
        if (hasSelection) {
          confirmBtn.classList.remove('btn-secondary');
          confirmBtn.classList.add('btn-orange');
        } else {
          confirmBtn.classList.remove('btn-orange');
          confirmBtn.classList.add('btn-secondary');
        }
      }
    },

    // 獲取選中的複選框選項
    getSelectedCheckboxOptions: () => {
      const checkboxes = document.querySelectorAll('.chat-checkbox-options input[type="checkbox"]:checked:not(:disabled)');
      const selectedOptions = [];
      
      checkboxes.forEach(checkbox => {
        const option = checkbox.getAttribute('data-option');
        const label = checkbox.nextElementSibling.textContent.trim();
        selectedOptions.push({ option, label });
      });
      
      return selectedOptions;
    },

    // 處理選中的選項
    handleSelectedOptions: (selectedOptions) => {
      console.log('DOM.chat.handleSelectedOptions called：處理選中的選項', selectedOptions);
      
      // 添加使用者選擇的訊息
      const selectedText = selectedOptions.map(option => option.label).join('、');
      DOM.chat.addUserMessage(`選擇時段：${selectedText}`);
      
      // 分類選中的選項
      const demoTimeOptions = selectedOptions.filter(option => 
        option.option === 'demo-time-1' || option.option === 'demo-time-2'
      );
      const provideMyTimeOption = selectedOptions.find(option => 
        option.option === 'provide-my-time'
      );
      const cancelOption = selectedOptions.find(option => 
        option.option === 'cancel'
      );
      
      // 如果有取消選項，優先處理
      if (cancelOption) {
        DOM.chat.handleCancelSchedule();
        return;
      }
      
      // 如果有 Demo 時間選項，顯示預約成功表格
      if (demoTimeOptions.length > 0) {
        DOM.chat.handleMultipleDemoTimeSelection(demoTimeOptions, provideMyTimeOption);
        return;
      }
      
      // 如果只有提供我的時間選項
      if (provideMyTimeOption) {
        DOM.chat.handleProvideMyTime();
        return;
      }
      
      // 處理其他未知選項
      selectedOptions.forEach(selectedOption => {
        console.warn('未知的選項:', selectedOption.option);
      });
    },

    // 處理 Demo 時間選擇
    handleDemoTimeSelection: (timeSlot) => {
      console.log('DOM.chat.handleDemoTimeSelection called：處理 Demo 時間選擇', timeSlot);
      setTimeout(() => {
        const response = `您已成功預約 ${timeSlot}。<br><br>Giver 將在 24 小時內確認您的預約，請留意通知。<br><br>有其他問題需要協助嗎？`;
        DOM.chat.addGiverResponse(response);
      }, 1000);
    },

    // 處理提供我的時間選項
    handleProvideMyTime: () => {
      console.log('DOM.chat.handleProvideMyTime called：處理提供我的時間選項');
      setTimeout(() => {
        // 顯示提供我的時間選項（3個按鈕）
        DOM.chat.showProvideMyTimeOptions();
      }, 1000);
    },
    
    // 處理多個 Demo 時間選項
    handleMultipleDemoTimeSelection: (demoTimeOptions, provideMyTimeOption) => {
      console.log('DOM.chat.handleMultipleDemoTimeSelection called：處理多個 Demo 時間選項', { demoTimeOptions, provideMyTimeOption });
      
      setTimeout(() => {
        // 顯示預約成功訊息和表格
        const reservationSuccessHTML = TEMPLATES.chat.reservationSuccessMessageAndTable(demoTimeOptions, provideMyTimeOption);
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
          chatMessages.insertAdjacentHTML('beforeend', reservationSuccessHTML);
          // 綁定表格按鈕事件
          DOM.chat.setupReservationTableButtons();
          // 滾動到底部
          chatMessages.scrollTop = chatMessages.scrollHeight;
        }
      }, 1000);
    },
    
    // 處理查看時間選項
    handleViewTimes: () => {
      console.log('DOM.chat.handleViewTimes called：處理查看時間選項');
      setTimeout(() => {
        // 使用新的模板顯示「Giver 尚末提供提供方便的時間」訊息和按鈕
        const noGiverTimesHTML = TEMPLATES.chat.noGiverTimesWithButtons();
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
          chatMessages.insertAdjacentHTML('beforeend', noGiverTimesHTML);
          // 綁定按鈕事件
          DOM.chat.setupScheduleOptionButtons();
          // 滾動到底部
          chatMessages.scrollTop = chatMessages.scrollHeight;
        }
      }, 1000);
    },
    
    // 處理單筆時段選項
    handleSingleTime: (editIndex = null, editData = null) => {
      console.log('DOM.chat.handleSingleTime called：處理單筆時段選項', { editIndex, editData });
      setTimeout(() => {
        // 顯示表單
        let scheduleForm = document.getElementById('schedule-form');
        if (!scheduleForm) {
          // 動態創建
          const chatMessages = document.getElementById('chat-messages');
          if (chatMessages) {
            const formHTML = TEMPLATES.chat.scheduleForm();
            chatMessages.insertAdjacentHTML('beforeend', formHTML);
            scheduleForm = document.getElementById('schedule-form');
          }
        }
        if (scheduleForm) {
          // 將表單移動到聊天記錄的最下方
          const chatMessages = document.getElementById('chat-messages');
          if (chatMessages) {
            chatMessages.appendChild(scheduleForm);
          }
          // 初始化表單欄位事件（日期欄位可點擊彈出日曆 modal）
          const formElement = document.getElementById('time-schedule-form');
          if (formElement) {
            initScheduleFormInputs(formElement);
          }
          scheduleForm.classList.remove('schedule-form-hidden');
          scheduleForm.classList.add('schedule-form-visible');
          // 帶入編輯資料
          const startTimeInput = document.getElementById('schedule-start-time');
          const endTimeInput = document.getElementById('schedule-end-time');
          const dateInput = document.getElementById('schedule-date');
          const notesInput = document.getElementById('schedule-notes');
          if (editData) {
            if (dateInput) dateInput.value = editData.date;
            if (startTimeInput) startTimeInput.value = editData.startTime;
            if (endTimeInput) endTimeInput.value = editData.endTime;
            if (notesInput) notesInput.value = editData.notes || '';
          } else {
            if (startTimeInput) startTimeInput.value = '20:00';
            if (endTimeInput) endTimeInput.value = '22:00';
            if (dateInput) dateInput.value = DateUtils.formatDate(DateUtils.getToday());
            if (notesInput) notesInput.value = '';
          }
          // 設定表單事件
          DOM.chat.setupScheduleForm(editIndex);
          // 滾動到底部
          if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
        }
      }, 100);
    },
    
    // 設定表單事件
    setupScheduleForm: (editIndex = null) => {
      console.log('DOM.chat.setupScheduleForm called: 設定表單事件');
      const form = document.getElementById('time-schedule-form');
      if (form) {
        form.onsubmit = (e) => {
          console.log('DOM.chat.setupScheduleForm: 表單提交事件觸發');
          e.preventDefault();
          const dateInput = document.getElementById('schedule-date');
          const startTimeInput = document.getElementById('schedule-start-time');
          const endTimeInput = document.getElementById('schedule-end-time');
          const notesInput = document.getElementById('schedule-notes');
          const formData = {
            date: dateInput?.value || '',
            startTime: startTimeInput?.value || '',
            endTime: endTimeInput?.value || '',
            notes: notesInput?.value || ''
          };
          console.log('DOM.chat.setupScheduleForm: 表單資料', formData);
          const validationResult = FormValidator.validateScheduleForm(formData);
          if (!validationResult.isValid) {
            console.warn('DOM.chat.setupScheduleForm: 表單驗證失敗', validationResult);
            FormValidator.showValidationError(validationResult.message, form);
            return;
          }
          // 檢查重複時段
          const existingSchedules = ChatStateManager.getProvidedSchedules();
          const isDuplicate = existingSchedules.some((schedule, index) => {
            // 編輯模式時排除當前正在編輯的時段
            if (editIndex !== null && index === editIndex) {
              return false;
            }
            
            // 檢查是否為完全相同的時段
            const isExactDuplicate = schedule.date === formData.date && 
              schedule.startTime === formData.startTime && 
              schedule.endTime === formData.endTime;
            
            if (isExactDuplicate) {
              return true;
            }
            
            // 檢查是否為重疊時段（相同日期且時間有重疊）
            if (schedule.date === formData.date) {
              const existingStart = schedule.startTime;
              const existingEnd = schedule.endTime;
              const newStart = formData.startTime;
              const newEnd = formData.endTime;
              
              // 檢查時間重疊：新時段的開始時間 < 現有時段的結束時間 且 新時段的結束時間 > 現有時段的開始時間
              const isOverlapping = newStart < existingEnd && newEnd > existingStart;
              
              return isOverlapping;
            }
            
            return false;
          });
          
          if (isDuplicate) {
            console.warn('DOM.chat.setupScheduleForm: 檢測到重複或重疊時段', formData);
            const duplicateMessage = FormValidator.generateDuplicateScheduleMessage(formData, existingSchedules);
            FormValidator.showValidationError(duplicateMessage);
            return;
          }
          // 編輯模式：覆蓋原本那一筆
          if (editIndex !== null && editIndex !== undefined) {
            console.log('DOM.chat.setupScheduleForm: 編輯模式，覆蓋原本的時段');
            const schedules = ChatStateManager.getProvidedSchedules();
            schedules[editIndex] = { ...schedules[editIndex], ...formData };
            ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES, schedules);
            // 移除表單
            const scheduleForm = document.getElementById('schedule-form');
            if (scheduleForm) {
              scheduleForm.classList.remove('schedule-form-visible');
              scheduleForm.classList.add('schedule-form-hidden');
            }
            
            // 直接更新原本的成功提供時間泡泡，而不是創建新的泡泡
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
              // 找到原本的成功提供時間泡泡（如果存在）
              const successMessage = chatMessages.querySelector('.success-provide-table')?.closest('.giver-message');
              if (successMessage) {
                const updatedHTML = TEMPLATES.chat.successProvideTime(schedules);
                successMessage.outerHTML = updatedHTML;
                // 重新綁定修改和刪除按鈕事件
                const newEditButtons = chatMessages.querySelectorAll('.success-provide-table .edit-provide-btn');
                newEditButtons.forEach(btn => {
                  btn.addEventListener('click', function() {
                    const tr = btn.closest('tr');
                    const idx = parseInt(tr.getAttribute('data-index'));
                    const schedule = schedules[idx];
                    DOM.chat.handleSingleTime(idx, schedule);
                  });
                });
                const newDeleteButtons = chatMessages.querySelectorAll('.success-provide-table .delete-provide-btn');
                newDeleteButtons.forEach(btn => {
                  btn.addEventListener('click', function() {
                    const tr = btn.closest('tr');
                    const idx = parseInt(tr.getAttribute('data-index'));
                    UIComponents.confirmDialog({
                      title: '取消提供時間',
                      message: '確定要取消提供此時間嗎？',
                      confirmText: '取消提供',
                      cancelText: '保留',
                      onConfirm: () => {
                        let newSchedules = ChatStateManager.getProvidedSchedules();
                        newSchedules.splice(idx, 1);
                        ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES, newSchedules);
                        if (newSchedules.length === 0) {
                          DOM.chat.addGiverResponse('已取消所有提供時間。<br><br>如未來有需要預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。<br><br>有其他問題需要協助嗎？');
                        } else {
                          const newUpdatedHTML = TEMPLATES.chat.successProvideTime(newSchedules);
                          const newCurrentMessage = chatMessages.querySelector('.success-provide-table')?.closest('.giver-message');
                          if (newCurrentMessage) {
                            newCurrentMessage.outerHTML = newUpdatedHTML;
                          }
                        }
                      }
                    });
                  });
                });
              }
              
              // 同步更新「查看所有我已提供的時段」泡泡（如果存在）
              const scheduleTableMessage = chatMessages.querySelector('.schedule-table')?.closest('.giver-message');
              console.log('DOM.chat.setupScheduleForm: 尋找 schedule-table 泡泡', { scheduleTableMessage });
              if (scheduleTableMessage) {
                console.log('DOM.chat.setupScheduleForm: 找到 schedule-table 泡泡，準備更新');
                const updatedTableHTML = TEMPLATES.chat.scheduleTable(schedules);
                scheduleTableMessage.outerHTML = updatedTableHTML;
                console.log('DOM.chat.setupScheduleForm: schedule-table 泡泡已更新');
                // 重新綁定表格內按鈕事件
                const table = chatMessages.querySelector('.schedule-table');
                if (table) {
                  console.log('DOM.chat.setupScheduleForm: 找到更新後的表格，重新綁定事件');
                  table.querySelectorAll('.schedule-edit-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                      const tr = btn.closest('tr');
                      const idx = parseInt(tr.getAttribute('data-index'));
                      const schedule = schedules[idx];
                      DOM.chat.handleSingleTime(idx, schedule);
                    });
                  });
                  table.querySelectorAll('.schedule-delete-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                      const tr = btn.closest('tr');
                      const idx = parseInt(tr.getAttribute('data-index'));
                      UIComponents.confirmDialog({
                        title: '刪除時段',
                        message: '確定要刪除此時段嗎？',
                        confirmText: '刪除',
                        cancelText: '取消',
                        onConfirm: () => {
                          let newSchedules = ChatStateManager.getProvidedSchedules();
                          newSchedules.splice(idx, 1);
                          ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES, newSchedules);
                          if (newSchedules.length === 0) {
                            DOM.chat.addGiverResponse('已取消所有提供時間。<br><br>如未來有需要預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。<br><br>有其他問題需要協助嗎？');
                          } else {
                            const newUpdatedHTML = TEMPLATES.chat.scheduleTable(newSchedules);
                            const newCurrentMessage = chatMessages.querySelector('.schedule-table')?.closest('.giver-message');
                            if (newCurrentMessage) {
                              newCurrentMessage.outerHTML = newUpdatedHTML;
                            }
                          }
                        }
                      });
                    });
                  });
                }
                // 綁定下方動作按鈕
                const afterBtns = chatMessages.querySelectorAll('#after-view-all-options .btn-option');
                afterBtns.forEach(btn => {
                  btn.addEventListener('click', (e) => {
                    const option = btn.getAttribute('data-option');
                    if (option === 'single-time') {
                      DOM.chat.handleSingleTime();
                    } else if (option === 'multiple-times') {
                      DOM.chat.handleMultipleTimes();
                    } else if (option === 'finish') {
                      DOM.chat.addUserMessage('已新增完成所有時段，請協助送出給 Giver');
                      setTimeout(() => {
                        DOM.chat.handleSuccessProvideTime();
                      }, 1000);
                    } else if (option === 'cancel') {
                      DOM.chat.handleCancelSchedule();
                    }
                    const optionsContainer = btn.closest('.chat-options-buttons');
                    if (optionsContainer) {
                      optionsContainer.classList.remove('container-visible');
                      optionsContainer.classList.add('chat-options-hidden');
                    }
                  });
                });
              } else {
                console.log('DOM.chat.setupScheduleForm: 未找到 schedule-table 泡泡');
              }
              
              // 滾動到底部
              chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            return;
          }
          // 新增模式
          const formattedSchedule = `${formData.date} ${formData.startTime}~${formData.endTime}`;
          ChatStateManager.addSchedule({
            date: formData.date,
            startTime: formData.startTime,
            endTime: formData.endTime,
            notes: formData.notes.trim(),
            formattedSchedule: formattedSchedule
          });
          // 隱藏表單
          const scheduleForm = document.getElementById('schedule-form');
          if (scheduleForm) {
            scheduleForm.classList.remove('schedule-form-visible');
            scheduleForm.classList.add('schedule-form-hidden');
          }
          // 清空表單
          if (dateInput) dateInput.value = '';
          if (startTimeInput) startTimeInput.value = '20:00';
          if (endTimeInput) endTimeInput.value = '22:00';
          if (notesInput) notesInput.value = '';
          // 重置選中的日期
          DOM.chat.setSelectedDate(null);
          // 模擬 Giver 回覆
          setTimeout(() => {
            const responseHTML = TEMPLATES.chat.afterScheduleOptions(formData.date + ' ' + formData.startTime + '~' + formData.endTime, formData.notes);
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
              chatMessages.insertAdjacentHTML('beforeend', responseHTML);
              // 綁定按鈕事件
              const afterBtns = chatMessages.querySelectorAll('#after-schedule-options .btn-option');
              afterBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                  const option = btn.getAttribute('data-option');
                  const optionText = btn.textContent.trim();
                  console.log('after-schedule-options 按鈕被點擊:', { option, optionText });
                  // 處理不同選項
                  if (option === 'single-time') {
                    DOM.chat.handleSingleTime();
                  } else if (option === 'multiple-times') {
                    DOM.chat.handleMultipleTimes();
                  } else if (option === 'view-all') {
                    DOM.chat.handleViewAllSchedules();
                  } else if (option === 'finish') {
                    DOM.chat.addUserMessage('已新增完成所有時段，請協助送出給 Giver');
                    setTimeout(() => {
                      DOM.chat.handleSuccessProvideTime();
                    }, 1000);
                  } else if (option === 'cancel') {
                    DOM.chat.handleCancelSchedule();
                  }
                  // 點擊後隱藏按鈕區塊
                  const optionsContainer = btn.closest('.chat-options-buttons');
                  if (optionsContainer) {
                    optionsContainer.classList.remove('container-visible');
                    optionsContainer.classList.add('chat-options-hidden');
                  }
                });
              });
              chatMessages.scrollTop = chatMessages.scrollHeight;
            }
          }, 500);
        };
      }
    },
    
    // 顯示日期選擇器
    showDatePicker: () => {
      console.log('DOM.chat.showDatePicker called：顯示日期選擇器');
      
      // 初始化日期選擇器
      DOM.chat.initDatePicker();
      
      // 查找 Modal 元素
      const datePickerModalElement = document.getElementById('date-picker-modal');
      console.log('DOM.chat.showDatePicker: 查找日期選擇器 Modal', { datePickerModalElement });
      
      if (datePickerModalElement) {
        try {
          // 顯示 Modal
          const datePickerModal = new bootstrap.Modal(datePickerModalElement);
          console.log('DOM.chat.showDatePicker: 創建 Bootstrap Modal 實例', { datePickerModal });
          
          datePickerModal.show();
          console.log('DOM.chat.showDatePicker: Modal 顯示指令已執行');
          
          // 添加顯示完成的事件監聽器
          DOM.events.add(datePickerModalElement, 'shown.bs.modal', () => {
            console.log('DOM.chat.showDatePicker: Modal 已完全顯示');
          });
          
        } catch (error) {
          console.error('DOM.chat.showDatePicker: 顯示 Modal 時發生錯誤', error);
          
          // 備案：直接設定 Modal 為顯示狀態
          datePickerModalElement.classList.add('show');
          datePickerModalElement.style.display = 'block';
          document.body.classList.add('modal-open');
          
          // 添加 backdrop
          const backdrop = document.createElement('div');
          backdrop.className = 'modal-backdrop fade show';
          document.body.appendChild(backdrop);
          
          console.log('DOM.chat.showDatePicker: 使用備案方式顯示 Modal');
        }
      } else {
        console.error('DOM.chat.showDatePicker: 找不到日期選擇器 Modal 元素');
      }
    },
    
    // 初始化日期選擇器
    initDatePicker: () => {
      console.log('DOM.chat.initDatePicker called：初始化日期選擇器');
      const currentDate = new Date();
      let currentMonth = currentDate.getMonth();
      let currentYear = currentDate.getFullYear();
      
      // 更新日期選擇器的月份年份顯示（內部函式）
      const updateMonthYear = () => {
        console.log('DOM.chat.initDatePicker: 更新月份年份顯示');
        const monthYearElement = document.getElementById('current-month-year');
        if (monthYearElement) {
          const monthNames = ['一月', '二月', '三月', '四月', '五月', '六月', 
                             '七月', '八月', '九月', '十月', '十一月', '十二月'];
          monthYearElement.textContent = `${monthNames[currentMonth]} ${currentYear}`;
        }
      };
      
      // 生成日期選擇器的日曆內容（內部函式）
      const generateCalendar = () => {
        console.log('DOM.chat.initDatePicker: 生成日曆');
        const calendarElement = document.getElementById('date-picker-calendar');
        if (!calendarElement) return;
        
        calendarElement.innerHTML = '';
        
        const firstDay = new Date(currentYear, currentMonth, 1);
        const lastDay = new Date(currentYear, currentMonth + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        const today = new Date();
        const selectedDate = DOM.chat.getSelectedDate();
        
        for (let i = 0; i < 42; i++) {
          const date = new Date(startDate);
          date.setDate(startDate.getDate() + i);
          
          const dateCell = document.createElement('div');
          dateCell.className = 'date-cell';
          dateCell.textContent = date.getDate();
          
          // 檢查是否為今天
          if (date.toDateString() === today.toDateString()) {
            dateCell.classList.add('today');
          }
          
          // 檢查是否為選中的日期
          if (selectedDate && date.toDateString() === selectedDate.toDateString()) {
            dateCell.classList.add('selected');
          }
          
          // 檢查是否為其他月份的日期
          if (date.getMonth() !== currentMonth) {
            dateCell.classList.add('other-month');
          }
          
          // 檢查是否為過去的日期
          if (date < today && date.toDateString() !== today.toDateString()) {
            dateCell.classList.add('disabled');
          } else {
            // 添加點擊事件
            DOM.events.add(dateCell, 'click', () => {
              console.log('DOM.chat.initDatePicker: 日期被點擊', date);
              // 移除其他選中的日期
              document.querySelectorAll('.date-cell.selected').forEach(cell => {
                cell.classList.remove('selected');
              });
              // 選中當前日期
              dateCell.classList.add('selected');
              DOM.chat.setSelectedDate(date);
              // 直接寫入 input 並關閉 modal
              const dateInput = document.getElementById('schedule-date');
              if (dateInput) {
                const formattedDate = DateUtils.formatDate(date);
                dateInput.value = formattedDate;
                console.log('DOM.chat.initDatePicker: 日期已設定', formattedDate);
                
                // 驗證設定的日期
                const validationResult = FormValidator.validateField('date', formattedDate, 'schedule');
                if (!validationResult.isValid) {
                  FormValidator.showValidationError(validationResult.errorMessage, dateInput);
                } else {
                  FormValidator.clearValidationError(dateInput);
                }
              }
              // 關閉 Modal
              const datePickerModal = bootstrap.Modal.getInstance(document.getElementById('date-picker-modal'));
              if (datePickerModal) {
                datePickerModal.hide();
              }
              // 強制清理 backdrop 和 body 狀態
              setTimeout(() => {
                document.querySelectorAll('.modal-backdrop').forEach(bd => bd.remove());
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
              }, 200);
            });
          }
          
          calendarElement.appendChild(dateCell);
        }
      };
      
      // 上個月按鈕
      const prevMonthBtn = document.getElementById('prev-month');
      if (prevMonthBtn) {
        // 移除舊的事件監聽器
        const newPrevMonthBtn = prevMonthBtn.cloneNode(true);
        prevMonthBtn.parentNode.replaceChild(newPrevMonthBtn, prevMonthBtn);
        
        DOM.events.add(newPrevMonthBtn, 'click', () => {
          console.log('DOM.chat.initDatePicker: 上個月按鈕被點擊');
          currentMonth--;
          if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
          }
          updateMonthYear();
          generateCalendar();
        });
      }
      
      // 下個月按鈕
      const nextMonthBtn = document.getElementById('next-month');
      if (nextMonthBtn) {
        // 移除舊的事件監聽器
        const newNextMonthBtn = nextMonthBtn.cloneNode(true);
        nextMonthBtn.parentNode.replaceChild(newNextMonthBtn, nextMonthBtn);
        
        DOM.events.add(newNextMonthBtn, 'click', () => {
          console.log('DOM.chat.initDatePicker: 下個月按鈕被點擊');
          currentMonth++;
          if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
          }
          updateMonthYear();
          generateCalendar();
        });
      }
      
      // 確定按鈕
      const confirmBtn = document.getElementById('confirm-date');
      if (confirmBtn) {
        // 移除舊的事件監聽器
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        
        DOM.events.add(newConfirmBtn, 'click', () => {
          console.log('DOM.chat.initDatePicker: 確定按鈕被點擊');
          const selectedDate = DOM.chat.getSelectedDate();
          if (selectedDate) {
            const dateInput = document.getElementById('schedule-date');
            if (dateInput) {
              const formattedDate = DateUtils.formatDate(selectedDate);
              dateInput.value = formattedDate;
              console.log('DOM.chat.initDatePicker: 日期已設定', formattedDate);
            }
          }
          
          // 關閉 Modal
          const datePickerModal = bootstrap.Modal.getInstance(document.getElementById('date-picker-modal'));
          if (datePickerModal) {
            datePickerModal.hide();
          }
          // 強制清理 backdrop 和 body 狀態
          setTimeout(() => {
            document.querySelectorAll('.modal-backdrop').forEach(bd => bd.remove());
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
          }, 200);
        });
      }
      
      // 初始化顯示
      updateMonthYear();
      generateCalendar();
    },
    
    // 格式化時間輸入
    formatTimeInput: (input) => {
      console.log('DOM.chat.formatTimeInput called：格式化時間輸入', { value: input.value });
      let value = input.value.replace(/[^0-9]/g, '');
      
      if (value.length >= 4) {
        value = value.substring(0, 4);
        const hours = parseInt(value.substring(0, 2));
        const minutes = parseInt(value.substring(2, 4));
        
        if (hours >= 0 && hours <= 23 && minutes >= 0 && minutes <= 59) {
          input.value = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
        } else {
          input.value = value.substring(0, 2) + ':' + value.substring(2, 4);
        }
      } else if (value.length >= 2) {
        input.value = value.substring(0, 2) + ':' + value.substring(2);
      } else {
        input.value = value;
      }
      
      console.log('DOM.chat.formatTimeInput: 格式化後的值', input.value);
    },
    
    // 驗證並格式化時間
    validateAndFormatTime: (input) => {
      console.log('DOM.chat.validateAndFormatTime called：驗證並格式化時間', { value: input.value });
      let value = input.value.trim();
      
      // 如果為空，設定預設值
      if (!value) {
        input.value = '20:00';
        return;
      }
      
      // 移除所有非數字字符
      const numbers = value.replace(/[^0-9]/g, '');
      
      if (numbers.length === 0) {
        input.value = '20:00';
        return;
      }
      
      if (numbers.length === 1) {
        input.value = `0${numbers}:00`;
        return;
      }
      
      if (numbers.length === 2) {
        const hours = parseInt(numbers);
        if (hours >= 0 && hours <= 23) {
          input.value = `${String(hours).padStart(2, '0')}:00`;
        } else {
          input.value = '20:00';
        }
        return;
      }
      
      if (numbers.length >= 3) {
        const hours = parseInt(numbers.substring(0, 2));
        const minutes = parseInt(numbers.substring(2, 4));
        
        if (hours >= 0 && hours <= 23 && minutes >= 0 && minutes <= 59) {
          input.value = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
        } else {
          input.value = '20:00';
        }
        return;
      }
      
      // 預設值
      input.value = '20:00';
    },
    
    // 提交表單
    submitScheduleForm: () => {
      console.log('DOM.chat.submitScheduleForm called：提交表單');
      
      const dateInput = document.getElementById('schedule-date');
      const startTimeInput = document.getElementById('schedule-start-time');
      const endTimeInput = document.getElementById('schedule-end-time');
      const notesInput = document.getElementById('schedule-notes');
      
      // 收集表單資料
      const formData = {
        date: dateInput?.value || '',
        startTime: startTimeInput?.value || '',
        endTime: endTimeInput?.value || '',
        notes: notesInput?.value || ''
      };
      
      console.log('DOM.chat.submitScheduleForm: 表單資料', formData);
      
      // 使用 FormValidator 驗證表單
      const validationResult = FormValidator.validateScheduleForm(formData);
      
      if (!validationResult.isValid) {
        console.warn('DOM.chat.submitScheduleForm: 表單驗證失敗', validationResult);
        FormValidator.showValidationError(validationResult.message);
        return;
      }
      
      // 檢查重複時段
      const existingSchedules = ChatStateManager.getProvidedSchedules();
      const isDuplicate = existingSchedules.some(schedule => {
        // 檢查是否為完全相同的時段
        const isExactDuplicate = schedule.date === formData.date && 
          schedule.startTime === formData.startTime && 
          schedule.endTime === formData.endTime;
        
        if (isExactDuplicate) {
          return true;
        }
        
        // 檢查是否為重疊時段（相同日期且時間有重疊）
        if (schedule.date === formData.date) {
          const existingStart = schedule.startTime;
          const existingEnd = schedule.endTime;
          const newStart = formData.startTime;
          const newEnd = formData.endTime;
          
          // 檢查時間重疊：新時段的開始時間 < 現有時段的結束時間 且 新時段的結束時間 > 現有時段的開始時間
          const isOverlapping = newStart < existingEnd && newEnd > existingStart;
          
          return isOverlapping;
        }
        
        return false;
      });
      
      if (isDuplicate) {
        console.warn('DOM.chat.submitScheduleForm: 檢測到重複或重疊時段', formData);
        const duplicateMessage = FormValidator.generateDuplicateScheduleMessage(formData, existingSchedules);
        FormValidator.showValidationError(duplicateMessage);
        return;
      }
      
      // 格式化輸出
      const formattedSchedule = `${formData.date} ${formData.startTime}~${formData.endTime}`;
      const notes = formData.notes.trim();
      
      console.log('DOM.chat.submitScheduleForm: 格式化後的資料', {
        formattedSchedule,
        notes
      });
      
      // 記錄時段資料到聊天狀態
      ChatStateManager.addSchedule({
        date: formData.date,
        startTime: formData.startTime,
        endTime: formData.endTime,
        notes: notes,
        formattedSchedule: formattedSchedule
      });
      console.log('DOM.chat.submitScheduleForm: 時段資料已記錄', ChatStateManager.getProvidedSchedules());
      
      // 添加使用者訊息
      const userMessage = `提供方便時段：${formattedSchedule}${notes ? `\n備註：${notes}` : ''}`;
      DOM.chat.addUserMessage(userMessage);
      
      // 隱藏表單
      const scheduleForm = document.getElementById('schedule-form');
      if (scheduleForm) {
        scheduleForm.style.display = 'none';
      }
      
      // 清空表單
      if (dateInput) dateInput.value = '';
      if (startTimeInput) startTimeInput.value = '20:00';
      if (endTimeInput) endTimeInput.value = '22:00';
      if (notesInput) notesInput.value = '';
      
      // 重置選中的日期
      DOM.chat.setSelectedDate(null);
      
      // 模擬 Giver 回覆
      setTimeout(() => {
        // 將訊息與按鈕組合在同一個訊息框
        const responseHTML = TEMPLATES.chat.afterScheduleOptions(formattedSchedule, notes);
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
          chatMessages.insertAdjacentHTML('beforeend', responseHTML);
          // 綁定事件
          const afterBtns = chatMessages.querySelectorAll('#after-schedule-options .btn-option');
          afterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
              const option = btn.getAttribute('data-option');
              const optionText = btn.textContent.trim();
              console.log('after-schedule-options 按鈕被點擊:', { option, optionText });
              // 處理不同選項
              if (option === 'single-time') {
                DOM.chat.handleSingleTime();
              } else if (option === 'multiple-times') {
                DOM.chat.handleMultipleTimes();
              } else if (option === 'view-all') {
                DOM.chat.handleViewAllSchedules();
              } else if (option === 'finish') {
                DOM.chat.addUserMessage('已新增完成所有時段，請協助送出給 Giver');
                setTimeout(() => {
                  DOM.chat.handleSuccessProvideTime();
                }, 1000);
              } else if (option === 'cancel') {
                DOM.chat.handleCancelSchedule();
              }
              // 點擊後隱藏按鈕區塊
              const optionsContainer = btn.closest('.chat-options-buttons');
              if (optionsContainer) {
                optionsContainer.classList.remove('container-visible');
                optionsContainer.classList.add('chat-options-hidden');
              }
            });
          });
          // 滾動到底部
          chatMessages.scrollTop = chatMessages.scrollHeight;
        }
      }, 1000);
    },
    
    // 處理多筆時段選項
    handleMultipleTimes: () => {
      console.log('DOM.chat.handleMultipleTimes called：處理多筆時段選項');
      setTimeout(() => {
        // 使用新的模板顯示訊息和按鈕
        const responseHTML = TEMPLATES.chat.multipleTimesUnderConstruction();
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
          chatMessages.insertAdjacentHTML('beforeend', responseHTML);
          // 綁定按鈕事件
          const buttons = chatMessages.querySelectorAll('#multiple-times-under-construction-options .btn-option');
          buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
              const option = btn.getAttribute('data-option');
              const optionText = btn.textContent.trim();
              console.log('multiple-times-under-construction-options 按鈕被點擊:', { option, optionText });
              if (option === 'single-time') {
                DOM.chat.handleSingleTime();
              } else if (option === 'cancel') {
                DOM.chat.handleCancelSchedule();
              }
              // 點擊後隱藏按鈕區塊
              const optionsContainer = btn.closest('.chat-options-buttons');
              if (optionsContainer) {
                optionsContainer.classList.remove('container-visible');
                optionsContainer.classList.add('chat-options-hidden');
              }
            });
          });
          chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // 設定多筆時段輸入模式
        ChatStateManager.setMultipleTimesMode(true);
        console.log('DOM.chat.handleMultipleTimes: 已設定多筆時段輸入模式');
      }, 1000);
    },
    
    // 處理查看所有已提供時段選項
    handleViewAllSchedules: () => {
      console.log('DOM.chat.handleViewAllSchedules called：處理查看所有已提供時段選項');
      
      const providedSchedules = ChatStateManager.getProvidedSchedules();
      console.log('DOM.chat.handleViewAllSchedules: 已提供的時段資料', providedSchedules);
      
      // 重繪表格（內部函式）：生成時段表格的 HTML 內容
      function renderTable() {
        console.log('renderTable() called: 重繪時段表格');
        const schedules = ChatStateManager.getProvidedSchedules();
        console.log('renderTable() schedules:', schedules);
        const result = TEMPLATES.chat.scheduleTable(schedules);
        console.log('renderTable() completed: 表格模板已生成');
        return result;
      }
      
      // 真正渲染與事件綁定（內部函式）：渲染表格並綁定相關事件
      function mountTable() {
        console.log('mountTable() called: 渲染與事件綁定表格');
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) {
          console.warn('mountTable() error: 找不到 chat-messages 元素');
          return;
        }
        console.log('mountTable() 開始移除舊的時段表格訊息泡泡');
        // 先移除所有舊的時段表格訊息泡泡
        chatMessages.querySelectorAll('.giver-message .schedule-table').forEach(table => {
          const bubble = table.closest('.giver-message');
          if (bubble) bubble.remove();
        });
        console.log('mountTable() 插入新的表格訊息');
        // 插入新的表格訊息
        chatMessages.insertAdjacentHTML('beforeend', renderTable());          
        // 綁定表格內按鈕事件
        const table = chatMessages.querySelector('.giver-message:last-child table');
        if (!table) {
          console.warn('mountTable() error: 找不到新插入的表格');
          return;
        }
        console.log('mountTable() 綁定編輯按鈕事件');
        // 編輯按鈕
        table.querySelectorAll('.schedule-edit-btn').forEach(btn => {
          btn.addEventListener('click', function() {
            const tr = btn.closest('tr');
            const idx = parseInt(tr.getAttribute('data-index'));
            const schedules = ChatStateManager.getProvidedSchedules();
            const schedule = schedules[idx];
            console.log('mountTable() 編輯按鈕被點擊:', { idx, schedule });
            // 直接呼叫 handleSingleTime 進入編輯模式
            DOM.chat.handleSingleTime(idx, schedule);
          });
        });
        console.log('mountTable() 綁定刪除按鈕事件');
        // 刪除按鈕
        table.querySelectorAll('.schedule-delete-btn').forEach(btn => {
          btn.addEventListener('click', function() {
            const tr = btn.closest('tr');
            const idx = parseInt(tr.getAttribute('data-index'));
            console.log('mountTable() 刪除按鈕被點擊:', { idx });
            // 彈出確認
            UIComponents.confirmDialog({
              title: '刪除時段',
              message: '確定要刪除此時段嗎？',
              confirmText: '刪除',
              cancelText: '取消',
              onConfirm: () => {
                console.log('mountTable() 確認刪除時段:', { idx });
                // 刪除狀態
                let schedules = ChatStateManager.getProvidedSchedules();
                schedules.splice(idx, 1);
                ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES, schedules);
                mountTable();
              }
            });
          });
        });
        console.log('mountTable() 綁定下方動作按鈕事件');
        // 綁定下方動作按鈕
        const afterBtns = chatMessages.querySelectorAll('#after-view-all-options .btn-option');
        afterBtns.forEach(btn => {
          btn.addEventListener('click', (e) => {
            const option = btn.getAttribute('data-option');
            const optionText = btn.textContent.trim();
            console.log('mountTable() after-view-all-options 按鈕被點擊:', { option, optionText });
            if (option === 'single-time') {
              DOM.chat.handleSingleTime();
            } else if (option === 'multiple-times') {
              DOM.chat.handleMultipleTimes();
            } else if (option === 'finish') {
              DOM.chat.addUserMessage('已新增完成所有時段，請協助送出給 Giver');
              setTimeout(() => {
                DOM.chat.handleSuccessProvideTime();
              }, 1000);
            } else if (option === 'cancel') {
              DOM.chat.handleCancelSchedule();
            }
            // 點擊後隱藏按鈕區塊
            const optionsContainer = btn.closest('.chat-options-buttons');
            if (optionsContainer) {
              optionsContainer.classList.remove('container-visible');
              optionsContainer.classList.add('chat-options-hidden');
            }
          });
        });
        console.log('mountTable() 滾動到底部');
        // 滾動到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
        console.log('mountTable() completed: 表格渲染與事件綁定完成');
      }
      
      setTimeout(() => {
        if (providedSchedules.length === 0) {
          const html = TEMPLATES.chat.noSchedulesWithButtons();
          const chatMessages = document.getElementById('chat-messages');
          if (chatMessages) {
            chatMessages.insertAdjacentHTML('beforeend', html);
            DOM.chat.setupScheduleOptionButtons();
            chatMessages.scrollTop = chatMessages.scrollHeight;
          }
        } else {
          mountTable();
        }
      }, 1000);
    },
    
    // 處理取消預約選項
    handleCancelSchedule: () => {
      console.log('DOM.chat.handleCancelSchedule called：處理取消預約選項');
      setTimeout(() => {
        const response = '好的，已取消預約。<br><br>如未來有需要預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。<br><br>有其他問題需要協助嗎？';
        DOM.chat.addGiverResponse(response);
      }, 1000);
    },

    // 新增：處理成功提供時間選項
    handleSuccessProvideTime: () => {
      console.log('DOM.chat.handleSuccessProvideTime called：處理成功提供時間選項');
      
      const providedSchedules = ChatStateManager.getProvidedSchedules();
      console.log('DOM.chat.handleSuccessProvideTime: 已提供的時段資料', providedSchedules);
      
      setTimeout(() => {
        // 使用新的模板顯示成功訊息和表格
        const responseHTML = TEMPLATES.chat.successProvideTime(providedSchedules);
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
          chatMessages.insertAdjacentHTML('beforeend', responseHTML);
          
          // 綁定修改和刪除按鈕事件
          const editButtons = chatMessages.querySelectorAll('.success-provide-table .edit-provide-btn');
          editButtons.forEach(btn => {
            btn.addEventListener('click', function() {
              const tr = btn.closest('tr');
              const idx = parseInt(tr.getAttribute('data-index'));
              const schedule = providedSchedules[idx];
              // 直接呼叫 handleSingleTime 進入編輯模式
              DOM.chat.handleSingleTime(idx, schedule);
            });
          });
          
          const deleteButtons = chatMessages.querySelectorAll('.success-provide-table .delete-provide-btn');
          deleteButtons.forEach(btn => {
            btn.addEventListener('click', function() {
              const tr = btn.closest('tr');
              const idx = parseInt(tr.getAttribute('data-index'));
              // 彈出確認對話框
              UIComponents.confirmDialog({
                title: '取消提供時間',
                message: '確定要取消提供此時間嗎？',
                confirmText: '取消提供',
                cancelText: '保留',
                onConfirm: () => {
                  // 從狀態中移除該時段
                  let schedules = ChatStateManager.getProvidedSchedules();
                  schedules.splice(idx, 1);
                  ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES, schedules);
                  
                  // 重新渲染表格
                  if (schedules.length === 0) {
                    // 如果沒有時段了，顯示取消訊息
                    DOM.chat.addGiverResponse('已取消所有提供時間。<br><br>如未來有需要預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。<br><br>有其他問題需要協助嗎？');
                  } else {
                    // 重新渲染表格
                    const updatedHTML = TEMPLATES.chat.successProvideTime(schedules);
                    const currentMessage = chatMessages.querySelector('.success-provide-table').closest('.giver-message');
                    if (currentMessage) {
                      currentMessage.outerHTML = updatedHTML;
                      // 重新綁定事件
                      const newEditButtons = chatMessages.querySelectorAll('.success-provide-table .edit-provide-btn');
                      newEditButtons.forEach(newBtn => {
                        newBtn.addEventListener('click', function() {
                          const newTr = newBtn.closest('tr');
                          const newIdx = parseInt(newTr.getAttribute('data-index'));
                          const newSchedule = schedules[newIdx];
                          DOM.chat.handleSingleTime(newIdx, newSchedule);
                        });
                      });
                      
                      const newDeleteButtons = chatMessages.querySelectorAll('.success-provide-table .delete-provide-btn');
                      newDeleteButtons.forEach(newBtn => {
                        newBtn.addEventListener('click', function() {
                          const newTr = newBtn.closest('tr');
                          const newIdx = parseInt(newTr.getAttribute('data-index'));
                          UIComponents.confirmDialog({
                            title: '取消提供時間',
                            message: '確定要取消提供此時間嗎？',
                            confirmText: '取消提供',
                            cancelText: '保留',
                            onConfirm: () => {
                              let newSchedules = ChatStateManager.getProvidedSchedules();
                              newSchedules.splice(newIdx, 1);
                              ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES, newSchedules);
                              if (newSchedules.length === 0) {
                                DOM.chat.addGiverResponse('已取消所有提供時間。<br><br>如未來有需要預約 Giver 時間，請使用聊天輸入區域下方的功能按鈕。<br><br>有其他問題需要協助嗎？');
                              } else {
                                const newUpdatedHTML = TEMPLATES.chat.successProvideTime(newSchedules);
                                const newCurrentMessage = chatMessages.querySelector('.success-provide-table').closest('.giver-message');
                                if (newCurrentMessage) {
                                  newCurrentMessage.outerHTML = newUpdatedHTML;
                                }
                              }
                            }
                          });
                        });
                      });
                    }
                  }
                }
              });
            });
          });
          
          chatMessages.scrollTop = chatMessages.scrollHeight;
        }
      }, 1000);
    },
    
    // 獲取選中的日期
    getSelectedDate: () => {
      console.log('DOM.chat.getSelectedDate called：獲取選中的日期');
      return ChatStateManager.getSelectedDate();
    },
    
    // 設定選中的日期
    setSelectedDate: (date) => {
      console.log('DOM.chat.setSelectedDate called：設定選中的日期', { date });
      ChatStateManager.setSelectedDate(date);
    },
    
    // 設定輸入控制項
    setupInputControls: (chatInput, sendBtn) => {
      console.log('DOM.chat.setupInputControls called：設定輸入控制項', { chatInput, sendBtn });
      
      if (!chatInput || !sendBtn) {
        console.error('DOM.chat.setupInputControls: 聊天輸入框或發送按鈕未找到');
        return;
      }
      
      console.log('DOM.chat.setupInputControls: 設定聊天輸入控制項:', { chatInput, sendBtn });
      
      // 發送訊息函數（內部函式）：處理聊天訊息的發送邏輯
      const sendMessage = () => {
        const message = chatInput.value.trim();
        
        // 使用 FormValidator 驗證訊息
        const validationResult = FormValidator.validateChatMessage(message);
        if (!validationResult.isValid) {
          console.warn('DOM.chat.setupInputControls: 訊息驗證失敗:', validationResult);
          FormValidator.showValidationError(validationResult.message);
          return;
        }
        
        console.log('DOM.chat.setupInputControls: 發送訊息:', message);
        
        // 添加使用者訊息
        DOM.chat.addUserMessage(message);
        
        // 清空輸入框
        chatInput.value = '';
        
        if (ChatStateManager.isMultipleTimesMode()) {
          // 處理多筆時段輸入
          console.log('DOM.chat.setupInputControls: 處理多筆時段輸入', message);
          DOM.chat.handleMultipleTimesSubmission(message);
        } else {
          // 模擬 Giver 回覆
          setTimeout(() => {
            DOM.chat.addGiverResponse(message);
          }, 1000);
        }
      };
      
      // 按 Enter 鍵發送訊息
      DOM.events.add(chatInput, 'keypress', (e) => {
        console.log('DOM.chat.setupInputControls: 按鍵事件:', e.key);
        if (e.key === 'Enter') {
          sendMessage();
        }
      });
      
      // 點擊發送按鈕
      DOM.events.add(sendBtn, 'click', () => {
        console.log('DOM.chat.setupInputControls: 發送按鈕被點擊');
        sendMessage();
      });
    },
    
    // 設定模態框事件
    setupModalEvents: () => {
      console.log('DOM.chat.setupModalEvents called：設定模態框事件');
      const modalElement = DOM.chatElements.modalElement();
      if (modalElement) {
        // 監聽 modal 隱藏事件
        DOM.events.add(modalElement, 'hidden.bs.modal', () => {
          console.log('DOM.chat.setupModalEvents: Modal 已隱藏，清理聊天功能');
          DOM.chat.cleanup();
          
          // 強制處理焦點問題
          DOM.chat.forceFocusToBody();
          
          // 確保 backdrop 被清理
          setTimeout(() => {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
              backdrop.remove();
            }
            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = '';
          }, 0);
        });
        
        // 監聽 modal 顯示事件
        DOM.events.add(modalElement, 'shown.bs.modal', () => {
          console.log('DOM.chat.setupModalEvents: Modal 已顯示');
          // 確保 modal 有正確的 tabindex
          modalElement.setAttribute('tabindex', '-1');
          modalElement.removeAttribute('inert');
          
          // 設定聊天輸入區域的額外功能按鈕事件監聽器
          DOM.chat.setupChatExtraButtons();
        });
      }
    },
    
    // 強制將焦點移到 body
    forceFocusToBody: () => {
      console.log('DOM.chat.forceFocusToBody called：強制將焦點移到 body');
      // 使用多種方法確保焦點正確轉移
      setTimeout(() => {
        // 移除所有可能的焦點
        const activeElement = document.activeElement;
        if (activeElement && activeElement !== document.body) {
          activeElement.blur();
        }
        
        // 移除 modal 的 tabindex 屬性
        const modalElement = DOM.chatElements.modal();
        if (modalElement) {
          modalElement.removeAttribute('tabindex');
          modalElement.setAttribute('inert', '');
        }
        
        // 強制焦點到 body
        document.body.focus();
        
        // 如果焦點仍然不在 body 上，再次嘗試
        setTimeout(() => {
          if (document.activeElement !== document.body) {
            document.body.focus();
          }
        }, 50);
      }, 0);
    },
    
    // 顯示關閉確認對話框
    showCloseConfirmation: () => {
      console.log('DOM.chat.showCloseConfirmation called：顯示關閉確認對話框');
      showConfirmDialog({
        title: '差幾步就能完成申請囉！',
        message: 'Giver 提供的名額即將額滿，現在離開下次需要重新申請哦！要繼續完成嗎？',
        confirmText: '繼續完成',
        cancelText: '忍痛離開',
        cleanupBackdrop: false, // 點擊繼續完成時不清理 backdrop
        onConfirm: () => {
          // 繼續聊天，不做任何操作
        },
        onCancel: () => {
          // 關閉聊天對話框
          const chatModal = bootstrap.Modal.getInstance(DOM.chatElements.modal());
          if (chatModal) {
            chatModal.hide();
          }
          // 清理 modal 和 backdrop
          setTimeout(() => {
            const modalElement = DOM.chatElements.modal();
            if (modalElement) {
              DOM.utils.cleanupModal(modalElement);
            }
            // 額外清理 backdrop
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) backdrop.remove();
            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = '';
            
            // 強制處理焦點問題：當使用者關閉對話框時，強制將焦點移到 body，避免使用者無法操作其他元素。
            DOM.chat.forceFocusToBody(); 
          }, 150);
        }
      });
    },
    
    // 添加使用者訊息
    addUserMessage: (message) => {
      console.log('DOM.chat.addUserMessage called：添加使用者訊息', { message });
      
      const messageElement = DOM.message.createMessage(message, 'user');
      if (!messageElement) {
        console.error('DOM.chat.addUserMessage: 無法創建使用者訊息元素');
        return;
      }
      
      DOM.message.addToChat(messageElement); // 將使用者訊息添加到聊天區域
      
      // 使用 ChatStateManager 記錄訊息歷史
      ChatStateManager.addUserMessage(message);
      console.log('DOM.chat.addUserMessage: 使用者訊息已添加');
    },
    
    // 添加 Giver 回覆
    addGiverResponse: (message) => {
      console.log('DOM.chat.addGiverResponse called：添加 Giver 回覆', { message });
      const response = message;
      console.log('DOM.chat.addGiverResponse: Giver 回覆內容:', response);
      const messageElement = DOM.message.createMessage(response, 'giver', true);
      if (!messageElement) {
        console.error('DOM.chat.addGiverResponse: 無法創建 Giver 訊息元素');
        return;
      }
      DOM.message.addToChat(messageElement);
      ChatStateManager.addGiverMessage(response);
      console.log('DOM.chat.addGiverResponse: Giver 回覆已添加');
    },
    
    // 獲取 Giver 回覆
    getGiverResponse: (userMessage) => {
      console.log('DOM.chat.getGiverResponse called：獲取 Giver 回覆', { userMessage });
      return BusinessLogic.chat.generateResponse(userMessage);
    },
    
    // 清理聊天功能
    cleanup: () => {
      console.log('DOM.chat.cleanup called：清理聊天功能');
      
      // 清空聊天區域並重新設定初始狀態
      DOM.message.clearChat();
      
      // 移除關閉按鈕
      const closeBtn = DOM.getElement('.btn-close-header');
      if (closeBtn) {
        closeBtn.remove();
      }
      
      // 隱藏並清理表單
      const scheduleForm = document.getElementById('schedule-form');
      if (scheduleForm) {
        scheduleForm.style.display = 'none';
        
        // 清空表單欄位
        const dateInput = document.getElementById('schedule-date');
        const startTimeInput = document.getElementById('schedule-start-time');
        const endTimeInput = document.getElementById('schedule-end-time');
        const notesInput = document.getElementById('schedule-notes');
        
        if (dateInput) dateInput.value = '';
        if (startTimeInput) startTimeInput.value = '';
        if (endTimeInput) endTimeInput.value = '';
        if (notesInput) notesInput.value = '';
      }
      
      // 清理日期選擇器狀態
      ChatStateManager.setSelectedDate(null);
      
      // 關閉日期選擇器 Modal
      const datePickerModal = bootstrap.Modal.getInstance(document.getElementById('date-picker-modal'));
      if (datePickerModal) {
        datePickerModal.hide();
      }
      
      // 清理聊天狀態
      ChatStateManager.endChatSession();
      
      // 清理所有聊天相關的事件監聽器
      const chatInput = DOM.chatElements.input();
      const sendBtn = DOM.chatElements.sendBtn();
      
      if (chatInput) {
        // 使用 DOM.events.removeAll 移除所有事件監聽器
        DOM.events.removeAll(chatInput);
      }
      
      if (sendBtn) {
        // 使用 DOM.events.removeAll 移除所有事件監聽器
        DOM.events.removeAll(sendBtn);
      }
      
      console.log('DOM.chat.cleanup: 聊天功能清理完成');
    },
    
    // 聊天功能工具
    utils: {
      // 獲取聊天統計
      getStats: () => {
        console.log('DOM.chat.utils.getStats called：獲取聊天統計');
        return ChatStateManager.getStats();
      },
      
      // 獲取聊天歷史
      getHistory: () => {
        console.log('DOM.chat.utils.getHistory called：獲取聊天歷史');
        return ChatStateManager.getMessageHistory();
      },
      
      // 清空聊天歷史
      clearHistory: () => {
        console.log('DOM.chat.utils.clearHistory called：清空聊天歷史');
        ChatStateManager.clearMessageHistory();
      },
      
      // 檢查聊天是否活躍
      isActive: () => {
        console.log('DOM.chat.utils.isActive called：檢查聊天是否活躍');
        return ChatStateManager.isActive();
      },
      
      // 獲取當前 Giver
      getCurrentGiver: () => {
        console.log('DOM.chat.utils.getCurrentGiver called：獲取當前 Giver');
        return ChatStateManager.getCurrentGiver();
      },
      
      // 調試聊天功能
      debug: () => {
        console.group('DOM.chat.utils.debug called：聊天功能調試資訊');
        ChatStateManager.debug();
        console.groupEnd();
      }
    },
    
    // 設定選項按鈕事件監聽器
    setupOptionButtons: () => {
      console.log('DOM.chat.setupOptionButtons called：設定選項按鈕');
      const optionButtons = DOM.getElements('.btn-option');
      optionButtons.forEach(button => {
        // 先移除舊的事件監聽器（用 cloneNode 替換）
        const newBtn = button.cloneNode(true);
        button.parentNode.replaceChild(newBtn, button);
        // 再綁定新的
        DOM.events.add(newBtn, 'click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          const option = newBtn.getAttribute('data-option');
          const optionText = newBtn.textContent.trim();
          console.log('DOM.chat.setupOptionButtons: 選項按鈕被點擊:', { option, optionText });
          DOM.chat.addUserMessage(optionText);
          if (option === 'schedule') {
            DOM.chat.handleScheduleOption();
          } else if (option === 'skip') {
            DOM.chat.handleSkipOption();
          }
          // 隱藏選項按鈕
          const optionsContainer = newBtn.closest('.chat-options-buttons');
          if (optionsContainer) {
            optionsContainer.style.display = 'none';
          }
        });
      });
    },
    
    // 處理多筆時段提交
    handleMultipleTimesSubmission: (message) => {
      console.log('DOM.chat.handleMultipleTimesSubmission called：處理多筆時段提交', { message });
      
      // 使用 FormValidator 驗證多筆時段
      const validationResult = FormValidator.validateMultipleSchedules(message);
      
      if (!validationResult.isValid) {
        console.warn('DOM.chat.handleMultipleTimesSubmission: 多筆時段驗證失敗', validationResult);
        setTimeout(() => {
          DOM.chat.addGiverResponse(validationResult.message);
        }, 1000);
        return;
      }
      
      // 使用 DateUtils 解析多筆時段
      const { isValid, schedules } = DateUtils.parseMultipleSchedules(message);
      
      console.log('DOM.chat.handleMultipleTimesSubmission: 解析出的時段', schedules);
      
      if (!isValid) {
        // 沒有解析到有效時段
        setTimeout(() => {
          DOM.chat.addGiverResponse('抱歉，我無法解析您提供的時段格式。請使用以下格式：\n日期 時間範圍\n例如：\n2024/01/15 14:00-16:00\n2024/01/17 10:00-12:00');
        }, 1000);
        return;
      }
      
      // 檢查重複時段
      const existingSchedules = ChatStateManager.getProvidedSchedules();
      const duplicateSchedules = [];
      
      schedules.forEach(schedule => {
        const isDuplicate = existingSchedules.some(existingSchedule => {
          // 檢查是否為完全相同的時段
          const isExactDuplicate = existingSchedule.date === schedule.date && 
            existingSchedule.startTime === schedule.startTime && 
            existingSchedule.endTime === schedule.endTime;
          
          if (isExactDuplicate) {
            return true;
          }
          
          // 檢查是否為重疊時段（相同日期且時間有重疊）
          if (existingSchedule.date === schedule.date) {
            const existingStart = existingSchedule.startTime;
            const existingEnd = existingSchedule.endTime;
            const newStart = schedule.startTime;
            const newEnd = schedule.endTime;
            
            // 檢查時間重疊：新時段的開始時間 < 現有時段的結束時間 且 新時段的結束時間 > 現有時段的開始時間
            const isOverlapping = newStart < existingEnd && newEnd > existingStart;
            
            return isOverlapping;
          }
          
          return false;
        });
        
        if (isDuplicate) {
          duplicateSchedules.push(schedule);
        }
      });
      
      if (duplicateSchedules.length > 0) {
        console.warn('DOM.chat.handleMultipleTimesSubmission: 檢測到重複或重疊時段', duplicateSchedules);
        
        // 為每個重複的時段生成詳細錯誤訊息
        const duplicateMessages = duplicateSchedules.map(schedule => {
          const duplicateMessage = FormValidator.generateDuplicateScheduleMessage(schedule, existingSchedules);
          return `• ${schedule.formattedSchedule}：${duplicateMessage}`;
        });
        
        const errorMessage = `以下時段與已提供的時段重複或重疊：\n${duplicateMessages.join('\n')}`;
        
        setTimeout(() => {
          DOM.chat.addGiverResponse(errorMessage);
        }, 1000);
        return;
      }
      
      // 記錄時段資料
      ChatStateManager.addSchedules(schedules);
      
      // 退出多筆時段輸入模式
      ChatStateManager.setMultipleTimesMode(false);
      
      // 顯示提交結果
      setTimeout(() => {
        let scheduleList = '';
        schedules.forEach((schedule, index) => {
          const scheduleNumber = index + 1;
          scheduleList += `• 時段 ${scheduleNumber}：${schedule.formattedSchedule}\n`;
        });
        
        const scheduleCount = schedules.length;
        
        const responseHTML = TEMPLATES.chat.afterMultipleScheduleOptions().replace('{{SCHEDULE_LIST}}', scheduleList).replace('{{SCHEDULE_COUNT}}', scheduleCount);
        
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
          chatMessages.insertAdjacentHTML('beforeend', responseHTML);
          // 綁定事件
          const afterBtns = chatMessages.querySelectorAll('#after-multiple-schedule-options .btn-option');
          afterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
              const option = btn.getAttribute('data-option');
              const optionText = btn.textContent.trim();
              console.log('after-multiple-schedule-options 按鈕被點擊:', { option, optionText });
              // 處理不同選項
              if (option === 'single-time') {
                DOM.chat.handleSingleTime();
              } else if (option === 'multiple-times') {
                DOM.chat.handleMultipleTimes();
              } else if (option === 'view-all') {
                DOM.chat.handleViewAllSchedules();
              } else if (option === 'finish') {
                DOM.chat.addUserMessage('已新增完成所有時段，請協助送出給 Giver');
                setTimeout(() => {
                  DOM.chat.handleSuccessProvideTime();
                }, 1000);
              } else if (option === 'cancel') {
                DOM.chat.handleCancelSchedule();
              }
              // 點擊後隱藏按鈕區塊
              btn.closest('.chat-options-buttons').style.display = 'none';
            });
          });
          // 滾動到底部
          chatMessages.scrollTop = chatMessages.scrollHeight;
        }
      }, 1000);
    },

    // 新增 showScheduleOptionsWithViewAll
    showScheduleOptionsWithViewAll: () => {
      console.log('DOM.chat.showScheduleOptionsWithViewAll called：顯示 5 按鈕預約選項');
      const scheduleOptionsHTML = TEMPLATES.chat.scheduleOptionsWithViewAll();
      const chatMessages = document.getElementById('chat-messages');
      if (chatMessages) {
        chatMessages.insertAdjacentHTML('beforeend', scheduleOptionsHTML);
        DOM.chat.setupScheduleOptionButtons();
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    },

    // 處理互斥選擇邏輯
    handleMutualExclusion: (changedCheckbox) => {
      console.log('DOM.chat.handleMutualExclusion called：處理互斥選擇邏輯', { 
        option: changedCheckbox.getAttribute('data-option'), 
        checked: changedCheckbox.checked 
      });
      
      const allCheckboxes = document.querySelectorAll('.chat-checkbox-options input[type="checkbox"]');
      const changedOption = changedCheckbox.getAttribute('data-option');
      
      // 重置所有選項的狀態
      allCheckboxes.forEach(checkbox => {
        const label = checkbox.nextElementSibling;
        if (label) {
          label.style.textDecoration = 'none';
          label.style.color = '';
        }
        checkbox.disabled = false;
      });
      
      // 根據選中的選項來禁用不相容的選項
      if (changedCheckbox.checked) {
        switch (changedOption) {
          case 'demo-time-1':
          case 'demo-time-2':
            // 如果選擇了 Demo 時間，禁用其他選項
            allCheckboxes.forEach(checkbox => {
              const option = checkbox.getAttribute('data-option');
              if (option !== 'demo-time-1' && option !== 'demo-time-2') {
                checkbox.disabled = true;
                checkbox.checked = false;
                const label = checkbox.nextElementSibling;
                if (label) {
                  label.style.textDecoration = 'line-through';
                  label.style.color = '#6c757d';
                }
              }
            });
            break;
            
          case 'provide-my-time':
            // 如果選擇了提供我的時間，禁用 Demo 時間和取消選項
            allCheckboxes.forEach(checkbox => {
              const option = checkbox.getAttribute('data-option');
              if (option === 'demo-time-1' || option === 'demo-time-2' || option === 'cancel') {
                checkbox.disabled = true;
                checkbox.checked = false;
                const label = checkbox.nextElementSibling;
                if (label) {
                  label.style.textDecoration = 'line-through';
                  label.style.color = '#6c757d';
                }
              }
            });
            break;
            
          case 'cancel':
            // 如果選擇了取消，禁用其他所有選項
            allCheckboxes.forEach(checkbox => {
              const option = checkbox.getAttribute('data-option');
              if (option !== 'cancel') {
                checkbox.disabled = true;
                checkbox.checked = false;
                const label = checkbox.nextElementSibling;
                if (label) {
                  label.style.textDecoration = 'line-through';
                  label.style.color = '#6c757d';
                }
              }
            });
            break;
        }
      }
    },
  },
  
  // 資料載入管理工具
  dataLoader: {
    // 載入狀態管理
    state: {
      isLoading: false,
      lastLoadTime: null,
      loadCount: 0,
      errorCount: 0,
      cache: new Map(),
      retryCount: 0,
      loadingElement: null
    },
    
    // API 配置
    config: {
      baseURL: BASE_URL,
      timeout: 10000,
      retryDelay: 1000,
      maxRetries: 3,
      cacheExpiry: 5 * 60 * 1000 // 5分鐘
    },
    
    // 載入 Giver 資料
    loadGivers: async ({ onSuccess, onError, onComplete, showLoading = true } = {}) => {
      console.log('DOM.dataLoader.loadGivers called：載入 Giver 資料');
      // 檢查快取
      if (DOM.dataLoader.isCached('givers')) {
        const cachedData = DOM.dataLoader.getCached('givers');
        console.log('DOM.dataLoader.loadGivers: 使用快取的 Giver 資料');
        onSuccess?.(cachedData);
        onComplete?.();
        return cachedData;
      }
      
      // 顯示載入狀態
      if (showLoading) {
        DOM.dataLoader.showLoading();
      }
      
      try {
        DOM.dataLoader.state.isLoading = true;
        DOM.dataLoader.state.lastLoadTime = new Date();
        
        console.log('DOM.dataLoader.loadGivers: 開始載入 Giver 資料');
        
        const response = await axios.get(DOM.dataLoader.config.baseURL);
        
        // 處理成功回應
        const giversData = response.data.results || [];
        console.log('DOM.dataLoader.loadGivers: Giver 資料載入成功:', giversData.length, '筆資料');
        
        // 更新應用狀態
        appState.givers = giversData;
        
        // 快取資料
        DOM.dataLoader.cacheData('givers', giversData);
        
        // 渲染 UI
        renderGiverList(getGiversByPage(1));
        renderPaginator(giversData.length);
        
        // 重置重試計數
        DOM.dataLoader.state.retryCount = 0;
        DOM.dataLoader.state.loadCount++;
        
        // 回調函數
        onSuccess?.(giversData);
        
        return giversData;
        
      } catch (error) {
        console.error('DOM.dataLoader.loadGivers: Giver 資料載入失敗:', error);
        
        DOM.dataLoader.state.errorCount++;
        
        // 處理錯誤
        DOM.dataLoader.handleError(error, () => {
          DOM.dataLoader.loadGivers({ onSuccess, onError, onComplete, showLoading });
        });
        
        onError?.(error);
        
        throw error;
        
      } finally {
        DOM.dataLoader.state.isLoading = false;
        if (showLoading) {
          DOM.dataLoader.hideLoading();
        }
        onComplete?.();
      }
    },
    
    // 載入特定 Giver 資料
    loadGiverById: async (giverId, options = {}) => {
      console.log('DOM.dataLoader.loadGiverById called：載入特定 Giver 資料', { giverId });
      const {
        forceRefresh = false,
        showLoading = true,
        onSuccess = null,
        onError = null
      } = options;
      
      const cacheKey = `giver_${giverId}`;
      
      // 檢查快取
      if (!forceRefresh && DOM.dataLoader.isCached(cacheKey)) {
        const cachedData = DOM.dataLoader.getCached(cacheKey);
        console.log('DOM.dataLoader.loadGiverById: 使用快取的 Giver 資料:', giverId);
        if (onSuccess) onSuccess(cachedData);
        return cachedData;
      }
      
      // 顯示載入狀態
      if (showLoading) {
        DOM.dataLoader.showLoading();
      }
      
      try {
        console.log('DOM.dataLoader.loadGiverById: 載入特定 Giver 資料:', giverId);
        
        const response = await DOM.dataLoader.makeRequest(cacheKey, {
          method: 'GET',
          url: `${DOM.dataLoader.config.baseURL}/${giverId}`
        });
        
        const giverData = response.data;
        console.log('DOM.dataLoader.loadGiverById: Giver 資料載入成功:', giverData);
        
        // 快取資料
        DOM.dataLoader.cacheData(cacheKey, giverData);
        
        if (onSuccess) onSuccess(giverData);
        return giverData;
        
      } catch (error) {
        console.error('DOM.dataLoader.loadGiverById: Giver 資料載入失敗:', error);
        if (onError) onError(error);
        throw error;
        
      } finally {
        if (showLoading) {
          DOM.dataLoader.hideLoading();
        }
      }
    },
    
    // 搜尋 Giver 資料
    searchGivers: async (searchParams, options = {}) => {
      const {
        showLoading = true,
        onSuccess = null,
        onError = null
      } = options;
      
      const cacheKey = `search_${JSON.stringify(searchParams)}`;
      
      // 檢查快取
      if (DOM.dataLoader.isCached(cacheKey)) {
        const cachedData = DOM.dataLoader.getCached(cacheKey);
        console.log('DOM.dataLoader.searchGivers: 使用快取的搜尋結果');
        if (onSuccess) onSuccess(cachedData);
        return cachedData;
      }
      
      // 顯示載入狀態
      if (showLoading) {
        DOM.dataLoader.showLoading();
      }
      
      try {
        console.log('DOM.dataLoader.searchGivers: 搜尋 Giver 資料:', searchParams);
        
        const response = await DOM.dataLoader.makeRequest(cacheKey, {
          method: 'GET',
          url: DOM.dataLoader.config.baseURL,
          params: searchParams
        });
        
        const searchResults = response.data.results || [];
        console.log('DOM.dataLoader.searchGivers: 搜尋結果:', searchResults.length, '筆資料');
        
        // 快取資料
        DOM.dataLoader.cacheData(cacheKey, searchResults);
        
        if (onSuccess) onSuccess(searchResults);
        return searchResults;
        
      } catch (error) {
        console.error('DOM.dataLoader.searchGivers: 搜尋失敗:', error);
        if (onError) onError(error);
        throw error;
        
      } finally {
        if (showLoading) {
          DOM.dataLoader.hideLoading();
        }
      }
    },
    
    // 發送 HTTP 請求
    makeRequest: async (cacheKey, requestConfig) => {
      console.log('DOM.dataLoader.makeRequest called：發送 HTTP 請求', { cacheKey, requestConfig });
      const config = {
        timeout: DOM.dataLoader.config.timeout,
        ...requestConfig
      };
      
      try {
        const response = await axios(config);
        return response;
        
      } catch (error) {
        // 重試邏輯
        if (DOM.dataLoader.state.retryCount < DOM.dataLoader.config.maxRetries) {
          DOM.dataLoader.state.retryCount++;
          console.log(`DOM.dataLoader.makeRequest: 請求失敗，重試第 ${DOM.dataLoader.state.retryCount} 次`);
          
          await new Promise(resolve => 
            setTimeout(resolve, DOM.dataLoader.config.retryDelay * DOM.dataLoader.state.retryCount)
          );
          
          return DOM.dataLoader.makeRequest(cacheKey, requestConfig);
        }
        
        throw error;
      }
    },
    
    // 錯誤處理
    handleError: (error, retryCallback) => {
      console.error('DOM.dataLoader.handleError: 資料載入錯誤:', error);
      
      // 顯示錯誤訊息
      DOM.dataLoader.showError(error.message || '資料載入失敗');
      
      // 如果還有重試次數，自動重試
      if (DOM.dataLoader.state.retryCount < DOM.dataLoader.config.maxRetries) {
        setTimeout(retryCallback, DOM.dataLoader.config.retryDelay);
      }
    },
    
    // 快取管理
    cacheData: (key, data) => {
      const cacheItem = {
        data,
        timestamp: Date.now(),
        expiry: Date.now() + DOM.dataLoader.config.cacheExpiry
      };
      
      DOM.dataLoader.state.cache.set(key, cacheItem);
      console.log('DOM.dataLoader.cacheData: 資料已快取:', key);
    },
    
    // 從快取中獲取資料，如果資料存在且未過期則返回資料，否則返回 null
    getCached: (key) => {
      const cacheItem = DOM.dataLoader.state.cache.get(key);
      if (cacheItem && Date.now() < cacheItem.expiry) {
        return cacheItem.data;
      }
      
      // 過期資料，從快取中移除
      DOM.dataLoader.state.cache.delete(key);
      return null;
    },
    
    // 檢查指定鍵值的資料是否存在於快取中且未過期
    isCached: (key) => {
      return DOM.dataLoader.getCached(key) !== null;
    },
    
    // 清除指定鍵值的資料或清除所有快取
    clearCache: (key = null) => {
      if (key) {
        DOM.dataLoader.state.cache.delete(key);
        console.log('DOM.dataLoader.clearCache: 清除快取:', key);
      } else {
        DOM.dataLoader.state.cache.clear();
        console.log('DOM.dataLoader.clearCache: 清除所有快取');
      }
    },
    
    // 載入狀態 UI
    showLoading: () => {
      console.log('DOM.dataLoader.showLoading called：顯示載入指示器');
      // 創建載入指示器
      const loadingIndicator = DOM.createElement('div', 'loading-indicator', `
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
        <p class="mt-2">載入資料中...</p>
      `);
      
      document.body.appendChild(loadingIndicator);
      DOM.dataLoader.state.loadingElement = loadingIndicator;
    },
    
    // 隱藏載入指示器
    hideLoading: () => {
      console.log('DOM.dataLoader.hideLoading called：隱藏載入指示器');
      if (DOM.dataLoader.state.loadingElement) {
        DOM.dataLoader.state.loadingElement.remove();
        DOM.dataLoader.state.loadingElement = null;
      }
    },
    
    // 顯示錯誤訊息
    showError: (message) => {
      console.log('DOM.dataLoader.showError called：顯示錯誤訊息', { message });
      // 創建錯誤訊息
      const errorElement = DOM.createElement('div', 'error-message', `
        <div class="alert alert-danger" role="alert">
          <i class="fas fa-exclamation-triangle me-2"></i>
          ${message}
          <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
      `);
      
      document.body.appendChild(errorElement);
      
      // 自動移除錯誤訊息
      setTimeout(() => {
        if (errorElement.parentNode) {
          errorElement.remove();
        }
      }, 5000);
    },
    
    // 資料載入工具
    utils: {
      // 獲取載入統計
      getStats: () => {
        console.log('DOM.dataLoader.utils.getStats called：獲取載入統計');
        return {
          isLoading: DOM.dataLoader.state.isLoading,
          lastLoadTime: DOM.dataLoader.state.lastLoadTime,
          loadCount: DOM.dataLoader.state.loadCount,
          errorCount: DOM.dataLoader.state.errorCount,
          retryCount: DOM.dataLoader.state.retryCount,
          cacheSize: DOM.dataLoader.state.cache.size
        };
      },
      
      // 檢查網路狀態
      checkNetworkStatus: () => {
        console.log('DOM.dataLoader.utils.checkNetworkStatus called：檢查網路狀態');
        return navigator.onLine;
      },
      
      // 預載入資料
      preloadData: async (dataTypes = ['givers']) => {
        console.log('DOM.dataLoader.utils.preloadData called：預載入資料', { dataTypes });
        
        const promises = dataTypes.map(type => {
          switch (type) {
            case 'givers':
              return DOM.dataLoader.loadGivers({ showLoading: false });
            default:
              return Promise.resolve();
          }
        });
        
        try {
          await Promise.all(promises);
          console.log('DOM.dataLoader.utils.preloadData: 資料預載入完成');
        } catch (error) {
          console.error('DOM.dataLoader.utils.preloadData: 資料預載入失敗:', error);
        }
      },
      
      // 清理過期快取
      cleanupExpiredCache: () => {
        console.log('DOM.dataLoader.utils.cleanupExpiredCache called：清理過期快取');
        const now = Date.now();
        let cleanedCount = 0;
        
        for (const [key, item] of DOM.dataLoader.state.cache) {
          if (now > item.expiry) {
            DOM.dataLoader.state.cache.delete(key);
            cleanedCount++;
          }
        }
        
        if (cleanedCount > 0) {
          console.log(`DOM.dataLoader.utils.cleanupExpiredCache: 清理了 ${cleanedCount} 個過期快取項目`);
        }
      },
      
      // 調試資料載入功能
      debug: () => {
        console.group('DOM.dataLoader.utils.debug called：資料載入調試資訊');
        console.log('DOM.dataLoader.utils.debug: 載入狀態:', DOM.dataLoader.state);
        console.log('DOM.dataLoader.utils.debug: 載入統計:', DOM.dataLoader.utils.getStats());
        console.log('DOM.dataLoader.utils.debug: 網路狀態:', DOM.dataLoader.utils.checkNetworkStatus());
        console.log('DOM.dataLoader.utils.debug: 快取項目:', Array.from(DOM.dataLoader.state.cache.keys()));
        console.groupEnd();
      }
    }
  },
  
  // Giver 相關功能
  giver: {
    // 渲染 Giver 列表
    renderGiverList: (givers) => {
      console.log('DOM.giver.renderGiverList called：渲染 Giver 列表', { givers });
      
      const giverPanel = DOM.getElement(CONFIG.SELECTORS.GIVER_PANEL);
      if (!giverPanel) {
        console.error('DOM.giver.renderGiverList: Giver 面板元素未找到:', CONFIG.SELECTORS.GIVER_PANEL);
        return;
      }
      
      // 清空面板
      giverPanel.innerHTML = '';
      
      // 檢查是否有資料
      if (!givers || givers.length === 0) {
        giverPanel.innerHTML = TEMPLATES.noDataMessage();
        return;
      }
      
      // 渲染每個 Giver 卡片
      const giverCardsHTML = givers.map(giver => {
        const cardHTML = TEMPLATES.giverCard(giver);
        // 使用 TEMPLATES 中的包裝器模板
        return TEMPLATES.giverCardWrapper(cardHTML);
      }).join('');
      giverPanel.innerHTML = giverCardsHTML;
      
      // 設定卡片點擊事件
      DOM.giver.setupCardEvents();
      
      // 檢查服務項目是否超出範圍
      DOM.giver.checkAllTopicsOverflow();
      
      console.log('DOM.giver.renderGiverList: Giver 列表渲染完成:', givers.length, '筆資料');
    },
    
    // 設定卡片事件
    setupCardEvents: () => {
      console.log('DOM.giver.setupCardEvents called：設定卡片事件');
      // 移除原本為卡片設定的點擊事件，只保留按鈕事件
      
      // 設定諮詢按鈕事件
      const actionButtons = DOM.getElements(`.${CONFIG.CLASSES.GIVER_CARD_ACTION_BUTTON}`);
      actionButtons.forEach(button => {
        DOM.events.add(button, 'click', (e) => {
          e.preventDefault();
          e.stopPropagation(); // 防止事件冒泡
          
          const giverId = button.dataset.id;
          const giver = appState.givers.find(g => g.id == giverId);
          
          if (giver) {
            // 呼叫 UIInteraction 開啟聊天對話框
            UIInteraction.openChatDialog(giver);
          }
        });
      });
    },

    // 檢查所有卡片的服務項目是否超出容器，並處理溢出
    checkAllTopicsOverflow: () => {
      const topicContainers = DOM.getElements(`.${CONFIG.CLASSES.GIVER_CARD_TOPIC}`);
      
      topicContainers.forEach(container => {
        const buttons = Array.from(container.querySelectorAll(`.${CONFIG.CLASSES.GIVER_CARD_TOPIC_BUTTON}`));
        const chevron = container.querySelector('.fa-chevron-right');

        if (!chevron || buttons.length === 0) return;

        // 1. 重設狀態，以便正確測量
        buttons.forEach(btn => {
          btn.classList.remove('btn-hidden');
          btn.classList.add('btn-visible');
        });
        chevron.classList.remove('inline');
        chevron.classList.add('hidden');
        container.classList.remove('flex-wrap');
        container.classList.add('flex-nowrap');

        // 2. 延遲執行以等待 DOM 更新
        setTimeout(() => {
          const containerWidth = container.clientWidth;

          // 如果沒有溢出，則恢復並跳出
          if (container.scrollWidth <= containerWidth) {
            chevron.classList.remove('inline');
            chevron.classList.add('hidden');
            container.classList.remove('flex-nowrap');
            container.classList.add('flex-wrap');
            return;
          }

          // 如果確定溢出，則顯示箭頭並計算可用空間
          chevron.classList.remove('hidden');
          chevron.classList.add('inline');
          const chevronWidth = chevron.offsetWidth;
          const gap = 8; // 根據 CSS --spacing-sm 變數設定
          const availableWidth = containerWidth - chevronWidth;
          let accumulatedWidth = 0;

          for (const btn of buttons) {
            const btnWidthWithGap = btn.offsetWidth + gap;
            if (accumulatedWidth + btnWidthWithGap > availableWidth) {
              btn.classList.remove('btn-visible');
              btn.classList.add('btn-hidden'); // 隱藏放不下的按鈕
            } else {
              accumulatedWidth += btnWidthWithGap;
              btn.classList.remove('btn-hidden');
              btn.classList.add('btn-visible'); // 確保按鈕可見
            }
          }

          // 3. 恢復容器的換行屬性
          container.classList.remove('flex-nowrap');
          container.classList.add('flex-wrap');
        }, 0);
      });
    }
  },
  
  // 分頁相關功能
  pagination: {
    // 根據頁碼取得該頁的 Giver 資料
    getGiversByPage: (page) => {
      console.log('DOM.pagination.getGiversByPage called：取得第', page, '頁的 Giver 資料');
      
      if (!appState.givers || appState.givers.length === 0) {
        console.warn('沒有 Giver 資料');
        return [];
      }
      
      const startIndex = (page - 1) * CONFIG.PAGINATION.GIVERS_PER_PAGE;
      const endIndex = startIndex + CONFIG.PAGINATION.GIVERS_PER_PAGE;
      const pageGivers = appState.givers.slice(startIndex, endIndex);
      
      console.log('DOM.pagination.getGiversByPage: 第', page, '頁資料:', pageGivers.length, '筆');
      return pageGivers;
    },
    
    // 渲染分頁器
    renderPaginator: (totalCount) => {
      console.log('DOM.pagination.renderPaginator called：渲染分頁器，總數:', totalCount);
      
      const paginator = DOM.getElement(CONFIG.SELECTORS.PAGINATOR);
      if (!paginator) {
        console.error('DOM.pagination.renderPaginator: 分頁器元素未找到:', CONFIG.SELECTORS.PAGINATOR);
        return;
      }
      
      const totalPages = Math.ceil(totalCount / CONFIG.PAGINATION.GIVERS_PER_PAGE);
      
      if (totalPages <= 1) {
        paginator.innerHTML = '';
        return;
      }
      
      // 生成分頁 HTML
      let paginatorHTML = TEMPLATES.paginator.container();
      
      // 上一頁按鈕
      paginatorHTML += TEMPLATES.paginator.prevButton();
      
      // 頁碼按鈕
      const currentPage = appState.currentPage || 1;
      const maxPagesToShow = CONFIG.PAGINATION.MAX_PAGES_DISPLAY;
      
      let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
      let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);
      
      // 調整起始頁碼
      if (endPage - startPage + 1 < maxPagesToShow) {
        startPage = Math.max(1, endPage - maxPagesToShow + 1);
      }
      
      // 第一頁
      if (startPage > 1) {
        paginatorHTML += TEMPLATES.paginator.item(1);
        if (startPage > 2) {
          paginatorHTML += TEMPLATES.paginator.ellipsis();
        }
      }
      
      // 頁碼
      for (let i = startPage; i <= endPage; i++) {
        const isActive = i === currentPage;
        paginatorHTML += TEMPLATES.paginator.pageNumber(i, isActive);
      }
      
      // 最後一頁
      if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
          paginatorHTML += TEMPLATES.paginator.ellipsis();
        }
        paginatorHTML += TEMPLATES.paginator.item(totalPages);
      }
      
      // 下一頁按鈕
      paginatorHTML += TEMPLATES.paginator.nextButton();
      
      paginatorHTML += '</ul>';
      paginator.innerHTML = paginatorHTML;
      
      // 設定分頁事件
      DOM.pagination.setupPaginatorEvents();
      
      console.log('DOM.pagination.renderPaginator: 分頁器渲染完成，總頁數:', totalPages);
    },
    
    // 設定分頁事件
    setupPaginatorEvents: () => {
      console.log('DOM.pagination.setupPaginatorEvents called：設定分頁事件');
      const paginator = DOM.getElement(CONFIG.SELECTORS.PAGINATOR);
      if (!paginator) return;
      
      const pageLinks = paginator.querySelectorAll(`.${CONFIG.CLASSES.PAGINATOR_LINK}`);
      
      pageLinks.forEach(link => {
        DOM.events.add(link, 'click', (e) => {
          e.preventDefault();
          
          const page = link.dataset.page;
          const currentPage = appState.currentPage || 1;
          const totalPages = Math.ceil((appState.givers || []).length / CONFIG.PAGINATION.GIVERS_PER_PAGE);
          
          let targetPage = currentPage;
          
          if (page === 'prev') {
            targetPage = Math.max(1, currentPage - 1);
          } else if (page === 'next') {
            targetPage = Math.min(totalPages, currentPage + 1);
          } else {
            targetPage = parseInt(page);
          }
          
          if (targetPage !== currentPage && targetPage >= 1 && targetPage <= totalPages) {
            console.log('DOM.pagination.setupPaginatorEvents: 切換到第', targetPage, '頁');
            DOM.pagination.goToPage(targetPage);
          }
        });
      });
    },
    
    // 切換到指定頁面
    goToPage: (page) => {
      console.log('DOM.pagination.goToPage called：切換到第', page, '頁');
      
      // 更新當前頁面
      appState.currentPage = page;
      
      // 取得該頁資料
      const pageGivers = DOM.pagination.getGiversByPage(page);
      
      // 重新渲染列表
      DOM.giver.renderGiverList(pageGivers);
      
      // 重新渲染分頁器
      DOM.pagination.renderPaginator(appState.givers.length);
      
      // 滾動到頂部
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }
};

// =================================================================
//   全域函式 (Global Functions) - 為了向後相容
// =================================================================

// 為了向後相容，保留舊的函式引用
const renderPaginator = DOM.pagination.renderPaginator;
const getGiversByPage = DOM.pagination.getGiversByPage;
const renderGiverList = DOM.giver.renderGiverList;
const checkTopicOverflow = DOM.utils.checkTopicOverflow;
const scrollToBottom = DOM.utils.scrollToBottom;
const cleanupModal = DOM.utils.cleanupModal;
const openChatDialog = UIInteraction.openChatDialog;
const showConfirmDialog = UIInteraction.showConfirmDialog;

// =================================================================
//   錯誤型別常數 (Error Types Constants)
// =================================================================

const ERROR_TYPES = {
  NETWORK: 'NETWORK_ERROR',
  VALIDATION: 'VALIDATION_ERROR',
  DOM: 'DOM_ERROR',
  BUSINESS: 'BUSINESS_ERROR',
  UNKNOWN: 'UNKNOWN_ERROR'
};

// =================================================================
//   錯誤處理器 (Error Handlers)
// =================================================================

const errorHandlers = {
  [ERROR_TYPES.NETWORK]: (error) => {
    console.error('DOM.errorHandler.handle: 網路錯誤:', error);
    return {
      type: ERROR_TYPES.NETWORK,
      message: CONFIG.MESSAGES.ERROR.NETWORK,
      originalError: error,
      timestamp: new Date(),
      retryable: true
    };
  },
  [ERROR_TYPES.VALIDATION]: (error) => {
    console.error('DOM.errorHandler.handle: 驗證錯誤:', error);
    return {
      type: ERROR_TYPES.VALIDATION,
      message: CONFIG.MESSAGES.ERROR.VALIDATION,
      originalError: error,
      timestamp: new Date(),
      retryable: false
    };
  },
  [ERROR_TYPES.DOM]: (error) => {
    console.error('DOM.errorHandler.handle: DOM 錯誤:', error);
    return {
      type: ERROR_TYPES.DOM,
      message: 'DOM 操作失敗',
      originalError: error,
      timestamp: new Date(),
      retryable: false
    };
  },
  [ERROR_TYPES.BUSINESS]: (error) => {
    console.error('DOM.errorHandler.handle: 業務邏輯錯誤:', error);
    return {
      type: ERROR_TYPES.BUSINESS,
      message: error.message || '業務邏輯錯誤',
      originalError: error,
      timestamp: new Date(),
      retryable: false
    };
  },
  [ERROR_TYPES.UNKNOWN]: (error) => {
    console.error('DOM.errorHandler.handle: 未知錯誤:', error);
    return {
      type: ERROR_TYPES.UNKNOWN,
      message: CONFIG.MESSAGES.ERROR.UNKNOWN,
      originalError: error,
      timestamp: new Date(),
      retryable: false
    };
  }
};

// =================================================================
//   錯誤處理模組 (Error Handling Module)
// =================================================================

const ErrorHandler = {
  ERROR_TYPES,
  handlers: errorHandlers,

  // 錯誤歷史記錄
  errorHistory: [],

  // 處理錯誤
  handle: (error, type = ERROR_TYPES.UNKNOWN, context = {}) => {
    console.log('ErrorHandler.handle called: 處理錯誤', { error, type, context });
    const handler = ErrorHandler.handlers[type];
    if (!handler) {
      console.error('DOM.errorHandler.handle: 未找到錯誤處理器:', type);
      return ErrorHandler.handlers[ERROR_TYPES.UNKNOWN](error);
    }

    const processedError = handler(error);
    processedError.context = context;

    // 記錄錯誤歷史
    ErrorHandler.errorHistory.push(processedError);

    // 限制錯誤歷史記錄數量
    if (ErrorHandler.errorHistory.length > 100) {
      ErrorHandler.errorHistory = ErrorHandler.errorHistory.slice(-50);
    }

    return processedError;
  },

  // 顯示錯誤訊息
  showError: (error, options = {}) => {
    console.log('ErrorHandler.showError called: 顯示錯誤訊息', { error, options });
    const {
      duration = CONFIG.UI.ERROR_DISPLAY_TIME,
      showNotification = true,
      logToConsole = true
    } = options;

    if (logToConsole) {
      console.error('DOM.errorHandler.showError: 顯示錯誤:', error);
    }

    if (showNotification) {
      // 創建錯誤通知元素
      const errorElement = DOM.createElement('div', 'error-notification', `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
          <i class="fas fa-exclamation-triangle me-2"></i>
          ${error.message || CONFIG.MESSAGES.ERROR.UNKNOWN}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
      `);

      // 添加到頁面
      document.body.appendChild(errorElement);

      // 自動移除
      setTimeout(() => {
        if (errorElement.parentNode) {
          errorElement.remove();
        }
      }, duration);
    }
  },

  // 顯示成功訊息
  showSuccess: (message, options = {}) => {
    console.log('ErrorHandler.showSuccess called: 顯示成功訊息', { message, options });
    const {
      duration = CONFIG.UI.ERROR_DISPLAY_TIME,
      showNotification = true
    } = options;

    if (showNotification) {
      const successElement = DOM.createElement('div', 'success-notification', `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          <i class="fas fa-check-circle me-2"></i>
          ${message}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
      `);

      document.body.appendChild(successElement);

      setTimeout(() => {
        if (successElement.parentNode) {
          successElement.remove();
        }
      }, duration);
    }
  },

  // 顯示資訊訊息
  showInfo: (message, options = {}) => {
    console.log('ErrorHandler.showInfo called: 顯示資訊訊息', { message, options });
    const {
      duration = CONFIG.UI.ERROR_DISPLAY_TIME,
      showNotification = true
    } = options;

    if (showNotification) {
      const infoElement = DOM.createElement('div', 'info-notification', `
        <div class="alert alert-info alert-dismissible fade show" role="alert">
          <i class="fas fa-info-circle me-2"></i>
          ${message}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
      `);

      document.body.appendChild(infoElement);

      setTimeout(() => {
        if (infoElement.parentNode) {
          infoElement.remove();
        }
      }, duration);
    }
  },

  // 工具方法
  utils: {
    // 獲取錯誤統計
    getStats: () => {
      console.log('ErrorHandler.utils.getStats called: 獲取錯誤統計');
      const stats = {
        total: ErrorHandler.errorHistory.length,
        byType: {},
        byTime: {
          lastHour: 0,
          lastDay: 0,
          lastWeek: 0
        }
      };

      const now = new Date();
      const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
      const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

      ErrorHandler.errorHistory.forEach(error => {
        // 按類型統計
        stats.byType[error.type] = (stats.byType[error.type] || 0) + 1;

        // 按時間統計
        if (error.timestamp > oneHourAgo) {
          stats.byTime.lastHour++;
        }
        if (error.timestamp > oneDayAgo) {
          stats.byTime.lastDay++;
        }
        if (error.timestamp > oneWeekAgo) {
          stats.byTime.lastWeek++;
        }
      });

      return stats;
    },

    // 清理錯誤歷史
    clearHistory: () => {
      console.log('ErrorHandler.utils.clearHistory called: 清理錯誤歷史');
      ErrorHandler.errorHistory = [];
    },

    // 獲取最近的錯誤
    getRecentErrors: (count = 10) => {
      console.log('ErrorHandler.utils.getRecentErrors called: 獲取最近的錯誤', { count });
      return ErrorHandler.errorHistory.slice(-count);
    },

    // 檢查是否有特定類型的錯誤
    hasErrorType: (type) => {
      console.log('ErrorHandler.utils.hasErrorType called: 檢查是否有特定類型的錯誤', { type });
      return ErrorHandler.errorHistory.some(error => error.type === type);
    },

    // 調試錯誤處理器
    debug: () => {
      console.group('DOM.errorHandler.utils.debug called：錯誤處理器調試資訊');
      console.log('DOM.errorHandler.utils.debug: 錯誤歷史:', ErrorHandler.errorHistory);
      console.log('DOM.errorHandler.utils.debug: 錯誤統計:', ErrorHandler.utils.getStats());
      console.log('DOM.errorHandler.utils.debug: 最近的錯誤:', ErrorHandler.utils.getRecentErrors());
      console.groupEnd();
    }
  }
};

// =================================================================
//   日誌級別常數 (Logger Level Constants)
// =================================================================

const LOGGER_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  FATAL: 4
};
const LOGGER_LEVEL_NAMES = {
  0: 'DEBUG',
  1: 'INFO',
  2: 'WARN',
  3: 'ERROR',
  4: 'FATAL'
};

// =================================================================
//   日誌記錄模組 (Logging Module)
// =================================================================

const Logger = {
  LEVELS: LOGGER_LEVELS,
  LEVEL_NAMES: LOGGER_LEVEL_NAMES,

  // 配置
  config: {
    level: LOGGER_LEVELS.INFO,
    enableConsole: true,
    enableStorage: false,
    maxLogs: 1000,
    storageKey: 'app_logs'
  },

  // 日誌記錄
  logs: [],

  // 記錄日誌
  log: (level, message, data = null, context = {}) => {
    console.log('Logger.log called: 記錄日誌', { level, message, data, context });
    if (level < Logger.config.level) {
      return;
    }

    const logEntry = {
      level,
      levelName: Logger.LEVEL_NAMES[level],
      message,
      data,
      context,
      timestamp: new Date(),
      timestampISO: new Date().toISOString()
    };

    // 添加到日誌記錄
    Logger.logs.push(logEntry);

    // 限制日誌數量
    if (Logger.logs.length > Logger.config.maxLogs) {
      Logger.logs = Logger.logs.slice(-Logger.config.maxLogs / 2);
    }

    // 控制台輸出
    if (Logger.config.enableConsole) {
      const consoleMethod = Logger.getConsoleMethod(level);
      const prefix = `[${logEntry.levelName}] ${DateUtils.formatToLocalTime(logEntry.timestamp)}`;
      
      if (data) {
        console[consoleMethod](prefix, message, data);
      } else {
        console[consoleMethod](prefix, message);
      }
    }

    // 儲存到本地儲存
    if (Logger.config.enableStorage) {
      Logger.saveToStorage(logEntry);
    }

    return logEntry;
  },

  // 獲取控制台方法
  getConsoleMethod: (level) => {
    console.log('DOM.Logger.getConsoleMethod called：獲取控制台方法', { level });
    switch (level) {
      case LOGGER_LEVELS.DEBUG:
        return 'debug';
      case LOGGER_LEVELS.INFO:
        return 'info';
      case LOGGER_LEVELS.WARN:
        return 'warn';
      case LOGGER_LEVELS.ERROR:
      case LOGGER_LEVELS.FATAL:
        return 'error';
      default:
        return 'log';
    }
  },

  // 儲存到本地儲存
  saveToStorage: (logEntry) => {
    console.log('DOM.Logger.saveToStorage called：儲存到本地儲存', { logEntry });
    try {
      const existingLogs = JSON.parse(localStorage.getItem(Logger.config.storageKey) || '[]');
      existingLogs.push(logEntry);
      
      // 限制儲存的日誌數量
      if (existingLogs.length > Logger.config.maxLogs) {
        existingLogs.splice(0, existingLogs.length - Logger.config.maxLogs);
      }
      
      localStorage.setItem(Logger.config.storageKey, JSON.stringify(existingLogs));
    } catch (error) {
      console.error('DOM.Logger.saveToStorage: 儲存日誌失敗:', error);
    }
  },

  // 便捷方法
  debug: (message, data = null, context = {}) => {
    console.log('Logger.debug called: 記錄 DEBUG 日誌', { message, data, context });
    return Logger.log(LOGGER_LEVELS.DEBUG, message, data, context);
  },

  info: (message, data = null, context = {}) => {
    console.log('Logger.info called: 記錄 INFO 日誌', { message, data, context });
    return Logger.log(LOGGER_LEVELS.INFO, message, data, context);
  },

  warn: (message, data = null, context = {}) => {
    console.log('Logger.warn called: 記錄 WARN 日誌', { message, data, context });
    return Logger.log(LOGGER_LEVELS.WARN, message, data, context);
  },

  error: (message, data = null, context = {}) => {
    console.log('Logger.error called: 記錄 ERROR 日誌', { message, data, context });
    return Logger.log(LOGGER_LEVELS.ERROR, message, data, context);
  },

  fatal: (message, data = null, context = {}) => {
    console.log('Logger.fatal called: 記錄 FATAL 日誌', { message, data, context });
    return Logger.log(LOGGER_LEVELS.FATAL, message, data, context);
  },

  // 工具方法
  utils: {
    // 獲取日誌統計
    getStats: () => {
      console.log('DOM.Logger.utils.getStats called：獲取日誌統計');
      const stats = {
        total: Logger.logs.length,
        byLevel: {},
        byTime: {
          lastHour: 0,
          lastDay: 0,
          lastWeek: 0
        }
      };

      const now = new Date();
      const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
      const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

      Logger.logs.forEach(log => {
        // 按級別統計
        stats.byLevel[log.levelName] = (stats.byLevel[log.levelName] || 0) + 1;

        // 按時間統計
        if (log.timestamp > oneHourAgo) {
          stats.byTime.lastHour++;
        }
        if (log.timestamp > oneDayAgo) {
          stats.byTime.lastDay++;
        }
        if (log.timestamp > oneWeekAgo) {
          stats.byTime.lastWeek++;
        }
      });

      return stats;
    },

    // 清理日誌
    clear: () => {
      console.log('DOM.Logger.utils.clear called：清空日誌');
      Logger.logs = [];
    },

    // 獲取最近的日誌
    getRecent: (count = 50, level = null) => {
      console.log('DOM.Logger.utils.getRecent called：獲取最近的日誌', { count, level });
      let filteredLogs = Logger.logs;
      
      if (level !== null) {
        filteredLogs = Logger.logs.filter(log => log.level >= level);
      }
      
      return filteredLogs.slice(-count);
    },

    // 搜尋日誌
    search: (query, options = {}) => {
      console.log('DOM.Logger.utils.search called：搜尋日誌', { query, options });
      const {
        level = null,
        startTime = null,
        endTime = null,
        caseSensitive = false
      } = options;

      let filteredLogs = Logger.logs;

      // 按級別過濾
      if (level !== null) {
        filteredLogs = filteredLogs.filter(log => log.level >= level);
      }

      // 按時間過濾
      if (startTime) {
        filteredLogs = filteredLogs.filter(log => log.timestamp >= startTime);
      }
      if (endTime) {
        filteredLogs = filteredLogs.filter(log => log.timestamp <= endTime);
      }

      // 按查詢字串過濾
      if (query) {
        const searchQuery = caseSensitive ? query : query.toLowerCase();
        filteredLogs = filteredLogs.filter(log => {
          const message = caseSensitive ? log.message : log.message.toLowerCase();
          return message.includes(searchQuery);
        });
      }

      return filteredLogs;
    },

    // 匯出日誌
    export: (format = 'json') => {
      console.log('DOM.Logger.utils.export called：匯出日誌', { format });
      switch (format.toLowerCase()) {
        case 'json':
          return JSON.stringify(Logger.logs, null, 2);
        case 'csv':
          const csvHeader = 'Level,Message,Timestamp,Data\n';
          const csvRows = Logger.logs.map(log => 
            `"${log.levelName}","${log.message.replace(/"/g, '""')}","${log.timestampISO}","${JSON.stringify(log.data).replace(/"/g, '""')}"`
          ).join('\n');
          return csvHeader + csvRows;
        default:
          throw new Error(`不支援的匯出格式: ${format}`);
      }
    },

    // 設定日誌級別
    setLevel: (level) => {
      console.log('DOM.Logger.setLevel called：設定日誌級別', { level });
      if (Object.values(LOGGER_LEVELS).includes(level)) {
        Logger.config.level = level;
        Logger.info(`日誌級別已設定為: ${LOGGER_LEVEL_NAMES[level]}`);
      } else {
        Logger.warn(`無效的日誌級別: ${level}`);
      }
    },

    // 啟用/停用控制台輸出
    setConsoleOutput: (enabled) => {
      console.log('DOM.Logger.setConsoleOutput called：設定控制台輸出', { enabled });
      Logger.config.enableConsole = enabled;
      Logger.info(`控制台輸出已${enabled ? '啟用' : '停用'}`);
    },

    // 啟用/停用本地儲存
    setStorage: (enabled) => {
      console.log('DOM.Logger.setStorage called：設定本地儲存', { enabled });
      Logger.config.enableStorage = enabled;
      Logger.info(`本地儲存已${enabled ? '啟用' : '停用'}`);
    },

    // 調試日誌系統
    debug: () => {
      console.group('DOM.Logger.utils.debug called：日誌系統調試資訊');
      console.log('DOM.Logger.utils.debug: 配置:', Logger.config);
      console.log('DOM.Logger.utils.debug: 統計:', Logger.utils.getStats());
      console.log('DOM.Logger.utils.debug: 最近的日誌:', Logger.utils.getRecent(10));
      console.groupEnd();
    }
  }
};

// =================================================================
//   效能監控模組 (Performance Monitoring Module)
// =================================================================

const PerformanceMonitor = {
  // 效能指標
  metrics: {
    pageLoad: null,
    apiCalls: [],
    domOperations: [],
    memoryUsage: [],
    errors: []
  },

  // 配置
  config: {
    enableMonitoring: true,
    enableMemoryTracking: true,
    enableAPITracking: true,
    enableDOMTracking: true,
    maxMetricsCount: 100,
    reportInterval: 60000 // 1分鐘
  },

  // 計時器
  timers: new Map(),

  // 開始計時
  startTimer: (name) => {
    console.log('DOM.PerformanceMonitor.startTimer called：開始計時', { name });
    if (!PerformanceMonitor.config.enableMonitoring) return;
    
    PerformanceMonitor.timers.set(name, {
      start: performance.now(),
      name
    });
    
    Logger.debug(`開始計時: ${name}`);
  },

  // 結束計時
  endTimer: (name, context = {}) => {
    console.log('DOM.PerformanceMonitor.endTimer called：結束計時', { name, context });
    if (!PerformanceMonitor.config.enableMonitoring) return;
    
    const timer = PerformanceMonitor.timers.get(name);
    if (!timer) {
      Logger.warn(`找不到計時器: ${name}`);
      return;
    }

    const duration = performance.now() - timer.start;
    const metric = {
      name,
      duration,
      timestamp: new Date(),
      context
    };

    // 根據計時器類型分類儲存
    if (name.startsWith('api_')) {
      PerformanceMonitor.metrics.apiCalls.push(metric);
      if (PerformanceMonitor.metrics.apiCalls.length > PerformanceMonitor.config.maxMetricsCount) {
        PerformanceMonitor.metrics.apiCalls = PerformanceMonitor.metrics.apiCalls.slice(-PerformanceMonitor.config.maxMetricsCount / 2);
      }
    } else if (name.startsWith('dom_')) {
      PerformanceMonitor.metrics.domOperations.push(metric);
      if (PerformanceMonitor.metrics.domOperations.length > PerformanceMonitor.config.maxMetricsCount) {
        PerformanceMonitor.metrics.domOperations = PerformanceMonitor.metrics.domOperations.slice(-PerformanceMonitor.config.maxMetricsCount / 2);
      }
    }

    PerformanceMonitor.timers.delete(name);
    Logger.debug(`結束計時: ${name} (${duration.toFixed(2)}ms)`);
    
    return metric;
  },

  // 測量函數執行時間
  measure: async (name, fn, context = {}) => {
    console.log('DOM.PerformanceMonitor.measure called：測量函數執行時間', { name, context });
    PerformanceMonitor.startTimer(name);
    
    try {
      const result = await fn();
      PerformanceMonitor.endTimer(name, { ...context, success: true });
      return result;
    } catch (error) {
      PerformanceMonitor.endTimer(name, { ...context, success: false, error: error.message });
      throw error;
    }
  },

  // 同步測量函數執行時間
  measureSync: (name, fn, context = {}) => {
    console.log('DOM.PerformanceMonitor.measureSync called：同步測量函數執行時間', { name, context });
    PerformanceMonitor.startTimer(name);
    
    try {
      const result = fn();
      PerformanceMonitor.endTimer(name, { ...context, success: true });
      return result;
    } catch (error) {
      PerformanceMonitor.endTimer(name, { ...context, success: false, error: error.message });
      throw error;
    }
  },

  // 記錄記憶體使用
  recordMemoryUsage: () => {
    console.log('DOM.PerformanceMonitor.recordMemoryUsage called：記錄記憶體使用');
    if (!PerformanceMonitor.config.enableMemoryTracking || !performance.memory) return;
    
    const memoryInfo = {
      used: performance.memory.usedJSHeapSize,
      total: performance.memory.totalJSHeapSize,
      limit: performance.memory.jsHeapSizeLimit,
      timestamp: new Date()
    };

    PerformanceMonitor.metrics.memoryUsage.push(memoryInfo);
    
    if (PerformanceMonitor.metrics.memoryUsage.length > PerformanceMonitor.config.maxMetricsCount) {
      PerformanceMonitor.metrics.memoryUsage = PerformanceMonitor.metrics.memoryUsage.slice(-PerformanceMonitor.config.maxMetricsCount / 2);
    }
  },

  // 記錄錯誤
  recordError: (error, context = {}) => {
    console.log('DOM.PerformanceMonitor.recordError called：記錄錯誤', { error, context });
    const errorMetric = {
      message: error.message,
      stack: error.stack,
      timestamp: new Date(),
      context
    };

    PerformanceMonitor.metrics.errors.push(errorMetric);
    
    if (PerformanceMonitor.metrics.errors.length > PerformanceMonitor.config.maxMetricsCount) {
      PerformanceMonitor.metrics.errors = PerformanceMonitor.metrics.errors.slice(-PerformanceMonitor.config.maxMetricsCount / 2);
    }
  },

  // 獲取效能報告
  getReport: () => {
    console.log('DOM.PerformanceMonitor.getReport called：獲取效能報告');
    const report = {
      timestamp: new Date(),
      pageLoad: PerformanceMonitor.metrics.pageLoad,
      apiCalls: PerformanceMonitor.getAPICallStats(),
      domOperations: PerformanceMonitor.getDOMOperationStats(),
      memoryUsage: PerformanceMonitor.getMemoryStats(),
      errors: PerformanceMonitor.getErrorStats(),
      summary: PerformanceMonitor.getSummary()
    };

    return report;
  },

  // 獲取 API 呼叫統計
  getAPICallStats: () => {
    console.log('DOM.PerformanceMonitor.getAPICallStats called：獲取 API 呼叫統計');
    const calls = PerformanceMonitor.metrics.apiCalls;
    if (calls.length === 0) return null;

    const durations = calls.map(call => call.duration);
    const successful = calls.filter(call => call.context.success !== false);
    const failed = calls.filter(call => call.context.success === false);

    return {
      total: calls.length,
      successful: successful.length,
      failed: failed.length,
      averageDuration: durations.reduce((a, b) => a + b, 0) / durations.length,
      minDuration: Math.min(...durations),
      maxDuration: Math.max(...durations),
      recentCalls: calls.slice(-10)
    };
  },

  // 獲取 DOM 操作統計
  getDOMOperationStats: () => {
    console.log('DOM.PerformanceMonitor.getDOMOperationStats called：獲取 DOM 操作統計');
    const operations = PerformanceMonitor.metrics.domOperations;
    if (operations.length === 0) return null;

    const durations = operations.map(op => op.duration);

    return {
      total: operations.length,
      averageDuration: durations.reduce((a, b) => a + b, 0) / durations.length,
      minDuration: Math.min(...durations),
      maxDuration: Math.max(...durations),
      recentOperations: operations.slice(-10)
    };
  },

  // 獲取記憶體統計
  getMemoryStats: () => {
    console.log('DOM.PerformanceMonitor.getMemoryStats called：獲取記憶體統計');
    const usage = PerformanceMonitor.metrics.memoryUsage;
    if (usage.length === 0) return null;

    const latest = usage[usage.length - 1];
    const usedValues = usage.map(u => u.used);

    return {
      current: latest,
      averageUsed: usedValues.reduce((a, b) => a + b, 0) / usedValues.length,
      maxUsed: Math.max(...usedValues),
      minUsed: Math.min(...usedValues),
      usageHistory: usage.slice(-20)
    };
  },

  // 獲取錯誤統計
  getErrorStats: () => {
    console.log('DOM.PerformanceMonitor.getErrorStats called：獲取錯誤統計');
    const errors = PerformanceMonitor.metrics.errors;
    if (errors.length === 0) return null;

    const errorTypes = {};
    errors.forEach(error => {
      const type = error.message.split(':')[0] || 'Unknown';
      errorTypes[type] = (errorTypes[type] || 0) + 1;
    });

    return {
      total: errors.length,
      byType: errorTypes,
      recentErrors: errors.slice(-10)
    };
  },

  // 獲取摘要統計
  getSummary: () => {
    console.log('DOM.PerformanceMonitor.getSummary called：獲取摘要統計');
    const apiStats = PerformanceMonitor.getAPICallStats();
    const domStats = PerformanceMonitor.getDOMOperationStats();
    const memoryStats = PerformanceMonitor.getMemoryStats();
    const errorStats = PerformanceMonitor.getErrorStats();

    return {
      apiCalls: apiStats ? apiStats.total : 0,
      domOperations: domStats ? domStats.total : 0,
      errors: errorStats ? errorStats.total : 0,
      memoryUsage: memoryStats ? memoryStats.current.used : 0,
      performance: {
        api: apiStats ? apiStats.averageDuration : 0,
        dom: domStats ? domStats.averageDuration : 0
      }
    };
  },

  // 初始化效能監控
  init: () => {
    console.log('DOM.PerformanceMonitor.init called：初始化效能監控');
    if (!PerformanceMonitor.config.enableMonitoring) return;

    // 記錄頁面載入時間
    if (document.readyState === 'complete') {
      PerformanceMonitor.metrics.pageLoad = performance.now();
    } else {
      window.addEventListener('load', () => {
        PerformanceMonitor.metrics.pageLoad = performance.now();
        Logger.info('頁面載入完成', { loadTime: PerformanceMonitor.metrics.pageLoad });
      });
    }

    // 定期記錄記憶體使用
    if (PerformanceMonitor.config.enableMemoryTracking) {
      setInterval(() => {
        PerformanceMonitor.recordMemoryUsage();
      }, 30000); // 每30秒記錄一次
    }

    // 定期生成報告
    setInterval(() => {
      const report = PerformanceMonitor.getReport();
      Logger.info('效能監控報告', report.summary);
    }, PerformanceMonitor.config.reportInterval);

    Logger.info('效能監控已初始化');
  },

  // 工具方法
  utils: {
    // 清理舊的指標
    cleanup: () => {
      console.log('DOM.PerformanceMonitor.utils.cleanup called：清理舊的指標');
      PerformanceMonitor.metrics.apiCalls = [];
      PerformanceMonitor.metrics.domOperations = [];
      PerformanceMonitor.metrics.memoryUsage = [];
      PerformanceMonitor.metrics.errors = [];
      PerformanceMonitor.timers.clear();
      Logger.info('效能監控資料已清理');
    },

    // 啟用/停用監控
    setEnabled: (enabled) => {
      console.log('DOM.PerformanceMonitor.utils.setEnabled called：啟用/停用監控', { enabled });
      PerformanceMonitor.config.enableMonitoring = enabled;
      Logger.info(`效能監控已${enabled ? '啟用' : '停用'}`);
    },

    // 設定報告間隔
    setReportInterval: (interval) => {
      console.log('DOM.PerformanceMonitor.utils.setReportInterval called：設定報告間隔', { interval });
      PerformanceMonitor.config.reportInterval = interval;
      Logger.info(`效能監控報告間隔已設定為: ${interval}ms`);
    },

    // 匯出效能資料
    export: (format = 'json') => {
      console.log('DOM.PerformanceMonitor.utils.export called：匯出效能資料', { format });
      const report = PerformanceMonitor.getReport();
      
      switch (format.toLowerCase()) {
        case 'json':
          return JSON.stringify(report, null, 2);
        case 'csv':
          const csvRows = [];
          csvRows.push('Metric,Value,Unit');
          csvRows.push(`API Calls,${report.apiCalls?.total || 0},count`);
          csvRows.push(`DOM Operations,${report.domOperations?.total || 0},count`);
          csvRows.push(`Errors,${report.errors?.total || 0},count`);
          csvRows.push(`Memory Usage,${report.memoryUsage?.current?.used || 0},bytes`);
          return csvRows.join('\n');
        default:
          throw new Error(`不支援的匯出格式: ${format}`);
      }
    },

    // 調試效能監控
    debug: () => {
      console.group('DOM.PerformanceMonitor.utils.debug called：效能監控調試資訊');
      console.log('DOM.PerformanceMonitor.utils.debug: 配置:', PerformanceMonitor.config);
      console.log('DOM.PerformanceMonitor.utils.debug: 計時器:', Array.from(PerformanceMonitor.timers.keys()));
      console.log('DOM.PerformanceMonitor.utils.debug: 報告:', PerformanceMonitor.getReport());
      console.groupEnd();
    }
  }
};

// =================================================================
//   初始化模組 (Initialization Module)
// =================================================================

const Initializer = {
  // 初始化應用程式
  init: () => {
    console.log('DOM.Initializer.init called：開始初始化應用程式');
    
    try {
      // 初始化效能監控
      PerformanceMonitor.init();
      
      // 初始化資料載入器
      DOM.dataLoader.utils.preloadData(['givers']);
      
      // 設定定期清理
      setInterval(() => {
        DOM.dataLoader.utils.cleanupExpiredCache();
      }, DOM.dataLoader.config.cacheExpiry);
      
      console.log('應用程式初始化完成');
      
    } catch (error) {
      console.error('DOM.Initializer.init: 應用程式初始化失敗:', error);
      ErrorHandler.handle(error, ERROR_TYPES.UNKNOWN, { context: 'Initializer.init' });
    }
  }
};

// =================================================================
//   初始化 (Initialization Functions)
// =================================================================

// 頁面載入時設定全域事件監聽器
DOM.events.add(document, 'DOMContentLoaded', function() {
  console.log('DOM.events.add called：頁面載入時設定全域事件監聽器');
  // 使用初始化模組進行完整初始化
  Initializer.init();

  // 設定 resize 事件監聽器，用於處理服務項目溢出
  let resizeTimeout;
  window.addEventListener('resize', () => {
    console.log('DOM.events.add: 設定 resize 事件監聽器');
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      if (DOM.giver && typeof DOM.giver.checkAllTopicsOverflow === 'function') {
        DOM.giver.checkAllTopicsOverflow();
      }
    }, 150);
  });

  // --- 手動初始化聊天對話框，並將實例存到全域變數中 ---
  const giverModalElement = DOM.getById(CONFIG.SELECTORS.GIVER_MODAL);
  if (giverModalElement) {
    console.log('DOM.events.add: 手動初始化聊天對話框');
    // 初始化 Modal 實例，並設定點擊外部不可關閉
    CONFIG.INSTANCES.GIVER_MODAL = new bootstrap.Modal(giverModalElement, {
      backdrop: 'static', // 點擊背景不會關閉 Modal
      keyboard: false     // 按下 ESC 鍵不會關閉 Modal
    });

    // 監聽 'shown.bs.modal' 事件，此事件在對話框完全顯示後觸發
    giverModalElement.addEventListener('shown.bs.modal', () => {
      console.log('DOM.events.add: 監聽 shown.bs.modal 事件');
      const modalDialog = giverModalElement.querySelector('.modal-dialog');
      const modalContent = giverModalElement.querySelector('.modal-content');
      const modalBody = giverModalElement.querySelector('.modal-body');

      if (modalDialog && modalContent && modalBody) {
        // --- 最終解決方案：用 JS 動態應用 Flexbox ---

        // 1. 設定對話框本身的最大高度，確保它不會超出視窗
        modalDialog.style.height = '90vh';
        modalContent.style.height = '100%';
        
        // 2. 將 modal-content 設為 Flex 容器，讓其子元素可以彈性分配空間
        modalContent.style.display = 'flex';
        modalContent.style.flexDirection = 'column';

        // 3. 讓 modal-body (內容區) 自動填滿所有剩餘空間
        modalBody.style.flexGrow = '1';
        modalBody.style.overflowY = 'auto'; // 讓內容區內部可以滾動
      }
    });
  }
});

// === 新增：表單欄位初始化 function ===
// 初始化時段表單的輸入欄位，設定預設值和事件監聽器
function initScheduleFormInputs(formElement) {
  console.log('initScheduleFormInputs() called: 初始化表單欄位');
  console.log('initScheduleFormInputs() formElement:', formElement);
  
  // 日期 input
  console.log('initScheduleFormInputs called: 初始化表單欄位');
  // 日期 input
  const dateInput = formElement.querySelector('#schedule-date');
  if (dateInput) {
    dateInput.value = DateUtils.getTodayFormatted();
    dateInput.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      DOM.chat.showDatePicker();
    });
    dateInput.addEventListener('focus', (e) => {
      e.preventDefault();
      DOM.chat.showDatePicker();
    });
  }
  // 開始時間 input
  const startTimeInput = formElement.querySelector('#schedule-start-time');
  if (startTimeInput) {
    startTimeInput.value = '20:00';
    startTimeInput.addEventListener('input', (e) => {
      DOM.chat.formatTimeInput(e.target);
      const validationResult = FormValidator.validateField('startTime', e.target.value, 'schedule');
      if (!validationResult.isValid) {
        FormValidator.showValidationError(validationResult.errorMessage, e.target);
      } else {
        FormValidator.clearValidationError(e.target);
      }
    });
    startTimeInput.addEventListener('blur', (e) => {
      DOM.chat.validateAndFormatTime(e.target);
      const validationResult = FormValidator.validateField('startTime', e.target.value, 'schedule');
      if (!validationResult.isValid) {
        FormValidator.showValidationError(validationResult.errorMessage, e.target);
      } else {
        FormValidator.clearValidationError(e.target);
      }
    });
  }
  // 結束時間 input
  const endTimeInput = formElement.querySelector('#schedule-end-time');
  if (endTimeInput) {
    endTimeInput.value = '22:00';
    endTimeInput.addEventListener('input', (e) => {
      DOM.chat.formatTimeInput(e.target);
      const validationResult = FormValidator.validateField('endTime', e.target.value, 'schedule');
      if (!validationResult.isValid) {
        FormValidator.showValidationError(validationResult.errorMessage, e.target);
      } else {
        FormValidator.clearValidationError(e.target);
      }
    });
    endTimeInput.addEventListener('blur', (e) => {
      DOM.chat.validateAndFormatTime(e.target);
      const validationResult = FormValidator.validateField('endTime', e.target.value, 'schedule');
      if (!validationResult.isValid) {
        FormValidator.showValidationError(validationResult.errorMessage, e.target);
      } else {
        FormValidator.clearValidationError(e.target);
      }
    });
  }
  // 備註 input（如需即時驗證可加上）
}

// ...
// 在 handleSingleTime 動態產生表單後呼叫
// ...
// 於動態產生表單後加上：
const formElement = document.getElementById('time-schedule-form');
if (formElement) {
  initScheduleFormInputs(formElement);
}
// ...
// setupScheduleForm 只負責表單提交事件即可

// =================================================================
//   聊天狀態管理模組 (Chat State Management Module)
// =================================================================

const ChatStateManager = {
  // 狀態配置
  CONFIG: {
    // 狀態鍵值
    STATE_KEYS: {
      CURRENT_GIVER: 'currentGiver',
      IS_ACTIVE: 'isActive',
      MESSAGE_HISTORY: 'messageHistory',
      LAST_MESSAGE_TIME: 'lastMessageTime',
      PROVIDED_SCHEDULES: 'providedSchedules',
      IS_MULTIPLE_TIMES_MODE: 'isMultipleTimesMode',
      SELECTED_DATE: 'selectedDate'
    },
    
    // 預設狀態
    DEFAULT_STATE: {
      currentGiver: null,
      isActive: false,
      messageHistory: [],
      lastMessageTime: null,
      providedSchedules: [],
      isMultipleTimesMode: false,
      selectedDate: null
    },
    
    // 狀態驗證規則
    VALIDATION_RULES: {
      MESSAGE_HISTORY_MAX_LENGTH: 1000,
      PROVIDED_SCHEDULES_MAX_LENGTH: 50,
      LAST_MESSAGE_TIME_MAX_AGE: 24 * 60 * 60 * 1000 // 24小時
    }
  },
  
  // 內部狀態存儲
  _state: {
    currentGiver: null,
    isActive: false,
    messageHistory: [],
    lastMessageTime: null,
    providedSchedules: [],
    isMultipleTimesMode: false,
    selectedDate: null
  },
  
  // 狀態變更監聽器
  _listeners: new Map(),
  
  // 初始化狀態管理器
  init: () => {
    console.log('ChatStateManager.init called：初始化聊天狀態管理器');
    ChatStateManager.reset();
    console.log('ChatStateManager.init: 狀態管理器初始化完成');
  },
  
  // 重置狀態到預設值
  reset: () => {
    console.log('ChatStateManager.reset called：重置聊天狀態');
    ChatStateManager._state = { ...ChatStateManager.CONFIG.DEFAULT_STATE };
    ChatStateManager._notifyListeners('reset', ChatStateManager._state);
    console.log('ChatStateManager.reset: 狀態已重置', ChatStateManager._state);
  },
  
  // 獲取完整狀態
  getState: () => {
    return { ...ChatStateManager._state };
  },
  
  // 獲取特定狀態值
  get: (key) => {
    console.log('ChatStateManager.get called', { key });
    const value = ChatStateManager._state[key];
    console.log('ChatStateManager.get: 獲取狀態值', { key, value });
    return value;
  },
  
  // 設定特定狀態值
  set: (key, value) => {
    console.log('ChatStateManager.set called', { key, value });
    
    // 驗證狀態鍵值
    if (!Object.values(ChatStateManager.CONFIG.STATE_KEYS).includes(key)) {
      console.warn('ChatStateManager.set: 無效的狀態鍵值', { key });
      return false;
    }
    
    // 驗證狀態值
    if (!ChatStateManager._validateStateValue(key, value)) {
      console.warn('ChatStateManager.set: 狀態值驗證失敗', { key, value });
      return false;
    }
    
    const oldValue = ChatStateManager._state[key];
    ChatStateManager._state[key] = value;
    
    // 通知監聽器
    ChatStateManager._notifyListeners(key, value, oldValue);
    
    console.log('ChatStateManager.set: 狀態值已更新', { key, oldValue, newValue: value });
    return true;
  },
  
  // 批量更新狀態
  setMultiple: (updates) => {
    console.log('ChatStateManager.setMultiple called', { updates });
    
    const results = {};
    let hasChanges = false;
    
    for (const [key, value] of Object.entries(updates)) {
      const success = ChatStateManager.set(key, value);
      results[key] = success;
      if (success) hasChanges = true;
    }
    
    if (hasChanges) {
      ChatStateManager._notifyListeners('multiple', updates);
    }
    
    console.log('ChatStateManager.setMultiple: 批量更新完成', { results });
    return results;
  },
  
  // 初始化聊天會話
  initChatSession: (giver) => {
    console.log('ChatStateManager.initChatSession called', { giver });
    
    const updates = {
      [ChatStateManager.CONFIG.STATE_KEYS.CURRENT_GIVER]: giver,
      [ChatStateManager.CONFIG.STATE_KEYS.IS_ACTIVE]: true,
      [ChatStateManager.CONFIG.STATE_KEYS.MESSAGE_HISTORY]: [],
      [ChatStateManager.CONFIG.STATE_KEYS.LAST_MESSAGE_TIME]: new Date(),
      [ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES]: [],
      [ChatStateManager.CONFIG.STATE_KEYS.IS_MULTIPLE_TIMES_MODE]: false,
      [ChatStateManager.CONFIG.STATE_KEYS.SELECTED_DATE]: null
    };
    
    ChatStateManager.setMultiple(updates);
    console.log('ChatStateManager.initChatSession: 聊天會話已初始化');
  },
  
  // 結束聊天會話
  endChatSession: () => {
    console.log('ChatStateManager.endChatSession called');
    
    const updates = {
      [ChatStateManager.CONFIG.STATE_KEYS.CURRENT_GIVER]: null,
      [ChatStateManager.CONFIG.STATE_KEYS.IS_ACTIVE]: false,
      [ChatStateManager.CONFIG.STATE_KEYS.IS_MULTIPLE_TIMES_MODE]: false,
      [ChatStateManager.CONFIG.STATE_KEYS.SELECTED_DATE]: null
    };
    
    ChatStateManager.setMultiple(updates);
    console.log('ChatStateManager.endChatSession: 聊天會話已結束');
  },
  
  // 添加訊息到歷史記錄
  addMessage: (message) => {
    console.log('ChatStateManager.addMessage called', { message });
    
    const messageHistory = ChatStateManager.get(ChatStateManager.CONFIG.STATE_KEYS.MESSAGE_HISTORY);
    
    // 檢查訊息歷史長度限制
    if (messageHistory.length >= ChatStateManager.CONFIG.VALIDATION_RULES.MESSAGE_HISTORY_MAX_LENGTH) {
      // 移除最舊的訊息
      messageHistory.shift();
    }
    
    // 添加新訊息
    messageHistory.push({
      ...message,
      timestamp: new Date()
    });
    
    // 更新狀態
    ChatStateManager.setMultiple({
      [ChatStateManager.CONFIG.STATE_KEYS.MESSAGE_HISTORY]: messageHistory,
      [ChatStateManager.CONFIG.STATE_KEYS.LAST_MESSAGE_TIME]: new Date()
    });
    
    console.log('ChatStateManager.addMessage: 訊息已添加到歷史記錄');
  },
  
  // 添加使用者訊息
  addUserMessage: (content) => {
    console.log('ChatStateManager.addUserMessage called', { content });
    
    const message = {
      type: 'user',
      content: content,
      timestamp: new Date()
    };
    
    ChatStateManager.addMessage(message);
  },
  
  // 添加 Giver 訊息
  addGiverMessage: (content) => {
    console.log('ChatStateManager.addGiverMessage called', { content });
    
    const message = {
      type: 'giver',
      content: content,
      timestamp: new Date()
    };
    
    ChatStateManager.addMessage(message);
  },
  
  // 添加時段到已提供時段列表
  addSchedule: (schedule) => {
    console.log('ChatStateManager.addSchedule called', { schedule });
    
    const providedSchedules = ChatStateManager.get(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES);
    
    // 檢查時段列表長度限制
    if (providedSchedules.length >= ChatStateManager.CONFIG.VALIDATION_RULES.PROVIDED_SCHEDULES_MAX_LENGTH) {
      console.warn('ChatStateManager.addSchedule: 時段列表已達最大長度限制');
      return false;
    }
    
    // 添加新時段
    providedSchedules.push({
      ...schedule,
      timestamp: new Date()
    });
    
    ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES, providedSchedules);
    console.log('ChatStateManager.addSchedule: 時段已添加到列表');
    return true;
  },
  
  // 批量添加時段
  addSchedules: (schedules) => {
    console.log('ChatStateManager.addSchedules called', { schedules });
    
    const providedSchedules = ChatStateManager.get(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES);
    
    // 檢查是否會超過長度限制
    if (providedSchedules.length + schedules.length > ChatStateManager.CONFIG.VALIDATION_RULES.PROVIDED_SCHEDULES_MAX_LENGTH) {
      console.warn('ChatStateManager.addSchedules: 批量添加會超過長度限制');
      return false;
    }
    
    // 批量添加時段
    const newSchedules = schedules.map(schedule => ({
      ...schedule,
      timestamp: new Date()
    }));
    
    providedSchedules.push(...newSchedules);
    ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES, providedSchedules);
    console.log('ChatStateManager.addSchedules: 批量時段已添加到列表');
    return true;
  },
  
  // 設定多筆時段模式
  setMultipleTimesMode: (isEnabled) => {
    console.log('ChatStateManager.setMultipleTimesMode called', { isEnabled });
    ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.IS_MULTIPLE_TIMES_MODE, isEnabled);
  },
  
  // 設定選中的日期
  setSelectedDate: (date) => {
    console.log('ChatStateManager.setSelectedDate called', { date });
    ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.SELECTED_DATE, date);
  },
  
  // 獲取聊天統計
  getStats: () => {
    console.log('ChatStateManager.getStats called');
    
    const state = ChatStateManager.getState();
    const messageHistory = state[ChatStateManager.CONFIG.STATE_KEYS.MESSAGE_HISTORY];
    
    const stats = {
      totalMessages: messageHistory.length,
      userMessages: messageHistory.filter(msg => msg.type === 'user').length,
      giverMessages: messageHistory.filter(msg => msg.type === 'giver').length,
      lastMessageTime: state[ChatStateManager.CONFIG.STATE_KEYS.LAST_MESSAGE_TIME],
      isActive: state[ChatStateManager.CONFIG.STATE_KEYS.IS_ACTIVE],
      currentGiver: state[ChatStateManager.CONFIG.STATE_KEYS.CURRENT_GIVER],
      providedSchedulesCount: state[ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES].length,
      isMultipleTimesMode: state[ChatStateManager.CONFIG.STATE_KEYS.IS_MULTIPLE_TIMES_MODE]
    };
    
    console.log('ChatStateManager.getStats: 統計資料', stats);
    return stats;
  },
  
  // 獲取訊息歷史
  getMessageHistory: () => {
    console.log('ChatStateManager.getMessageHistory called');
    const messageHistory = ChatStateManager.get(ChatStateManager.CONFIG.STATE_KEYS.MESSAGE_HISTORY);
    return [...messageHistory];
  },
  
  // 清空訊息歷史
  clearMessageHistory: () => {
    console.log('ChatStateManager.clearMessageHistory called');
    ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.MESSAGE_HISTORY, []);
  },
  
  // 獲取已提供時段列表
  getProvidedSchedules: () => {
    console.log('ChatStateManager.getProvidedSchedules called');
    const providedSchedules = ChatStateManager.get(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES);
    return [...providedSchedules];
  },
  
  // 清空已提供時段列表
  clearProvidedSchedules: () => {
    console.log('ChatStateManager.clearProvidedSchedules called');
    ChatStateManager.set(ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES, []);
  },
  
  // 檢查聊天是否活躍
  isActive: () => {
    console.log('ChatStateManager.isActive called');
    return ChatStateManager.get(ChatStateManager.CONFIG.STATE_KEYS.IS_ACTIVE);
  },
  
  // 獲取當前 Giver
  getCurrentGiver: () => {
    console.log('ChatStateManager.getCurrentGiver called');
    return ChatStateManager.get(ChatStateManager.CONFIG.STATE_KEYS.CURRENT_GIVER);
  },
  
  // 檢查是否為多筆時段模式
  isMultipleTimesMode: () => {
    console.log('ChatStateManager.isMultipleTimesMode called');
    return ChatStateManager.get(ChatStateManager.CONFIG.STATE_KEYS.IS_MULTIPLE_TIMES_MODE);
  },
  
  // 獲取選中的日期
  getSelectedDate: () => {
    console.log('ChatStateManager.getSelectedDate called');
    return ChatStateManager.get(ChatStateManager.CONFIG.STATE_KEYS.SELECTED_DATE);
  },
  
  // 添加狀態變更監聽器
  addListener: (key, callback) => {
    console.log('ChatStateManager.addListener called', { key, callback });
    
    if (!ChatStateManager._listeners.has(key)) {
      ChatStateManager._listeners.set(key, new Set());
    }
    
    ChatStateManager._listeners.get(key).add(callback);
    console.log('ChatStateManager.addListener: 監聽器已添加');
  },
  
  // 移除狀態變更監聽器
  removeListener: (key, callback) => {
    console.log('ChatStateManager.removeListener called', { key, callback });
    
    if (ChatStateManager._listeners.has(key)) {
      ChatStateManager._listeners.get(key).delete(callback);
      console.log('ChatStateManager.removeListener: 監聽器已移除');
    }
  },
  
  // 通知監聽器
  _notifyListeners: (key, newValue, oldValue) => {
    console.log('ChatStateManager._notifyListeners called', { key, newValue, oldValue });
    
    if (ChatStateManager._listeners.has(key)) {
      const callbacks = ChatStateManager._listeners.get(key);
      callbacks.forEach(callback => {
        try {
          callback(newValue, oldValue);
        } catch (error) {
          console.error('ChatStateManager._notifyListeners: 監聽器執行錯誤', error);
        }
      });
    }
  },
  
  // 驗證狀態值
  _validateStateValue: (key, value) => {
    console.log('ChatStateManager._validateStateValue called', { key, value });
    
    switch (key) {
      case ChatStateManager.CONFIG.STATE_KEYS.CURRENT_GIVER:
        return value === null || typeof value === 'object';
        
      case ChatStateManager.CONFIG.STATE_KEYS.IS_ACTIVE:
      case ChatStateManager.CONFIG.STATE_KEYS.IS_MULTIPLE_TIMES_MODE:
        return typeof value === 'boolean';
        
      case ChatStateManager.CONFIG.STATE_KEYS.MESSAGE_HISTORY:
        return Array.isArray(value);
        
      case ChatStateManager.CONFIG.STATE_KEYS.LAST_MESSAGE_TIME:
        return value === null || value instanceof Date;
        
      case ChatStateManager.CONFIG.STATE_KEYS.PROVIDED_SCHEDULES:
        return Array.isArray(value);
        
      case ChatStateManager.CONFIG.STATE_KEYS.SELECTED_DATE:
        return value === null || value instanceof Date;
        
      default:
        return true;
    }
  },
  
  // 調試功能
  debug: () => {
    console.group('ChatStateManager.debug called：聊天狀態調試資訊');
    console.log('當前狀態:', ChatStateManager.getState());
    console.log('統計資料:', ChatStateManager.getStats());
    console.log('訊息歷史:', ChatStateManager.getMessageHistory());
    console.log('已提供時段:', ChatStateManager.getProvidedSchedules());
    console.log('監聽器數量:', ChatStateManager._listeners.size);
    console.groupEnd();
  },
  
  // 匯出狀態（用於持久化）
  export: () => {
    console.log('ChatStateManager.export called');
    const state = ChatStateManager.getState();
    const exportData = {
      ...state,
      lastMessageTime: state.lastMessageTime ? state.lastMessageTime.toISOString() : null,
      selectedDate: state.selectedDate ? state.selectedDate.toISOString() : null
    };
    console.log('ChatStateManager.export: 狀態匯出完成', exportData);
    return exportData;
  },
  
  // 匯入狀態（用於恢復）
  import: (data) => {
    console.log('ChatStateManager.import called', { data });
    
    if (!data || typeof data !== 'object') {
      console.warn('ChatStateManager.import: 無效的匯入資料');
      return false;
    }
    
    try {
      const importedState = {
        ...data,
        lastMessageTime: data.lastMessageTime ? new Date(data.lastMessageTime) : null,
        selectedDate: data.selectedDate ? new Date(data.selectedDate) : null
      };
      
      // 驗證匯入的資料
      for (const [key, value] of Object.entries(importedState)) {
        if (!ChatStateManager._validateStateValue(key, value)) {
          console.warn('ChatStateManager.import: 匯入資料驗證失敗', { key, value });
          return false;
        }
      }
      
      // 更新狀態
      ChatStateManager._state = { ...ChatStateManager.CONFIG.DEFAULT_STATE, ...importedState };
      ChatStateManager._notifyListeners('import', ChatStateManager._state);
      
      console.log('ChatStateManager.import: 狀態匯入完成');
      return true;
    } catch (error) {
      console.error('ChatStateManager.import: 狀態匯入失敗', error);
      return false;
    }
  }
};

// =================================================================
//   UI 組件模組 (UIComponents)
// =================================================================

const UIComponents = {
  // 產生按鈕
  button: ({ text = '', className = '', icon = '', attrs = {} } = {}) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = className;
    if (icon) {
      const iconElem = document.createElement('i');
      iconElem.className = icon;
      btn.appendChild(iconElem);
      if (text) btn.appendChild(document.createTextNode(' '));
    }
    if (text) btn.appendChild(document.createTextNode(text));
    Object.entries(attrs).forEach(([k, v]) => btn.setAttribute(k, v));
    return btn;
  },

  // 產生確認對話框
  confirmDialog: ({ title = '', message = '', confirmText = '確定', cancelText = '取消', onConfirm, onCancel }) => {
    // 可根據現有 showConfirmDialog 實作
    return showConfirmDialog({ title, message, confirmText, cancelText, onConfirm, onCancel });
  },

  // 產生 Toast 訊息
  toast: ({ message = '', type = 'info', duration = 2000 }) => {
    const toast = document.createElement('div');
    toast.className = `ui-toast ui-toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => { toast.remove(); }, duration);
    return toast;
  },

  // 產生載入動畫
  spinner: ({ size = 'md', className = '' } = {}) => {
    const spinner = document.createElement('div');
    spinner.className = `ui-spinner spinner-border spinner-border-${size} ${className}`;
    spinner.setAttribute('role', 'status');
    spinner.innerHTML = '<span class="visually-hidden">Loading...</span>';
    return spinner;
  },

  // 產生 icon
  icon: (iconClass = '', extraClass = '') => {
    const icon = document.createElement('i');
    icon.className = `${iconClass} ${extraClass}`.trim();
    return icon;
  }
};

// =================================================================
//   API 請求模組 (APIClient)
// =================================================================

const APIClient = {
  // GET 請求
  get: async (url, options = {}) => {
    try {
      const res = await fetch(url, { ...options, method: 'GET' });
      return await APIClient._handleResponse(res);
    } catch (err) {
      APIClient._handleError(err);
      throw err;
    }
  },

  // POST 請求
  post: async (url, data = {}, options = {}) => {
    try {
      const res = await fetch(url, {
        ...options,
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
        body: JSON.stringify(data)
      });
      return await APIClient._handleResponse(res);
    } catch (err) {
      APIClient._handleError(err);
      throw err;
    }
  },

  // PUT 請求
  put: async (url, data = {}, options = {}) => {
    try {
      const res = await fetch(url, {
        ...options,
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
        body: JSON.stringify(data)
      });
      return await APIClient._handleResponse(res);
    } catch (err) {
      APIClient._handleError(err);
      throw err;
    }
  },

  // DELETE 請求
  delete: async (url, options = {}) => {
    try {
      const res = await fetch(url, { ...options, method: 'DELETE' });
      return await APIClient._handleResponse(res);
    } catch (err) {
      APIClient._handleError(err);
      throw err;
    }
  },

  // 統一處理回應
  _handleResponse: async (res) => {
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`API 錯誤: ${res.status} ${res.statusText} - ${errorText}`);
    }
    // 嘗試解析 JSON，若失敗則回傳原始文字
    try {
      return await res.json();
    } catch {
      return await res.text();
    }
  },

  // 統一錯誤處理
  _handleError: (err) => {
    console.error('APIClient 請求錯誤:', err);
    // 可在這裡加上全域錯誤提示、上報等
    UIComponents.toast({ message: '伺服器連線失敗，請稍後再試', type: 'error' });
  }
};