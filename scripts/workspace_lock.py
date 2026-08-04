#!/usr/bin/env python3
"""Workspace Lock Manager - Prevents concurrent modification conflicts."""

import sys
import time
import fcntl
from pathlib import Path
from typing import Optional


class WorkspaceLock:
    """File-based lock manager for workspace protection."""
    
    LOCK_TIMEOUT = 60  # seconds
    LOCK_SUFFIX = ".workspace.lock"
    
    def __init__(self, workspace_dir: Path):
        """Initialize lock manager.
        
        Args:
            workspace_dir: Path to workspace directory
        """
        self.workspace_dir = workspace_dir
        self.lock_file = workspace_dir / f".{self.LOCK_SUFFIX}"
    
    def acquire(self, timeout: Optional[int] = None) -> bool:
        """Acquire workspace lock.
        
        Args:
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if lock acquired, False otherwise
        """
        if timeout is None:
            timeout = self.LOCK_TIMEOUT
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Create lock file if it doesn't exist
                self.lock_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Try to acquire lock
                lock_fd = open(self.lock_file, 'w')
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                
                # Write lock info
                lock_info = {
                    "pid": os.getpid(),
                    "acquired_at": time.time(),
                    "host": "unknown"  # Could add hostname here
                }
                lock_fd.write(json.dumps(lock_info, indent=2))
                lock_fd.flush()
                
                return True
                
            except (IOError, OSError):
                # Lock already held, wait and retry
                time.sleep(0.5)
        
        return False
    
    def release(self) -> None:
        """Release workspace lock."""
        try:
            if self.lock_file.exists():
                lock_fd = open(self.lock_file, 'r')
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                lock_fd.close()
                self.lock_file.unlink()
        except (IOError, OSError):
            pass  # Lock may have already been released
    
    def is_locked(self) -> bool:
        """Check if workspace is currently locked.
        
        Returns:
            True if locked, False otherwise
        """
        if not self.lock_file.exists():
            return False
        
        try:
            lock_fd = open(self.lock_file, 'r')
            # Try to acquire lock without blocking
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
            return False
        except (IOError, OSError):
            return True
    
    def get_lock_info(self) -> Optional[dict]:
        """Get lock information.
        
        Returns:
            Lock info dict or None if not locked
        """
        if not self.lock_file.exists():
            return None
        
        try:
            content = self.lock_file.read_text()
            return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return None


if __name__ == "__main__":
    import argparse
    import json
    import os
    
    parser = argparse.ArgumentParser(description="Workspace Lock Manager")
    parser.add_argument("--workspace-dir", required=True, help="Path to workspace directory")
    parser.add_argument("--action", choices=["acquire", "release", "status"], required=True)
    
    args = parser.parse_args()
    
    workspace_dir = Path(args.workspace_dir)
    lock_manager = WorkspaceLock(workspace_dir)
    
    if args.action == "acquire":
        if lock_manager.acquire():
            print("✓ Lock acquired")
            sys.exit(0)
        else:
            print("✗ Failed to acquire lock (timeout)")
            sys.exit(1)
    
    elif args.action == "release":
        lock_manager.release()
        print("✓ Lock released")
    
    elif args.action == "status":
        if lock_manager.is_locked():
            info = lock_manager.get_lock_info()
            print(f"✗ Workspace is locked")
            if info:
                print(f"  PID: {info.get('pid')}")
                print(f"  Acquired: {info.get('acquired_at', 'unknown')}")
        else:
            print("✓ Workspace is unlocked")
