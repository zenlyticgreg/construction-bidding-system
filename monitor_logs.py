#!/usr/bin/env python3
"""
Log Monitor for PACE Application

This script monitors the application logs in real-time to help debug issues
and track user activity.
"""

import os
import time
import subprocess
from datetime import datetime
from pathlib import Path


def get_log_files():
    """Get all log files in the logs directory."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ Logs directory not found!")
        return []
    
    log_files = []
    for log_file in logs_dir.glob("*.log"):
        log_files.append(log_file)
    
    return log_files


def show_log_summary():
    """Show a summary of all log files."""
    log_files = get_log_files()
    
    if not log_files:
        print("❌ No log files found!")
        return
    
    print("📊 Log Files Summary")
    print("=" * 50)
    
    for log_file in log_files:
        try:
            size = log_file.stat().st_size
            modified = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if size == 0:
                status = "🟡 Empty"
            else:
                status = "🟢 Active"
            
            print(f"{status} {log_file.name}")
            print(f"   Size: {size:,} bytes")
            print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
        except Exception as e:
            print(f"❌ Error reading {log_file.name}: {e}")


def tail_log_file(log_file, lines=20):
    """Show the last N lines of a log file."""
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            print(f"📄 Last {len(last_lines)} lines of {log_file.name}")
            print("=" * 60)
            
            for line in last_lines:
                print(line.rstrip())
                
    except Exception as e:
        print(f"❌ Error reading {log_file}: {e}")


def monitor_logs_realtime(log_file=None):
    """Monitor logs in real-time."""
    if log_file is None:
        log_files = get_log_files()
        if not log_files:
            print("❌ No log files found!")
            return
        
        # Use the main app log by default
        log_file = next((f for f in log_files if "ui_app" in f.name), log_files[0])
    
    print(f"🔍 Monitoring {log_file.name} in real-time...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        # Use tail -f for real-time monitoring
        process = subprocess.Popen(
            ['tail', '-f', str(log_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        for line in process.stdout:
            print(line.rstrip())
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped")
        process.terminate()
    except Exception as e:
        print(f"❌ Error monitoring logs: {e}")


def search_logs(search_term, log_file=None):
    """Search for specific terms in log files."""
    log_files = get_log_files()
    
    if log_file:
        log_files = [f for f in log_files if log_file in f.name]
    
    if not log_files:
        print("❌ No log files found!")
        return
    
    print(f"🔍 Searching for '{search_term}' in log files...")
    print("=" * 60)
    
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                matching_lines = [line for line in lines if search_term.lower() in line.lower()]
                
                if matching_lines:
                    print(f"\n📄 Found {len(matching_lines)} matches in {log_file.name}:")
                    for line in matching_lines:
                        print(f"   {line.rstrip()}")
                        
        except Exception as e:
            print(f"❌ Error searching {log_file}: {e}")


def show_recent_activity(minutes=5):
    """Show recent activity from the last N minutes."""
    log_files = get_log_files()
    
    if not log_files:
        print("❌ No log files found!")
        return
    
    cutoff_time = time.time() - (minutes * 60)
    
    print(f"📈 Recent activity (last {minutes} minutes)")
    print("=" * 60)
    
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = []
                
                for line in lines:
                    # Try to parse timestamp from log line
                    try:
                        # Extract timestamp from log format
                        timestamp_str = line.split(' - ')[0]
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        if timestamp.timestamp() > cutoff_time:
                            recent_lines.append(line)
                    except:
                        continue
                
                if recent_lines:
                    print(f"\n📄 {len(recent_lines)} recent entries in {log_file.name}:")
                    for line in recent_lines[-10:]:  # Show last 10 recent entries
                        print(f"   {line.rstrip()}")
                        
        except Exception as e:
            print(f"❌ Error reading {log_file}: {e}")


def main():
    """Main function with interactive menu."""
    while True:
        print("\n🔍 PACE Log Monitor")
        print("=" * 30)
        print("1. Show log summary")
        print("2. View recent log entries")
        print("3. Monitor logs in real-time")
        print("4. Search logs")
        print("5. Show recent activity")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == '1':
            show_log_summary()
            
        elif choice == '2':
            log_files = get_log_files()
            if log_files:
                print("\nAvailable log files:")
                for i, log_file in enumerate(log_files):
                    print(f"{i+1}. {log_file.name}")
                
                try:
                    file_choice = int(input("Select log file (number): ")) - 1
                    if 0 <= file_choice < len(log_files):
                        tail_log_file(log_files[file_choice])
                    else:
                        print("❌ Invalid selection!")
                except ValueError:
                    print("❌ Please enter a valid number!")
            else:
                print("❌ No log files found!")
                
        elif choice == '3':
            log_files = get_log_files()
            if log_files:
                print("\nAvailable log files:")
                for i, log_file in enumerate(log_files):
                    print(f"{i+1}. {log_file.name}")
                
                try:
                    file_choice = int(input("Select log file to monitor (number): ")) - 1
                    if 0 <= file_choice < len(log_files):
                        monitor_logs_realtime(log_files[file_choice])
                    else:
                        print("❌ Invalid selection!")
                except ValueError:
                    print("❌ Please enter a valid number!")
            else:
                print("❌ No log files found!")
                
        elif choice == '4':
            search_term = input("Enter search term: ").strip()
            if search_term:
                search_logs(search_term)
            else:
                print("❌ Please enter a search term!")
                
        elif choice == '5':
            try:
                minutes = int(input("Show activity from last N minutes (default 5): ") or "5")
                show_recent_activity(minutes)
            except ValueError:
                print("❌ Please enter a valid number!")
                
        elif choice == '6':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice! Please select 1-6.")


if __name__ == "__main__":
    main() 