# 靜態檔案管理指南

## 📁 目錄結構

```
static/
├── images/                    # 圖片資源目錄
│   ├── icons/                 # 圖示類檔案
│   │   ├── favicon.png        # 網站圖示
│   │   ├── chat-avatar.svg    # 聊天頭像
│   │   └── logo-header.svg    # 頁首標誌
│   ├── ui/                    # UI 元件圖片
│   │   ├── buttons/           # 按鈕圖片
│   │   ├── backgrounds/       # 背景圖片
│   │   └── borders/           # 邊框圖片
│   ├── content/               # 內容相關圖片
│   │   ├── avatars/           # 使用者頭像
│   │   ├── banners/           # 橫幅圖片
│   │   └── illustrations/     # 插圖
│   └── temp/                  # 暫存圖片
├── css/                       # 樣式檔案
│   ├── style.css              # 主要樣式檔案
│   └── components/            # 元件樣式
├── js/                        # JavaScript 檔案
│   ├── script.js              # 主要腳本檔案
│   └── modules/               # 模組化 JS
└── fonts/                     # 字體檔案（如果需要）
```

## 🏷️ 命名規範

### 1. 檔案命名規則

```
[類型]-[功能]-[尺寸]-[狀態].[副檔名]
```

**範例：**

- `icon-chat-avatar-32x32.svg`
- `logo-header-primary-200x60.svg`
- `btn-submit-active-120x40.png`
- `bg-gradient-primary-1920x1080.jpg`

### 2. 目錄命名規則

```
[功能]-[類型]
```

**範例：**

- `icons-ui/` - UI 圖示
- `images-content/` - 內容圖片
- `avatars-users/` - 使用者頭像

## 📋 檔案類型說明

### 圖片檔案

- **favicon.png**: 網站圖示，顯示在瀏覽器標籤頁
- **chat-avatar.svg**: 聊天介面中的預設頭像
- **logo-header.svg**: 頁首的 104 履歷診療室標誌

### 樣式檔案

- **style.css**: 主要的 CSS 樣式檔案，包含所有自定義樣式

### JavaScript 檔案

- **script.js**: 主要的 JavaScript 檔案，包含所有互動功能

## 🔧 使用方式

### HTML 中的引用

```html
<!-- 圖片 -->
<img src="/static/images/icons/logo-header.svg" alt="標誌" />

<!-- 樣式 -->
<link rel="stylesheet" href="/static/css/style.css" />

<!-- 腳本 -->
<script src="/static/js/script.js"></script>
```

### JavaScript 中的引用

```javascript
// 設定圖片來源
avatarImg.src = "/static/images/icons/chat-avatar.svg";
```

## 📝 維護指南

### 新增圖片

1. 根據圖片類型選擇適當的目錄
2. 使用一致的命名規範
3. 更新相關的 HTML/JS 檔案中的路徑

### 新增樣式

1. 將 CSS 檔案放在 `css/` 目錄下
2. 在 HTML 中引用新的樣式檔案

### 新增腳本

1. 將 JS 檔案放在 `js/` 目錄下
2. 在 HTML 中引用新的腳本檔案

## 🎯 最佳實踐

1. **保持結構清晰**: 按照功能分類組織檔案
2. **使用描述性名稱**: 檔案名稱應該清楚表達其用途
3. **保持一致性**: 遵循既定的命名規範
4. **定期清理**: 移除不再使用的檔案
5. **版本控制**: 重要更新時考慮版本號命名
