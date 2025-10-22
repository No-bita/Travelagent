"""
Configuration Validation Script
Validates that all services use centralized configuration
"""

import os
import sys
import ast
import re
from pathlib import Path

def find_hardcoded_values():
    """Find hardcoded values in the codebase"""
    hardcoded_issues = []
    
    # Patterns to look for
    patterns = [
        (r'"[^"]*://[^"]*"', "Hardcoded URLs"),
        (r'\b\d{4,}\b', "Hardcoded large numbers (likely timeouts/limits)"),
        (r'localhost:\d+', "Hardcoded localhost URLs"),
        (r'redis://[^"]*', "Hardcoded Redis URLs"),
        (r'postgresql://[^"]*', "Hardcoded PostgreSQL URLs"),
        (r'timeout=\d+', "Hardcoded timeouts"),
        (r'maxsize=\d+', "Hardcoded cache sizes"),
        (r'ttl=\d+', "Hardcoded TTL values"),
        (r'limit=\d+', "Hardcoded connection limits"),
    ]
    
    # Files to check
    files_to_check = [
        "services/flight_service_async.py",
        "core/state_manager_async.py", 
        "core/nlp_engine_async.py",
        "routers/chat.py",
        "routers/healthcheck.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern, issue_type in patterns:
                        if re.search(pattern, line) and 'settings.' not in line:
                            # Skip comments and docstrings
                            if not line.strip().startswith('#') and not line.strip().startswith('"""'):
                                hardcoded_issues.append({
                                    'file': file_path,
                                    'line': i,
                                    'content': line.strip(),
                                    'issue': issue_type
                                })
    
    return hardcoded_issues

def check_config_usage():
    """Check if services are using centralized configuration"""
    config_issues = []
    
    # Files that should use settings
    files_to_check = [
        "services/flight_service_async.py",
        "core/state_manager_async.py",
        "core/nlp_engine_async.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Check if file imports settings
                if 'from config import settings' not in content and 'import settings' not in content:
                    config_issues.append({
                        'file': file_path,
                        'issue': 'Missing settings import'
                    })
                
                # Check for hardcoded values that should use settings
                hardcoded_patterns = [
                    (r'ClientSession\(\s*$', 'Should use settings for HTTP configuration'),
                    (r'TTLCache\(\s*$', 'Should use settings for cache configuration'),
                    (r'ThreadPoolExecutor\(\s*$', 'Should use settings for thread pool configuration'),
                    (r'redis\.from_url\(\s*$', 'Should use settings for Redis configuration'),
                ]
                
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    for pattern, issue in hardcoded_patterns:
                        if re.search(pattern, line) and 'settings.' not in line:
                            # Check if the next few lines contain settings usage
                            context_lines = lines[i-1:i+5]  # Check surrounding lines
                            context_text = ' '.join(context_lines)
                            if 'settings.' not in context_text:
                                config_issues.append({
                                    'file': file_path,
                                    'line': i,
                                    'content': line.strip(),
                                    'issue': issue
                                })
    
    return config_issues

def validate_environment_configs():
    """Validate environment-specific configurations"""
    issues = []
    
    # Check if environment configs exist
    env_configs = [
        "config/development.py",
        "config/production.py", 
        "config/testing.py",
        "config/factory.py"
    ]
    
    for config_file in env_configs:
        if not os.path.exists(config_file):
            issues.append({
                'file': config_file,
                'issue': 'Missing environment configuration file'
            })
    
    return issues

def main():
    """Main validation function"""
    print("🔍 Configuration Validation Report")
    print("=" * 50)
    
    # Find hardcoded values
    print("\n1. 🔍 Checking for hardcoded values...")
    hardcoded_issues = find_hardcoded_values()
    
    if hardcoded_issues:
        print(f"❌ Found {len(hardcoded_issues)} hardcoded values:")
        for issue in hardcoded_issues:
            print(f"  📁 {issue['file']}:{issue['line']} - {issue['issue']}")
            print(f"     {issue['content']}")
    else:
        print("✅ No hardcoded values found!")
    
    # Check config usage
    print("\n2. 🔧 Checking configuration usage...")
    config_issues = check_config_usage()
    
    if config_issues:
        print(f"❌ Found {len(config_issues)} configuration issues:")
        for issue in config_issues:
            if 'line' in issue:
                print(f"  📁 {issue['file']}:{issue['line']} - {issue['issue']}")
                print(f"     {issue['content']}")
            else:
                print(f"  📁 {issue['file']} - {issue['issue']}")
    else:
        print("✅ All services use centralized configuration!")
    
    # Validate environment configs
    print("\n3. 🌍 Checking environment configurations...")
    env_issues = validate_environment_configs()
    
    if env_issues:
        print(f"❌ Found {len(env_issues)} environment configuration issues:")
        for issue in env_issues:
            print(f"  📁 {issue['file']} - {issue['issue']}")
    else:
        print("✅ All environment configurations present!")
    
    # Summary
    total_issues = len(hardcoded_issues) + len(config_issues) + len(env_issues)
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Hardcoded values: {len(hardcoded_issues)}")
    print(f"Configuration issues: {len(config_issues)}")
    print(f"Environment issues: {len(env_issues)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\n🎉 All configuration validation passed!")
        return True
    else:
        print(f"\n⚠️  Found {total_issues} configuration issues to fix")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
