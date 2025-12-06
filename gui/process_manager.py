# -*- coding: utf-8 -*-
import os
import time
import platform
import subprocess
import psutil

# Use relative imports
from utils import info, error, warning, get_antigravity_executable_path, open_uri

def is_process_running(process_name=None):
    """Check if Antigravity process is running
    
    Use cross-platform detection method:
    - macOS: Check if path contains Antigravity.app
    - Linux: Check if process name or path contains antigravity
    """
    system = platform.system()
    
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            process_name_lower = proc.info['name'].lower() if proc.info['name'] else ""
            exe_path = proc.info.get('exe', '').lower() if proc.info.get('exe') else ""
            
            # Cross-platform detection
            is_antigravity = False
            
            if system == "Darwin":
                # macOS: Check if path contains Antigravity.app
                is_antigravity = 'antigravity.app' in exe_path
            else:
                # Linux: Check if process name or path contains antigravity
                is_antigravity = (process_name_lower == 'antigravity' or 
                                 'antigravity' in exe_path)
            
            if is_antigravity:
                return True
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def close_antigravity(timeout=10, force_kill=True):
    """Gracefully close all Antigravity processes
    
    Closing strategy (3 stages, cross-platform):
    1. Platform-specific graceful exit method
       - macOS: AppleScript
       - Linux: SIGTERM
    2. Gentle termination (SIGTERM/TerminateProcess) - Give process chance to cleanup
    3. Force kill (SIGKILL/taskkill /F) - Last resort
    """
    info("Attempting to close Antigravity...")
    system = platform.system()
    
    # Platform check
    if system not in ["Darwin", "Linux"]:
        warning(f"Unknown platform: {system}, will try generic method")
    
    try:
        # Stage 1: Platform-specific graceful exit
        if system == "Darwin":
            # macOS: Use AppleScript
            info("Attempting graceful exit via AppleScript...")
            try:
                result = subprocess.run(
                    ["osascript", "-e", 'tell application "Antigravity" to quit'],
                    capture_output=True,
                    timeout=3
                )
                if result.returncode == 0:
                    info("Exit request sent, waiting for app response...")
                    time.sleep(2)
            except Exception as e:
                warning(f"AppleScript exit failed: {e}, will use other methods")
        
        # Linux needs no special handling, use SIGTERM directly
        
        # Check and collect running processes
        target_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                process_name_lower = proc.info['name'].lower() if proc.info['name'] else ""
                exe_path = proc.info.get('exe', '').lower() if proc.info.get('exe') else ""
                
                # Exclude own process
                if proc.pid == os.getpid():
                    continue
                
                # Exclude all processes in current app directory (prevent killing self and subprocesses)
                # In PyInstaller packaged environment, sys.executable points to exe file
                # In dev environment, it points to python.exe
                try:
                    import sys
                    current_exe = sys.executable
                    current_dir = os.path.dirname(os.path.abspath(current_exe)).lower()
                    if exe_path and current_dir in exe_path:
                        # print(f"DEBUG: Skipping process in current dir: {proc.info['name']}")
                        continue
                except:
                    pass

                # Cross-platform detection: Check process name or executable path
                is_antigravity = False
                
                if system == "Darwin":
                    # macOS: Check if path contains Antigravity.app
                    is_antigravity = 'antigravity.app' in exe_path
                else:
                    # Linux: Check if process name or path contains antigravity
                    is_antigravity = (process_name_lower == 'antigravity' or 
                                     'antigravity' in exe_path)
                
                if is_antigravity:
                    info(f"Found target process: {proc.info['name']} ({proc.pid}) - {exe_path}")
                    target_processes.append(proc)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not target_processes:
            info("All Antigravity processes closed normally")
            return True
        
        info(f"Detected {len(target_processes)} processes still running")

        # Stage 2: Gently request process termination (SIGTERM)
        info("Sending termination signal (SIGTERM)...")
        for proc in target_processes:
            try:
                if proc.is_running():
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                continue
            except Exception as e:
                continue

        # Wait for process natural termination
        info(f"Waiting for process exit (max {timeout} seconds)...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            still_running = []
            for proc in target_processes:
                try:
                    if proc.is_running():
                        still_running.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not still_running:
                info("All Antigravity processes closed normally")
                return True
                
            time.sleep(0.5)

        # Stage 3: Force kill stubborn processes (SIGKILL)
        if still_running:
            still_running_names = ", ".join([f"{p.info['name']}({p.pid})" for p in still_running])
            warning(f"Still {len(still_running)} processes not exited: {still_running_names}")
            
            if force_kill:
                info("Sending force kill signal (SIGKILL)...")
                for proc in still_running:
                    try:
                        if proc.is_running():
                            proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Final check
                time.sleep(1)
                final_check = []
                for proc in still_running:
                    try:
                        if proc.is_running():
                            final_check.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if not final_check:
                    info("All Antigravity processes have been terminated")
                    return True
                else:
                    final_list = ", ".join([f"{p.info['name']}({p.pid})" for p in final_check])
                    error(f"Unable to terminate processes: {final_list}")
                    return False
            else:
                error("Some processes failed to close, please close manually and retry")
                return False
                
        return True

    except Exception as e:
        error(f"Error occurred while closing Antigravity process: {str(e)}")
        return False

def start_antigravity(use_uri=True):
    """Start Antigravity
    
    Args:
        use_uri: Whether to use URI protocol to start (default True)
                 URI protocol is more reliable, no need to find executable path
    """
    info("Starting Antigravity...")
    system = platform.system()
    
    try:
        # Prioritize URI protocol start (cross-platform)
        if use_uri:
            info("Starting using URI protocol...")
            uri = "antigravity://oauth-success"
            
            if open_uri(uri):
                info("Antigravity URI start command sent")
                return True
            else:
                warning("URI start failed, attempting to use executable path...")
                # Continue to execute fallback plan below
        
        # Fallback plan: Start using executable path
        info("Starting using executable path...")
        if system == "Darwin":
            subprocess.Popen(["open", "-a", "Antigravity"])
        elif system == "Linux":
            subprocess.Popen(["antigravity"])
        
        info("Antigravity start command sent")
        return True
    except Exception as e:
        error(f"Error starting process: {e}")
        # If URI start failed, try using executable path
        if use_uri:
            warning("URI start failed, attempting to use executable path...")
            return start_antigravity(use_uri=False)
        return False
