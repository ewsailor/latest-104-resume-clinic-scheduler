# 資料庫連線最佳實踐

## 🎯 MySQL 驅動程式選擇

### 驅動程式對比

| 驅動程式           | 優點                        | 缺點               | 建議        |
| ------------------ | --------------------------- | ------------------ | ----------- |
| **pymysql**        | 純 Python、安裝簡單、跨平台 | 效能稍慢           | ✅ **推薦** |
| **mysqlconnector** | 官方驅動、效能較好          | 需要編譯、安裝複雜 | ❌ 不推薦   |

### 為什麼選擇 pymysql

#### **✅ pymysql 的優勢**

| 優勢               | 說明                     | 影響                     |
| ------------------ | ------------------------ | ------------------------ |
| **純 Python 實作** | 無需編譯，安裝簡單       | 部署更容易               |
| **跨平台相容**     | 在所有平台上都能正常運作 | 開發環境一致性           |
| **專案一致性**     | 專案已使用 pymysql       | 避免混合使用不同驅動程式 |
| **社群支援**       | 活躍的社群支援           | 問題解決更容易           |
| **FastAPI 生態**   | FastAPI 社群常用         | 更好的整合性             |

#### **❌ mysqlconnector 的問題**

| 問題           | 說明                           | 影響           |
| -------------- | ------------------------------ | -------------- |
| **安裝複雜**   | 需要編譯，在某些環境下安裝困難 | 部署問題       |
| **依賴管理**   | 需要額外安裝，增加專案複雜度   | 維護成本增加   |
| **相容性問題** | 與某些系統不相容               | 開發環境不一致 |

## 🔧 連線字串最佳實踐

### 1. 基本格式

```python
# ✅ 推薦格式
DATABASE_URL = "mysql+pymysql://username:password@host:port/database?charset=utf8mb4"

# ❌ 不推薦格式
DATABASE_URL = "mysql+mysqlconnector://user:password@localhost:3306/fastapi_db"
```

### 2. 使用 Settings 配置

```python
# ✅ 最佳實踐：使用 settings 配置
DATABASE_URL = settings.mysql_connection_string

# 在 settings.py 中定義
@property
def mysql_connection_string(self) -> str:
    """MySQL 連接字串"""
    password = self.mysql_password.get_secret_value() if self.mysql_password is not None else ""
    return (
        f"mysql+pymysql://{self.mysql_user}:{password}"
        f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        f"?charset={self.mysql_charset}"
    )
```

### 3. 連線參數最佳實踐

```python
# ✅ 最佳實踐配置
engine = create_engine(
    DATABASE_URL,
    echo=False,  # 關閉 SQL 查詢日誌
    pool_pre_ping=True,  # 啟用連線檢查
    pool_recycle=3600,  # 連線池回收時間（1小時）
    pool_size=10,  # 連線池大小
    max_overflow=20,  # 最大溢出連線數
    pool_timeout=30,  # 連線超時時間（30秒）
    # pymysql 特定參數
    connect_args={
        "charset": "utf8mb4",  # 使用 utf8mb4 字符集
        "autocommit": False,  # 手動提交事務
        "sql_mode": "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO",  # 嚴格模式
    }
)
```

## 📊 參數說明

### 1. 連線池參數

| 參數            | 說明         | 建議值 | 原因               |
| --------------- | ------------ | ------ | ------------------ |
| `pool_pre_ping` | 連線前檢查   | `True` | 確保連線有效性     |
| `pool_recycle`  | 連線回收時間 | `3600` | 避免長時間閒置連線 |
| `pool_size`     | 連線池大小   | `10`   | 平衡效能和資源使用 |
| `max_overflow`  | 最大溢出連線 | `20`   | 處理突發流量       |
| `pool_timeout`  | 連線超時     | `30`   | 避免長時間等待     |

### 2. pymysql 特定參數

| 參數         | 說明     | 建議值    | 原因               |
| ------------ | -------- | --------- | ------------------ |
| `charset`    | 字符集   | `utf8mb4` | 支援完整的 Unicode |
| `autocommit` | 自動提交 | `False`   | 手動控制事務       |
| `sql_mode`   | SQL 模式 | 嚴格模式  | 資料完整性         |

## 🎯 環境變數配置

### 1. 開發環境

```bash
# .env.development
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=fastapi_user
MYSQL_PASSWORD=fastapi123
MYSQL_DATABASE=scheduler_db
MYSQL_CHARSET=utf8mb4
```

### 2. 生產環境

```bash
# .env.production
MYSQL_HOST=production-db.example.com
MYSQL_PORT=3306
MYSQL_USER=app_user
MYSQL_PASSWORD=secure_password_here
MYSQL_DATABASE=scheduler_prod
MYSQL_CHARSET=utf8mb4
```

### 3. 測試環境

```bash
# .env.test
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=test_user
MYSQL_PASSWORD=test123
MYSQL_DATABASE=scheduler_test
MYSQL_CHARSET=utf8mb4
```

## 🔍 錯誤處理最佳實踐

### 1. 連線錯誤處理

```python
try:
    # 創建資料庫引擎
    engine = create_engine(DATABASE_URL, **engine_config)

    # 測試連線
    with engine.connect() as connection:
        logger.info(f"✅ 成功建立資料庫引擎，並連結到資料庫：{settings.mysql_database}")
        logger.info(f"📍 資料庫主機：{settings.mysql_host}:{settings.mysql_port}")
        logger.info(f"👤 使用者：{settings.mysql_user}")
        logger.info(f"🔧 驅動程式：pymysql")

except Exception as e:
    logger.error(f"❌ 連結到資料庫失敗：{str(e)}")
    logger.error(f"🔍 請檢查以下項目：")
    logger.error(f"   1. MySQL 服務是否正在運行")
    logger.error(f"   2. 資料庫連線設定是否正確")
    logger.error(f"   3. 使用者權限是否足夠")
    logger.error(f"   4. 防火牆設定是否允許連線")
    raise
```

### 2. 常見錯誤及解決方案

| 錯誤                 | 原因             | 解決方案           |
| -------------------- | ---------------- | ------------------ |
| `Access denied`      | 使用者權限不足   | 檢查使用者權限設定 |
| `Connection refused` | MySQL 服務未運行 | 啟動 MySQL 服務    |
| `Unknown database`   | 資料庫不存在     | 建立資料庫         |
| `Connection timeout` | 網路連線問題     | 檢查網路設定       |

## 🎯 效能優化

### 1. 連線池優化

```python
# 根據應用程式需求調整連線池大小
if settings.is_production:
    pool_size = 20
    max_overflow = 40
else:
    pool_size = 5
    max_overflow = 10
```

### 2. 查詢優化

```python
# 使用連線池管理
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 在 FastAPI 中使用
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### 3. 監控和日誌

```python
# 啟用 SQL 查詢日誌（僅開發環境）
if settings.is_development:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
else:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
```

## 🔒 安全性最佳實踐

### 1. 密碼管理

```python
# 使用 SecretStr 保護敏感資訊
mysql_password: Optional[SecretStr] = Field(
    default=None,
    description="MySQL 密碼"
)

# 在連線字串中使用
password = self.mysql_password.get_secret_value() if self.mysql_password is not None else ""
```

### 2. 最小權限原則

```sql
-- 建立專用應用程式使用者
CREATE USER 'fastapi_user'@'localhost' IDENTIFIED BY 'secure_password';

-- 只授予必要權限
GRANT SELECT, INSERT, UPDATE, DELETE ON scheduler_db.* TO 'fastapi_user'@'localhost';
GRANT CREATE, DROP, ALTER ON scheduler_db.* TO 'fastapi_user'@'localhost';

-- 刷新權限
FLUSH PRIVILEGES;
```

### 3. 網路安全

```python
# 限制連線來源
# 在 MySQL 配置中設定
bind-address = 127.0.0.1  # 只允許本地連線
```

## 📊 測試策略

### 1. 連線測試

```python
def test_database_connection():
    """測試資料庫連線"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1
        print("✅ 資料庫連線測試通過")
    except Exception as e:
        print(f"❌ 資料庫連線測試失敗：{e}")
        raise
```

### 2. 效能測試

```python
import time

def test_connection_performance():
    """測試連線效能"""
    start_time = time.time()

    for i in range(100):
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    end_time = time.time()
    avg_time = (end_time - start_time) / 100
    print(f"平均連線時間：{avg_time:.3f}秒")
```

## 🎯 部署建議

### 1. Docker 部署

```dockerfile
# Dockerfile
FROM python:3.12-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 套件
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

# 複製應用程式
COPY . .

# 啟動應用程式
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Kubernetes 部署

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
        - name: fastapi-app
          image: fastapi-app:latest
          env:
            - name: MYSQL_HOST
              value: "mysql-service"
            - name: MYSQL_PORT
              value: "3306"
            - name: MYSQL_USER
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: username
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: password
```

## 📊 總結

### 1. 驅動程式選擇

**✅ 強烈建議使用 pymysql：**

| 考量因素       | pymysql   | mysqlconnector | 建議       |
| -------------- | --------- | -------------- | ---------- |
| **安裝簡便性** | ✅ 簡單   | ❌ 複雜        | ✅ pymysql |
| **跨平台相容** | ✅ 好     | ❌ 一般        | ✅ pymysql |
| **專案一致性** | ✅ 已使用 | ❌ 需要改變    | ✅ pymysql |
| **社群支援**   | ✅ 活躍   | ⚠️ 官方        | ✅ pymysql |
| **效能**       | ⚠️ 稍慢   | ✅ 較快        | ⚠️ 平手    |

### 2. 連線字串格式

**✅ 推薦格式：**

```python
DATABASE_URL = "mysql+pymysql://username:password@host:port/database?charset=utf8mb4"
```

**❌ 避免格式：**

```python
DATABASE_URL = "mysql+mysqlconnector://user:password@localhost:3306/fastapi_db"
```

### 3. 最佳實踐建議

1. **使用 pymysql 驅動程式**
2. **透過 settings 管理連線配置**
3. **設定適當的連線池參數**
4. **使用 utf8mb4 字符集**
5. **實施適當的錯誤處理**
6. **遵循最小權限原則**
7. **定期監控連線效能**
8. **完整的測試覆蓋**

### 4. 實施建議

**立即行動：**

1. 保持使用 pymysql 驅動程式
2. 更新連線字串使用 settings 配置
3. 加入連線池最佳實踐參數
4. 實施適當的錯誤處理
5. 建立完整的測試

這種配置既符合業界最佳實踐，又確保了應用程式的穩定性和可維護性！
