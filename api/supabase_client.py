import os
import httpx
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

        self.rest_url = f"{self.url}/rest/v1"
        self.auth_url = f"{self.url}/auth/v1"
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

        # Admin API用のヘッダー（Service Role Key使用）
        if self.service_role_key:
            self.admin_headers = {
                "apikey": self.service_role_key,
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": "application/json",
            }
        else:
            self.admin_headers = None

    async def select(self, table: str, columns: str = "*", filters: Optional[Dict[str, Any]] = None, order: Optional[str] = None) -> List[Dict[str, Any]]:
        """データを取得"""
        url = f"{self.rest_url}/{table}"
        params = {"select": columns}
        
        if filters:
            for key, value in filters.items():
                params[key] = f"eq.{value}"
        
        if order:
            params["order"] = order
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """データを挿入"""
        url = f"{self.rest_url}/{table}"
        headers = {**self.headers, "Prefer": "return=representation"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0]
            elif isinstance(result, dict):
                return result
            else:
                raise ValueError(f"Unexpected result format: {result}")

    async def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """データを更新"""
        url = f"{self.rest_url}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[key] = f"eq.{value}"
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, json=data, params=params)
            response.raise_for_status()
            result = response.json()
            return result[0] if result else {}

    async def select_paginated(self, table: str, page: int = 1, per_page: int = 20, 
                              filters: Optional[Dict[str, Any]] = None, 
                              order: Optional[str] = None) -> Dict[str, Any]:
        """ページネーション付きでデータを取得"""
        url = f"{self.rest_url}/{table}"
        
        # オフセットとリミットを計算
        offset = (page - 1) * per_page
        
        params = {
            "offset": offset,
            "limit": per_page
        }
        
        # フィルタリング条件を追加
        if filters:
            for key, value in filters.items():
                params[key] = f"eq.{value}"
        
        # 並び順を追加
        if order:
            params["order"] = order
        
        # 総件数を取得するヘッダーを追加
        headers = {**self.headers, "Prefer": "count=exact"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Content-Rangeヘッダーから総件数を取得
            content_range = response.headers.get("content-range", "")
            total = 0
            if content_range:
                # Format: "0-19/100" -> total = 100
                parts = content_range.split("/")
                if len(parts) == 2 and parts[1].isdigit():
                    total = int(parts[1])
            
            # ページネーション情報を計算
            total_pages = (total + per_page - 1) // per_page if total > 0 else 1
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                "items": data,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }

    async def delete(self, table: str, filters: Dict[str, Any]) -> bool:
        """データを削除"""
        url = f"{self.rest_url}/{table}"
        params = {}

        for key, value in filters.items():
            params[key] = f"eq.{value}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.status_code == 204

    async def delete_auth_user(self, user_id: str) -> bool:
        """auth.usersテーブルからユーザーを削除（Admin API使用）"""
        if not self.admin_headers:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY is not set. Cannot delete auth users.")

        url = f"{self.auth_url}/admin/users/{user_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.admin_headers)
            response.raise_for_status()
            return response.status_code == 200

    # 基本的なCRUD操作のみ提供
    # すべての操作はmain.pyから直接select/insert/update/deleteメソッドを使用