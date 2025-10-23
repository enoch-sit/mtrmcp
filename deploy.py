#!/usr/bin/env python3
"""
MTR MCP Server Deployment Script
================================

This script provides easy deployment options for the MTR MCP server
with FastAPI integration.

Usage:
    python deploy.py [command] [options]

Commands:
    standalone    - Run standalone MCP server
    fastapi       - Run FastAPI with integrated MCP
    docker        - Build and run Docker container
    docker-compose - Run with Docker Compose
    install       - Install dependencies
    test          - Run all tests
    
Examples:
    python deploy.py standalone --port 8001
    python deploy.py fastapi --port 8000
    python deploy.py docker --build
    python deploy.py test
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command and handle errors"""
    print(f"🔧 Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_requirements():
    """Check if required files exist"""
    required_files = [
        'requirements.txt',
        'mcp_server.py',
        'fastapi_integration.py'
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing required files: {', '.join(missing)}")
        return False
    
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    # Check if virtual environment exists
    venv_path = Path('.venv')
    if not venv_path.exists():
        print("🔧 Creating virtual environment...")
        run_command(f"{sys.executable} -m venv .venv")
    
    # Install dependencies
    if os.name == 'nt':  # Windows
        pip_command = ".venv\\Scripts\\pip"
        python_command = ".venv\\Scripts\\python"
    else:  # Unix-like
        pip_command = ".venv/bin/pip"
        python_command = ".venv/bin/python"
    
    run_command(f"{pip_command} install --upgrade pip")
    run_command(f"{pip_command} install -r requirements.txt")
    
    print("✅ Dependencies installed successfully!")
    return python_command


def run_standalone(port=8001):
    """Run standalone MCP server"""
    print(f"🚀 Starting standalone MCP server on port {port}")
    
    if not check_requirements():
        return
    
    run_command(f"python fastapi_integration.py standalone {port}")


def run_fastapi(port=8000):
    """Run FastAPI with integrated MCP server"""
    print(f"🌐 Starting FastAPI with MCP integration on port {port}")
    
    if not check_requirements():
        return
    
    run_command(f"python fastapi_integration.py fastapi {port}")


def run_docker(build=False):
    """Run with Docker"""
    print("🐳 Running with Docker...")
    
    if not Path('Dockerfile').exists():
        print("❌ Dockerfile not found")
        return
    
    if build:
        print("🔨 Building Docker image...")
        run_command("docker build -t mtr-mcp-server .")
    
    print("🚀 Starting Docker container...")
    run_command("docker run -p 8000:8000 -p 8001:8001 --name mtr-mcp mtr-mcp-server")


def run_docker_compose(profile=None):
    """Run with Docker Compose"""
    print("🐳 Running with Docker Compose...")
    
    if not Path('docker-compose.yml').exists():
        print("❌ docker-compose.yml not found")
        return
    
    command = "docker-compose up"
    if profile:
        command += f" --profile {profile}"
    
    run_command(command)


def run_tests():
    """Run all test files"""
    print("🧪 Running test suite...")
    
    test_files = [
        'test_01_aws_bedrock.py',
        'test_02_agent.py', 
        'test_03_mcp.py',
        'test_04_decoder_structured.py'
    ]
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n📋 Running {test_file}...")
            result = run_command(f"python {test_file}", check=False)
            if result.returncode == 0:
                print(f"✅ {test_file} PASSED")
                passed += 1
            else:
                print(f"❌ {test_file} FAILED")
                failed += 1
        else:
            print(f"⚠️  {test_file} not found")
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")


def show_status():
    """Show current service status"""
    print("📊 Checking service status...")
    
    # Check if ports are in use
    try:
        import socket
        
        def check_port(port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        
        ports = [8000, 8001]
        for port in ports:
            status = "🟢 OPEN" if check_port(port) else "🔴 CLOSED"
            print(f"  Port {port}: {status}")
    
    except ImportError:
        print("  Cannot check port status (socket module not available)")
    
    # Check Docker containers
    result = run_command("docker ps --filter name=mtr-mcp --format 'table {{.Names}}\t{{.Status}}'", check=False)
    if result.returncode == 0 and result.stdout.strip():
        print("\n🐳 Docker containers:")
        print(result.stdout)


def main():
    parser = argparse.ArgumentParser(description="MTR MCP Server Deployment Script")
    parser.add_argument('command', choices=[
        'standalone', 'fastapi', 'docker', 'docker-compose', 
        'install', 'test', 'status'
    ], help='Command to run')
    
    parser.add_argument('--port', type=int, help='Port number to use')
    parser.add_argument('--build', action='store_true', help='Build Docker image')
    parser.add_argument('--profile', type=str, help='Docker Compose profile')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 MTR MCP Server Deployment")
    print("=" * 60)
    
    if args.command == 'standalone':
        port = args.port or 8001
        run_standalone(port)
    
    elif args.command == 'fastapi':
        port = args.port or 8000
        run_fastapi(port)
    
    elif args.command == 'docker':
        run_docker(build=args.build)
    
    elif args.command == 'docker-compose':
        run_docker_compose(profile=args.profile)
    
    elif args.command == 'install':
        install_dependencies()
    
    elif args.command == 'test':
        run_tests()
    
    elif args.command == 'status':
        show_status()
    
    print("\n✅ Command completed!")


if __name__ == "__main__":
    main()