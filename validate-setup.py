#!/usr/bin/env python3
"""
Validate Rhino AI setup
Checks: files, dependencies, config, docker
"""
import os
import sys
import subprocess
from pathlib import Path

def check_file(path, description):
    """Check if file exists"""
    if Path(path).exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {path}")
        return False

def check_command(cmd, description):
    """Check if command is available"""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        print(f"✅ {description} installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ {description} NOT installed")
        return False

def check_env_file():
    """Check .env file"""
    if not Path(".env").exists():
        print("⚠️  .env file not found")
        print("   Run: cp sample.env .env")
        print("   Then edit .env and add your API key")
        return False
    
    with open(".env") as f:
        content = f.read()
        
    if "your-key-here" in content or "sk-..." in content:
        print("⚠️  .env file exists but API key not configured")
        print("   Edit .env and add your actual API key")
        return False
    
    print("✅ .env file configured")
    return True

def main():
    print("🦏 Rhino AI - Setup Validation")
    print("=" * 50)
    print()
    
    checks = []
    
    # Check critical files
    print("📁 Checking files...")
    checks.append(check_file("README.md", "README"))
    checks.append(check_file("docker-compose.yml", "Docker Compose config"))
    checks.append(check_file("sample.env", "Sample environment file"))
    checks.append(check_file("rubrica_government.json", "Rubrica JSON"))
    checks.append(check_file("backend/main.py", "Backend main"))
    checks.append(check_file("backend/requirements.txt", "Backend requirements"))
    checks.append(check_file("frontend/package.json", "Frontend package.json"))
    checks.append(check_file("frontend/src/App.jsx", "Frontend App"))
    print()
    
    # Check commands
    print("🔧 Checking dependencies...")
    checks.append(check_command("docker", "Docker"))
    checks.append(check_command("docker-compose", "Docker Compose"))
    checks.append(check_command("python", "Python"))
    checks.append(check_command("node", "Node.js"))
    print()
    
    # Check .env
    print("⚙️  Checking configuration...")
    checks.append(check_env_file())
    print()
    
    # Summary
    print("=" * 50)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print()
        print("🚀 Ready to start!")
        print("   Run: docker-compose up --build")
        print("   Or: ./quick-start.sh (Linux/Mac)")
        print("   Or: quick-start.bat (Windows)")
        return 0
    else:
        print(f"❌ Some checks failed ({passed}/{total})")
        print()
        print("Please fix the issues above before starting.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
