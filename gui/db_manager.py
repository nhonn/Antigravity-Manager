# -*- coding: utf-8 -*-
import sqlite3
import json
import os
from datetime import datetime

# Use relative imports
from utils import info, error, warning, debug, get_antigravity_db_paths

# List of keys to backup
KEYS_TO_BACKUP = [
    "antigravityAuthStatus",
    "jetskiStateSync.agentManagerInitState",
]



def get_db_connection(db_path):
    """Get database connection"""
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        error_msg = str(e)
        if "locked" in error_msg.lower():
            error(f"Database locked: {e}")
            error("Tip: Please ensure Antigravity app is fully closed")
        else:
            error(f"Failed to connect to database: {e}")
        return None
    except Exception as e:
        error(f"Unexpected error when connecting to database: {e}")
        return None

def backup_account(email, backup_file_path):
    """Backup account data to JSON file"""
    db_paths = get_antigravity_db_paths()
    if not db_paths:
        error("Antigravity database path not found")
        return False
    
    db_path = db_paths[0]
    if not db_path.exists():
        error(f"Database file does not exist: {db_path}")
        return False
        
    info(f"Backing up data from database: {db_path}")
    conn = get_db_connection(db_path)
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        data_map = {}
        
        # 1. Extract normal keys
        for key in KEYS_TO_BACKUP:
            cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                data_map[key] = row[0]
                debug(f"Backing up field: {key}")
            else:
                debug(f"Field does not exist: {key}")
        

        
        # 3. Add metadata
        data_map["account_email"] = email
        data_map["backup_time"] = datetime.now().isoformat()
        
        # 4. Write to file
        with open(backup_file_path, 'w', encoding='utf-8') as f:
            json.dump(data_map, f, ensure_ascii=False, indent=2)
            
        info(f"Backup successful: {backup_file_path}")
        return True
        
    except sqlite3.Error as e:
        error(f"Database query error: {e}")
        return False
    except Exception as e:
        error(f"Backup process error: {e}")
        return False
    finally:
        conn.close()

def restore_account(backup_file_path):
    """Restore account data from JSON file"""
    if not os.path.exists(backup_file_path):
        error(f"Backup file does not exist: {backup_file_path}")
        return False
        
    try:
        with open(backup_file_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
    except Exception as e:
        error(f"Failed to read backup file: {e}")
        return False
        
    db_paths = get_antigravity_db_paths()
    if not db_paths:
        error("Antigravity database path not found")
        return False
    
    # Usually there are two database files: state.vscdb and state.vscdb.backup
    # We need to restore both of them
    success_count = 0
    
    for db_path in db_paths:
        # Main database
        if _restore_single_db(db_path, backup_data):
            success_count += 1
            
        # Backup database (if exists)
        backup_db_path = db_path.with_suffix('.vscdb.backup')
        if backup_db_path.exists():
            if _restore_single_db(backup_db_path, backup_data):
                success_count += 1
                
    return success_count > 0

def _restore_single_db(db_path, backup_data):
    """Restore single database file"""
    if not db_path.exists():
        return False
        
    info(f"Restoring database: {db_path}")
    conn = get_db_connection(db_path)
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        restored_keys = []
        
        # 1. Restore normal keys
        for key in KEYS_TO_BACKUP:
            if key in backup_data:
                value = backup_data[key]
                # Ensure value is string
                if not isinstance(value, str):
                    value = json.dumps(value)
                    
                cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (key, value))
                restored_keys.append(key)
                debug(f"Restored field: {key}")

            
        conn.commit()
        info(f"Database restore completed: {db_path}")
        return True
        
    except sqlite3.Error as e:
        error(f"Database write error: {e}")
        return False
    except Exception as e:
        error(f"Restore process error: {e}")
        return False
    finally:
        conn.close()


def get_current_account_info():
    """Extract current account info from database (email etc.)"""
    db_paths = get_antigravity_db_paths()
    if not db_paths:
        return None
    
    db_path = db_paths[0]
    if not db_path.exists():
        return None
        
    conn = get_db_connection(db_path)
    if not conn:
        return None
        
    try:
        cursor = conn.cursor()
        
        # 1. Attempt to get from antigravityAuthStatus
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("antigravityAuthStatus",))
        row = cursor.fetchone()
        if row:
            try:
                # Attempt to parse JSON
                data = json.loads(row[0])
                if isinstance(data, dict):
                    if "email" in data:
                        return {"email": data["email"]}
                    # Sometimes it might be a token, or other structure, doing a simple traversal check here
                    for k, v in data.items():
                        if k.lower() == "email" and isinstance(v, str):
                            return {"email": v}
            except:
                pass

        # 2. Attempt to get from google.antigravity
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("google.antigravity",))
        row = cursor.fetchone()
        if row:
            try:
                data = json.loads(row[0])
                if isinstance(data, dict) and "email" in data:
                    return {"email": data["email"]}
            except:
                pass
                
        # 3. Attempt to get from antigravityUserSettings.allUserSettings
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("antigravityUserSettings.allUserSettings",))
        row = cursor.fetchone()
        if row:
            try:
                data = json.loads(row[0])
                if isinstance(data, dict) and "email" in data:
                    return {"email": data["email"]}
            except:
                pass
                
        return None
        
    except Exception as e:
        error(f"Error extracting account info: {e}")
        return None
    finally:
        conn.close()
