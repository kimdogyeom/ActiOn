import requests
import logging
from typing import Dict, List, Optional
from config import settings

logger = logging.getLogger(__name__)


class NotionService:
    """Service for Notion API integration."""
    
    def __init__(self):
        self.api_key = settings.notion_api_key
        self.database_id = settings.notion_database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def create_task_page(self, action_item: Dict) -> Dict:
        """
        Create a new page in Notion database for an action item.
        
        Args:
            action_item: Dict with assignee, task, due_date, confidence
            
        Returns:
            Response from Notion API
        """
        url = f"{self.base_url}/pages"
        
        # Notion 페이지 속성 구성
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": action_item['task']
                        }
                    }
                ]
            }
        }
        
        # Status 추가 (존재하는 경우)
        properties["Status"] = {
            "select": {
                "name": "To Do"
            }
        }
        
        # Assignee 추가 (Text 타입으로 처리)
        if action_item.get('assignee') and action_item['assignee'] != "Unassigned":
            properties["Assignee"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": action_item['assignee']
                        }
                    }
                ]
            }
        
        # Due Date 추가
        if action_item.get('due_date'):
            properties["Due Date"] = {
                "date": {
                    "start": action_item['due_date']
                }
            }
        
        # Confidence 추가 (Number 타입)
        if action_item.get('confidence') is not None:
            properties["Confidence"] = {
                "number": action_item['confidence']
            }
        
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": properties
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {
                "status": "success",
                "page_id": response.json()['id']
            }
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text
            return {
                "status": "error",
                "error": error_detail
            }
    
    def create_multiple_tasks(self, action_items: List[Dict]) -> List[Dict]:
        """
        Create multiple task pages in Notion.
        
        Args:
            action_items: List of action item dicts
            
        Returns:
            List of results for each task creation
        """
        results = []
        for item in action_items:
            logger.info(f"Creating Notion task: {item.get('task', 'Unknown')}")
            result = self.create_task_page(item)
            if result['status'] == 'success':
                logger.info(f"Successfully created task: {item.get('task')}")
            else:
                logger.error(f"Failed to create task: {item.get('task')} - {result.get('error')}")
            results.append({
                "task": item['task'],
                "assignee": item.get('assignee', 'Unassigned'),
                "result": result
            })
        return results
    
    def get_database_properties(self) -> Dict:
        """
        Retrieve database schema to verify property names.
        
        Returns:
            Database properties
        """
        url = f"{self.base_url}/databases/{self.database_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('properties', {})
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e)
            }
