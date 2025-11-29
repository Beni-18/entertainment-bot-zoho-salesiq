#!/usr/bin/env python3
"""
Zoho SalesIQ Bot API Push Workflow
Automated development workflow for pushing bot script updates via REST API
"""

import requests
import json
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path

class ZohoBotPusher:
    """Handle bot script updates via Zoho SalesIQ REST API"""
    
    OAUTH_TOKEN_URL = "https://www.zohoapis.com/oauth/v2/token"
    BOT_API_BASE = "https://salesiq.zoho.com/api/v2"
    
    def __init__(self, org_id, client_id, client_secret, refresh_token, bot_id):
        self.org_id = org_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.bot_id = bot_id
        self.access_token = None
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def refresh_access_token(self):
        """Get new access token using refresh token"""
        print("[*] Refreshing OAuth access token...")
        
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(self.OAUTH_TOKEN_URL, data=payload)
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            print(f"[+] Token refreshed successfully")
            return True
        except Exception as e:
            print(f"[-] Token refresh failed: {e}")
            return False
    
    def get_current_script(self):
        """Retrieve current bot script from Zoho"""
        print(f"[*] Retrieving current bot script (ID: {self.bot_id})...")
        
        if not self.access_token:
            print("[-] No access token available")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.BOT_API_BASE}/bots/{self.bot_id}/script"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            script = data.get("script", "")
            print(f"[+] Current script retrieved ({len(script)} chars)")
            return script
        except Exception as e:
            print(f"[-] Failed to get current script: {e}")
            return None
    
    def backup_script(self, script_content):
        """Create backup of current script"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"bot_{self.bot_id}_backup_{timestamp}.dlz"
        
        try:
            with open(backup_file, 'w') as f:
                f.write(script_content)
            print(f"[+] Backup created: {backup_file}")
            return str(backup_file)
        except Exception as e:
            print(f"[-] Backup failed: {e}")
            return None
    
    def push_script(self, script_file):
        """Push new bot script to Zoho"""
        print(f"[*] Reading script from {script_file}...")
        
        try:
            with open(script_file, 'r') as f:
                new_script = f.read()
            print(f"[+] Script loaded ({len(new_script)} chars)")
        except Exception as e:
            print(f"[-] Failed to read script file: {e}")
            return False
        
        # Get current script for backup
        current_script = self.get_current_script()
        if not current_script:
            print("[-] Could not retrieve current script for backup")
            return False
        
        backup_path = self.backup_script(current_script)
        if not backup_path:
            print("[-] Backup creation failed, aborting push")
            return False
        
        print(f"[*] Pushing updated script to Zoho...")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "script": new_script
        }
        
        url = f"{self.BOT_API_BASE}/bots/{self.bot_id}/script"
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201, 204]:
                print(f"[+] Script pushed successfully (Status: {response.status_code})")
                print(f"[+] Backup file: {backup_path}")
                return True
            else:
                print(f"[-] Push failed with status {response.status_code}")
                print(f"    Response: {response.text}")
                print(f"[!] Attempting rollback...")
                self.rollback_script(backup_path, current_script)
                return False
        except Exception as e:
            print(f"[-] Push request failed: {e}")
            print(f"[!] Attempting rollback...")
            self.rollback_script(backup_path, current_script)
            return False
    
    def rollback_script(self, backup_file, backup_script_content):
        """Rollback to previous script version"""
        print(f"[!] Rolling back to backup: {backup_file}")
        
        if not self.access_token:
            print("[-] No access token for rollback")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "script": backup_script_content
        }
        
        url = f"{self.BOT_API_BASE}/bots/{self.bot_id}/script"
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            if response.status_code in [200, 201, 204]:
                print(f"[+] Rollback successful!")
                return True
            else:
                print(f"[-] Rollback failed: {response.text}")
                return False
        except Exception as e:
            print(f"[-] Rollback error: {e}")
            return False
    
    def test_connection(self):
        """Test API connection"""
        print("[*] Testing API connection...")
        
        if not self.refresh_access_token():
            return False
        
        script = self.get_current_script()
        if script:
            print("[+] API connection successful!")
            return True
        else:
            print("[-] API connection failed")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Zoho SalesIQ Bot API Push Workflow"
    )
    
    parser.add_argument("--org-id", required=True, help="Zoho Organization ID")
    parser.add_argument("--client-id", required=True, help="OAuth Client ID")
    parser.add_argument("--client-secret", required=True, help="OAuth Client Secret")
    parser.add_argument("--refresh-token", required=True, help="OAuth Refresh Token")
    parser.add_argument("--bot-id", required=True, help="Bot ID")
    parser.add_argument("--script", required=True, help="Path to bot script file")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--no-rollback", action="store_true", help="Disable auto-rollback on failure")
    
    args = parser.parse_args()
    
    pusher = ZohoBotPusher(
        org_id=args.org_id,
        client_id=args.client_id,
        client_secret=args.client_secret,
        refresh_token=args.refresh_token,
        bot_id=args.bot_id
    )
    
    if args.test:
        success = pusher.test_connection()
        sys.exit(0 if success else 1)
    
    if not pusher.refresh_access_token():
        print("[-] Failed to get access token")
        sys.exit(1)
    
    success = pusher.push_script(args.script)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
