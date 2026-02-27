#!/usr/bin/env python3
"""
简单测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_manager import DataManager

def main():
    """主测试函数"""
    try:
        print("初始化数据管理器...")
        manager = DataManager("../config/config.yaml")
        
        print("\n测试收集每日数据...")
        daily_sessions = manager.collect_daily_data()
        print(f"找到 {len(daily_sessions)} 个当日会话")
        
        if daily_sessions:
            print("\n测试归档原始数据...")
            manager.archive_raw_data(daily_sessions, "daily")
            print("归档成功!")
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()