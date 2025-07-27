from fastapi import FastAPI
import tomllib  # Python 3.11+ 內建
import os

# --- 動態讀取專案版本號 ---
# 假設 pyproject.toml 位於專案根目錄，即 app 目錄的上一級
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 計算專案根目錄的絕對路徑
PYPROJECT_TOML_PATH = os.path.join(PROJECT_ROOT, "pyproject.toml")  # 取得 pyproject.toml 檔案的絕對路徑

try: 
    with open(PYPROJECT_TOML_PATH, "rb") as f:
        pyproject_data = tomllib.load(f)  # 使用 tomllib 讀取 pyproject.toml 檔案，並將內容儲存在 pyproject_data 變數中
        PROJECT_VERSION = pyproject_data["tool"]["poetry"]["version"]  # 從 pyproject.toml 中提取專案版本號
except (FileNotFoundError, KeyError, tomllib.TomlDecodeError) as e:
    print(f"警告: 無法從 pyproject.toml 讀取專案版本號。錯誤: {e}")
    PROJECT_VERSION = "unknown" # 設定一個預設值，以防萬一

# 定義叫 app 的 FastAPI 應用實例，所有 API 路由（像 /, /schedules）都掛在這個 app 上。
app = FastAPI(
    title="104 Resume Clinic Scheduler",
    description="【MVP】104 履歷診療室 - 站內諮詢時間媒合系統",
    version=PROJECT_VERSION, # 從 pyproject.toml 動態讀取,
)

@app.get("/")
async def root():
    return {"message": "Hello, 104 Resume Clinic Scheduler!"}
