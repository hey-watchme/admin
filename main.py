"""
WatchMe 管理画面
- 通知管理（トップページ）
- データベース管理（ユーザー、デバイス）
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# FastAPIアプリケーションの初期化
app = FastAPI(title="WatchMe Admin", version="1.0.0")

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Supabaseクライアントのインポート
from api.supabase_client import SupabaseClient

# グローバルSupabaseクライアント
supabase_client = SupabaseClient()

# =====================================
# Pydanticモデル（必要最小限）
# =====================================

class User(BaseModel):
    user_id: str
    name: str
    email: Optional[str] = None
    status: str
    subscription_plan: Optional[str] = None
    newsletter_subscription: Optional[bool] = False
    created_at: datetime
    updated_at: Optional[datetime] = None

class Device(BaseModel):
    device_id: str
    device_type: str
    owner_user_id: Optional[str] = None
    platform_type: Optional[str] = None
    platform_identifier: Optional[str] = None
    status: str
    total_audio_count: int = 0
    last_sync: Optional[datetime] = None
    registered_at: datetime

class Notification(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    is_read: bool = False
    created_at: datetime
    triggered_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# =====================================
# HTMLページエンドポイント
# =====================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """トップページ - 通知管理"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/database/users", response_class=HTMLResponse)
async def users_page(request: Request):
    """ユーザー管理ページ"""
    return templates.TemplateResponse("users.html", {"request": request})

@app.get("/database/devices", response_class=HTMLResponse)
async def devices_page(request: Request):
    """デバイス管理ページ"""
    return templates.TemplateResponse("devices.html", {"request": request})

# =====================================
# API エンドポイント
# =====================================

# --- 統計情報 ---
@app.get("/api/stats")
async def get_stats():
    """統計情報を取得"""
    try:
        # ユーザー数を取得
        users = await supabase_client.select("users")
        users_count = len(users)
        
        # デバイス数を取得
        devices = await supabase_client.select("devices")
        devices_count = len(devices)
        active_devices = [d for d in devices if d.get("status") == "active"]
        
        # 通知数を取得
        notifications = await supabase_client.select("notifications")
        notifications_count = len(notifications)
        unread_count = len([n for n in notifications if not n.get("is_read", False)])
        
        return {
            "users": users_count,
            "devices": devices_count,
            "active_devices": len(active_devices),
            "notifications": notifications_count,
            "unread_notifications": unread_count
        }
    except Exception as e:
        return {"users": 0, "devices": 0, "notifications": 0, "error": str(e)}

# --- 通知管理 API ---
@app.get("/api/notifications")
async def get_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """通知一覧を取得（ページネーション付き）"""
    try:
        result = await supabase_client.select_paginated(
            "notifications",
            page=page,
            per_page=per_page,
            order="created_at.desc"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notifications")
async def create_notification(notification: Dict[str, Any]):
    """通知を作成"""
    try:
        result = await supabase_client.insert("notifications", notification)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """通知を既読にする"""
    try:
        result = await supabase_client.update(
            "notifications",
            {"is_read": True},
            {"id": notification_id}
        )
        return {"success": True, "message": "通知を既読にしました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/notifications/{notification_id}")
async def delete_notification(notification_id: str):
    """通知を削除"""
    try:
        result = await supabase_client.delete(
            "notifications",
            {"id": notification_id}
        )
        return {"success": True, "message": "通知を削除しました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ユーザー管理 API ---
@app.get("/api/users")
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """ユーザー一覧を取得（ページネーション付き）"""
    try:
        result = await supabase_client.select_paginated(
            "users",
            page=page,
            per_page=per_page,
            order="created_at.desc"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users")
async def create_user(user: Dict[str, Any]):
    """ユーザーを作成"""
    try:
        result = await supabase_client.insert("users", user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/users/{user_id}")
async def update_user(user_id: str, user_data: Dict[str, Any]):
    """ユーザー情報を更新"""
    try:
        result = await supabase_client.update(
            "users",
            user_data,
            {"user_id": user_id}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str):
    """ユーザーを削除"""
    try:
        result = await supabase_client.delete(
            "users",
            {"user_id": user_id}
        )
        return {"success": True, "message": "ユーザーを削除しました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- デバイス管理 API ---
@app.get("/api/devices")
async def get_devices(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """デバイス一覧を取得（ページネーション付き）"""
    try:
        result = await supabase_client.select_paginated(
            "devices",
            page=page,
            per_page=per_page,
            order="registered_at.desc"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices")
async def create_device(device: Dict[str, Any]):
    """デバイスを作成"""
    try:
        result = await supabase_client.insert("devices", device)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/devices/{device_id}")
async def update_device(device_id: str, device_data: Dict[str, Any]):
    """デバイス情報を更新"""
    try:
        result = await supabase_client.update(
            "devices",
            device_data,
            {"device_id": device_id}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/devices/{device_id}")
async def delete_device(device_id: str):
    """デバイスを削除"""
    try:
        result = await supabase_client.delete(
            "devices",
            {"device_id": device_id}
        )
        return {"success": True, "message": "デバイスを削除しました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =====================================
# メイン実行
# =====================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 9000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )