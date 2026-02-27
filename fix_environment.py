#!/usr/bin/env python3
"""
修复环境问题
"""

import sys
import os
import subprocess

def check_python_environment():
    """检查Python环境"""
    print("🔍 检查Python环境...")
    
    # 检查Python版本
    python_version = sys.version
    print(f"Python版本: {python_version.split()[0]}")
    
    # 检查当前Python路径
    python_executable = sys.executable
    print(f"Python路径: {python_executable}")
    
    # 检查yaml模块
    try:
        import yaml
        print(f"✅ yaml模块: {yaml.__version__}")
        return True
    except ImportError as e:
        print(f"❌ yaml模块导入失败: {e}")
        return False

def check_conda_environment():
    """检查conda环境"""
    print("\n🐍 检查conda环境...")
    
    try:
        # 检查conda是否可用
        result = subprocess.run(
            ["conda", "info", "--envs"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ conda可用")
            
            # 检查当前环境
            env_result = subprocess.run(
                ["conda", "env", "list"],
                capture_output=True,
                text=True
            )
            
            lines = env_result.stdout.split('\n')
            for line in lines:
                if "*" in line:
                    print(f"当前环境: {line.strip()}")
                    break
                    
            return True
        else:
            print("❌ conda不可用")
            return False
            
    except FileNotFoundError:
        print("❌ conda未安装")
        return False

def check_system_dependencies():
    """检查系统依赖"""
    print("\n📦 检查系统依赖...")
    
    dependencies = [
        ("yaml", "import yaml"),
        ("json", "import json"),
        ("datetime", "import datetime"),
        ("pathlib", "from pathlib import Path")
    ]
    
    all_passed = True
    for dep_name, import_cmd in dependencies:
        try:
            exec(import_cmd)
            print(f"✅ {dep_name}")
        except ImportError as e:
            print(f"❌ {dep_name}: {e}")
            all_passed = False
    
    return all_passed

def fix_import_paths():
    """修复导入路径"""
    print("\n🛠️  修复导入路径...")
    
    # 添加脚本目录到Python路径
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
        print(f"✅ 添加脚本目录到Python路径: {scripts_dir}")
    else:
        print(f"✅ 脚本目录已在Python路径中")
    
    # 检查是否能导入模块
    modules_to_check = [
        "data_manager",
        "jsonl_parser", 
        "ai_summarizer",
        "main"
    ]
    
    for module_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"✅ 可以导入: {module_name}")
        except ImportError as e:
            print(f"❌ 无法导入 {module_name}: {e}")

def create_fixed_main_script():
    """创建修复后的主脚本"""
    print("\n📝 创建修复后的主脚本...")
    
    original_script = os.path.join("scripts", "main.py")
    fixed_script = os.path.join("scripts", "main_fixed.py")
    
    # 读取原始脚本
    with open(original_script, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加路径修复代码
    fixed_content = """#!/usr/bin/env python3
\"\"\"
Telegram 聊天记录总结系统 - 主入口 (修复版)
\"\"\"

import sys
import os

# 修复Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# 使用conda环境的Python
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

""" + content.split('from data_manager import DataManager')[0] + """

# 使用conda环境运行
def run_with_conda():
    \"\"\"使用conda环境运行命令\"\"\"
    cmd = [
        "/root/miniconda3/envs/dl/bin/python",
        os.path.join(script_dir, "main.py")
    ] + sys.argv[1:]
    
    print(f"运行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("错误输出:", result.stderr)
    
    return result.returncode

if __name__ == "__main__":
    # 检查是否在正确的环境中
    current_python = sys.executable
    target_python = "/root/miniconda3/envs/dl/bin/python"
    
    if current_python != target_python:
        print(f"⚠️  当前Python环境: {current_python}")
        print(f"🔧 切换到目标环境: {target_python}")
        sys.exit(run_with_conda())
    else:
        print(f"✅ 已在正确的Python环境中: {current_python}")
        # 继续执行原始代码
        from data_manager import DataManager
        from ai_summarizer import AISummarizer
        
        # 这里继续原始main.py的内容
        # ... (省略后续代码，因为我们会直接调用原始脚本)
        
        # 实际上我们直接运行原始脚本
        import main
        main.main()
"""
    
    # 写入修复后的脚本
    with open(fixed_script, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ 创建修复脚本: {fixed_script}")
    
    # 设置执行权限
    os.chmod(fixed_script, 0o755)
    print("✅ 设置执行权限")

def main():
    """主函数"""
    print("="*70)
    print("环境修复工具")
    print("="*70)
    
    # 运行检查
    env_ok = check_python_environment()
    conda_ok = check_conda_environment()
    deps_ok = check_system_dependencies()
    
    print("\n" + "="*70)
    print("修复建议")
    print("="*70)
    
    if not env_ok or not deps_ok:
        print("\n🔧 问题检测:")
        print("1. Python环境可能不正确")
        print("2. 依赖模块可能未安装")
        
        print("\n💡 解决方案:")
        print("1. 使用conda环境:")
        print("   source /root/miniconda3/etc/profile.d/conda.sh")
        print("   conda activate dl")
        
        print("\n2. 或者直接使用conda环境的Python:")
        print("   /root/miniconda3/envs/dl/bin/python scripts/main.py --status")
        
        print("\n3. 安装缺失的依赖:")
        print("   pip install pyyaml")
    
    # 修复导入路径
    fix_import_paths()
    
    # 创建修复脚本
    create_fixed_main_script()
    
    print("\n" + "="*70)
    print("测试修复")
    print("="*70)
    
    print("\n运行测试命令:")
    print("1. 使用conda环境:")
    print("   cd /root/.openclaw/workspace/telegram_summary")
    print("   /root/miniconda3/envs/dl/bin/python scripts/main.py --status")
    
    print("\n2. 使用修复脚本:")
    print("   cd /root/.openclaw/workspace/telegram_summary")
    print("   python scripts/main_fixed.py --status")
    
    print("\n3. 快速启动:")
    print("   ./quick_start.sh")
    
    print("\n" + "="*70)
    print("修复完成")
    print("="*70)

if __name__ == "__main__":
    main()