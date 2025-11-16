"""
Performance Optimizer - Fixes slowness issues
"""

import pygetwindow as gw
import psutil
import time
import os

def diagnose_performance_issues():
    """Diagnose what's causing slowness"""
    print("=== PERFORMANCE DIAGNOSIS ===")

    issues_found = []
    solutions = []

    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_percent}%")

    if cpu_percent > 80:
        issues_found.append("High CPU usage")
        solutions.append("Close unnecessary programs")

    # Check memory usage
    memory = psutil.virtual_memory()
    print(f"Memory Usage: {memory.percent}%")

    if memory.percent > 85:
        issues_found.append("High memory usage")
        solutions.append("Close memory-intensive applications")

    # Check number of open windows
    windows = gw.getAllWindows()
    visible_windows = [w for w in windows if w.visible and w.title.strip()]
    print(f"Open Windows: {len(visible_windows)}")

    if len(visible_windows) > 20:
        issues_found.append("Too many open windows")
        solutions.append("Close unnecessary windows")

    # Check for resource-heavy processes
    heavy_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if proc.info['cpu_percent'] > 5 or proc.info['memory_percent'] > 5:
                heavy_processes.append(proc.info)
        except:
            pass

    print(f"Resource-heavy processes: {len(heavy_processes)}")

    if len(heavy_processes) > 10:
        issues_found.append("Too many background processes")
        solutions.append("End unnecessary background processes")

    print(f"\nISSUES FOUND: {len(issues_found)}")
    for issue in issues_found:
        print(f"  - {issue}")

    print(f"\nSOLUTIONS:")
    for solution in solutions:
        print(f"  - {solution}")

    return issues_found, solutions

def optimize_for_speed():
    """Automatically optimize system for speed"""
    print("\n=== AUTOMATIC OPTIMIZATION ===")

    optimizations = 0

    # Close unnecessary windows
    target_windows = ["Dark War", "BlueStacks", "Bot Control"]
    windows = gw.getAllWindows()

    for window in windows:
        if (window.visible and window.title.strip() and
            not any(target in window.title for target in target_windows) and
            "Desktop" not in window.title and
            "Program Manager" not in window.title):

            try:
                # Don't close critical system windows
                if window.title not in ["Settings", "Task Manager", "File Explorer"]:
                    window.minimize()  # Minimize instead of closing
                    optimizations += 1
            except:
                pass

    print(f"Minimized {optimizations} non-essential windows")

    # Set high priority for bot process
    try:
        current_process = psutil.Process()
        current_process.nice(psutil.HIGH_PRIORITY_CLASS)
        print("Set bot process to high priority")
        optimizations += 1
    except:
        print("Could not set high priority (requires admin)")

    print(f"Applied {optimizations} optimizations")
    return optimizations

def create_speed_config():
    """Create optimized configuration for maximum speed"""
    speed_config = {
        "click_delay": 0.01,          # Minimum click delay
        "cycle_delay": 0.05,          # Minimum cycle delay
        "actions_per_cycle": 10,      # Maximum actions
        "screenshot_delay": 0.01,     # Minimum screenshot delay
        "window_focus_delay": 0.01,   # Minimum focus delay
        "max_threads": 4,             # Multiple threads
        "aggressive_mode": True       # Aggressive optimization
    }

    with open("speed_config.json", "w") as f:
        import json
        json.dump(speed_config, f, indent=2)

    print("Created speed_config.json with aggressive settings")
    return speed_config

def monitor_performance(duration=30):
    """Monitor performance for specified duration"""
    print(f"\n=== MONITORING PERFORMANCE ({duration}s) ===")

    start_time = time.time()
    samples = []

    while time.time() - start_time < duration:
        sample = {
            "time": time.time() - start_time,
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "processes": len(psutil.pids())
        }
        samples.append(sample)
        time.sleep(1)

    # Analyze results
    avg_cpu = sum(s["cpu"] for s in samples) / len(samples)
    avg_memory = sum(s["memory"] for s in samples) / len(samples)

    print(f"Average CPU: {avg_cpu:.1f}%")
    print(f"Average Memory: {avg_memory:.1f}%")
    print(f"Process count: {samples[-1]['processes']}")

    # Performance rating
    if avg_cpu < 30 and avg_memory < 70:
        rating = "EXCELLENT"
    elif avg_cpu < 50 and avg_memory < 80:
        rating = "GOOD"
    elif avg_cpu < 70 and avg_memory < 90:
        rating = "FAIR"
    else:
        rating = "POOR"

    print(f"Performance Rating: {rating}")
    return rating

def fix_common_slowness_issues():
    """Fix the most common causes of bot slowness"""
    print("\n=== FIXING COMMON SLOWNESS ISSUES ===")

    fixes_applied = []

    # 1. Disable Windows animations
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Control Panel\Desktop\WindowMetrics",
                           0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "MinAnimate", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key)
        fixes_applied.append("Disabled Windows animations")
    except:
        pass

    # 2. Set PyAutoGUI settings for speed
    import pyautogui
    pyautogui.PAUSE = 0.01  # Minimum delay between PyAutoGUI calls
    pyautogui.FAILSAFE = False  # Disable failsafe for speed
    fixes_applied.append("Optimized PyAutoGUI settings")

    # 3. Priority process adjustment
    try:
        import subprocess
        subprocess.run(["wmic", "process", "where", "name='python.exe'",
                       "CALL", "setpriority", "128"],
                      capture_output=True, check=False)
        fixes_applied.append("Increased Python process priority")
    except:
        pass

    print(f"Applied {len(fixes_applied)} performance fixes:")
    for fix in fixes_applied:
        print(f"  - {fix}")

    return fixes_applied

if __name__ == "__main__":
    print("PERFORMANCE OPTIMIZER")
    print("This tool will diagnose and fix bot slowness")
    print()

    # Diagnose issues
    issues, solutions = diagnose_performance_issues()

    # Offer solutions
    if issues:
        print("\nWould you like to apply automatic optimizations? (y/n)")
        choice = input().lower()

        if choice == 'y':
            optimize_for_speed()
            fix_common_slowness_issues()
            create_speed_config()

            print("\nTesting performance after optimization...")
            rating = monitor_performance(10)

            if rating in ["EXCELLENT", "GOOD"]:
                print("Optimization successful!")
            else:
                print("Further manual optimization may be needed")
    else:
        print("No performance issues detected!")

    print("\nPerformance optimization complete!")