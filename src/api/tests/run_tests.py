#!/usr/bin/env python3
"""
Test runner script for TalkShop API tests
"""
import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run the API tests"""
    # Change to project root directory
    project_root = Path(__file__).parent.parent.parent.parent
    os.chdir(project_root)
    
    print("Running TalkShop API Tests...")
    print("=" * 50)
    
    # Run pytest
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "src/api/tests/",
            "-v",
            "--tb=short",
            "--asyncio-mode=auto"
        ], check=False)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ All tests passed!")
        else:
            print("\n" + "=" * 50)
            print("❌ Some tests failed!")
            sys.exit(result.returncode)
            
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()