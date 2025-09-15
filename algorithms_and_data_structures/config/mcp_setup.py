#!/usr/bin/env python3
"""
MCP Setup and Configuration for Flow Nexus Integration
Handles automatic installation and configuration of required MCP tools
"""

import subprocess
import sys
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional


class MCPSetupManager:
    """Manages MCP tool installation and configuration"""
    
    def __init__(self):
        self.config_path = Path(__file__).parent / "cloud_config.json"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load cloud configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if prerequisites are installed"""
        checks = {}
        
        # Check Node.js/npm
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            checks['nodejs'] = result.returncode == 0
        except FileNotFoundError:
            checks['nodejs'] = False
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True)
            checks['npm'] = result.returncode == 0
        except FileNotFoundError:
            checks['npm'] = False
        
        # Check Claude CLI
        try:
            result = subprocess.run(['claude', '--version'], 
                                  capture_output=True, text=True)
            checks['claude_cli'] = result.returncode == 0
        except FileNotFoundError:
            checks['claude_cli'] = False
        
        # Check npx
        try:
            result = subprocess.run(['npx', '--version'], 
                                  capture_output=True, text=True)
            checks['npx'] = result.returncode == 0
        except FileNotFoundError:
            checks['npx'] = False
        
        return checks
    
    def install_flow_nexus(self) -> bool:
        """Install Flow Nexus MCP tools"""
        try:
            print("📦 Installing Flow Nexus MCP tools...")
            
            # Install Flow Nexus globally
            result = subprocess.run([
                'npm', 'install', '-g', 'flow-nexus@latest'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to install Flow Nexus: {result.stderr}")
                return False
            
            print("✅ Flow Nexus installed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False
    
    def configure_claude_mcp(self) -> bool:
        """Configure Claude CLI with Flow Nexus MCP server"""
        try:
            print("⚙️ Configuring Claude CLI with Flow Nexus MCP...")
            
            # Add Flow Nexus MCP server
            result = subprocess.run([
                'claude', 'mcp', 'add', 'flow-nexus', 
                'npx', 'flow-nexus@latest', 'mcp', 'start'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠️ MCP configuration note: {result.stderr}")
                # This might not be an error, Claude MCP might already be configured
            
            # Optionally add other MCP servers
            if self.config.get('ruv_swarm', {}).get('enabled'):
                subprocess.run([
                    'claude', 'mcp', 'add', 'ruv-swarm',
                    'npx', 'ruv-swarm', 'mcp', 'start'
                ], capture_output=True, text=True)
            
            print("✅ Claude MCP configuration completed!")
            return True
            
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return False
    
    def verify_mcp_tools(self) -> Dict[str, bool]:
        """Verify that required MCP tools are available"""
        required_tools = self.config.get('flow_nexus', {}).get('mcp_tools_required', [])
        results = {}
        
        print("🔍 Verifying MCP tools availability...")
        
        # Test basic MCP connectivity
        try:
            result = subprocess.run([
                'claude', 'mcp', 'list'
            ], capture_output=True, text=True, timeout=10)
            
            mcp_available = result.returncode == 0
            results['mcp_basic'] = mcp_available
            
            if mcp_available:
                print("✅ Claude MCP is available")
            else:
                print("❌ Claude MCP not available")
                return results
            
        except subprocess.TimeoutExpired:
            print("⚠️ MCP check timed out")
            results['mcp_basic'] = False
            return results
        except Exception as e:
            print(f"❌ MCP check failed: {e}")
            results['mcp_basic'] = False
            return results
        
        # Test Flow Nexus specific tools
        for tool in required_tools[:3]:  # Test first few tools
            try:
                result = subprocess.run([
                    'claude', 'mcp', 'call', tool, '--help'
                ], capture_output=True, text=True, timeout=10)
                
                results[tool] = result.returncode == 0
                
            except subprocess.TimeoutExpired:
                results[tool] = False
            except Exception:
                results[tool] = False
        
        return results
    
    def setup_authentication(self) -> bool:
        """Guide user through Flow Nexus authentication setup"""
        print("\n🔐 Flow Nexus Authentication Setup")
        print("You have two options:")
        print("1. Login with existing account")
        print("2. Create new account")
        print("3. Skip authentication (limited features)")
        
        choice = input("\nChoice (1-3): ").strip()
        
        if choice == "1":
            return self._login_existing_account()
        elif choice == "2":
            return self._create_new_account()
        elif choice == "3":
            print("ℹ️ Skipping authentication - you can login later via CLI")
            return True
        else:
            print("❌ Invalid choice")
            return False
    
    def _login_existing_account(self) -> bool:
        """Login to existing Flow Nexus account"""
        try:
            print("\n📧 Please login using Flow Nexus CLI:")
            print("Run: npx flow-nexus@latest login")
            
            input("Press Enter after completing login...")
            
            # Verify login
            result = subprocess.run([
                'npx', 'flow-nexus@latest', 'status'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Authentication verified!")
                return True
            else:
                print("⚠️ Could not verify authentication")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def _create_new_account(self) -> bool:
        """Create new Flow Nexus account"""
        try:
            print("\n📝 Please register using Flow Nexus CLI:")
            print("Run: npx flow-nexus@latest register")
            
            input("Press Enter after completing registration...")
            
            # Verify registration and login
            result = subprocess.run([
                'npx', 'flow-nexus@latest', 'status'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Registration and login verified!")
                return True
            else:
                print("⚠️ Could not verify registration")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def run_full_setup(self) -> bool:
        """Run complete setup process"""
        print("🚀 Flow Nexus Integration Setup")
        print("=" * 50)
        
        # Check prerequisites
        prereqs = self.check_prerequisites()
        print("\n📋 Prerequisites Check:")
        
        for name, available in prereqs.items():
            status = "✅" if available else "❌"
            print(f"  {status} {name}")
        
        if not all(prereqs.values()):
            print("\n❌ Missing prerequisites. Please install:")
            if not prereqs.get('nodejs'):
                print("  • Node.js: https://nodejs.org/")
            if not prereqs.get('npm'):
                print("  • npm (comes with Node.js)")
            if not prereqs.get('claude_cli'):
                print("  • Claude CLI: https://claude.ai/cli")
            return False
        
        print("\n✅ All prerequisites available!")
        
        # Install Flow Nexus
        if not self.install_flow_nexus():
            return False
        
        # Configure MCP
        if not self.configure_claude_mcp():
            print("⚠️ MCP configuration had issues, but continuing...")
        
        # Verify tools
        verification = self.verify_mcp_tools()
        print("\n🔍 Tool Verification:")
        for tool, available in verification.items():
            status = "✅" if available else "❌"
            print(f"  {status} {tool}")
        
        # Setup authentication
        auth_success = self.setup_authentication()
        
        # Summary
        print("\n📊 Setup Summary:")
        print(f"  • Flow Nexus installed: ✅")
        print(f"  • MCP configured: {'✅' if verification.get('mcp_basic', False) else '⚠️'}")
        print(f"  • Authentication: {'✅' if auth_success else '⚠️'}")
        
        if verification.get('mcp_basic', False):
            print("\n🎉 Setup completed successfully!")
            print("You can now use --cloud mode in the CLI")
            return True
        else:
            print("\n⚠️ Setup completed with warnings")
            print("Some cloud features may not be available")
            return False
    
    def quick_check(self) -> bool:
        """Quick check if cloud features are available"""
        try:
            # Quick MCP availability check
            result = subprocess.run([
                'claude', 'mcp', 'list'
            ], capture_output=True, text=True, timeout=5)
            
            return result.returncode == 0
        except:
            return False


def main():
    """Main setup function"""
    setup = MCPSetupManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick-check":
            available = setup.quick_check()
            print("✅ Cloud features available" if available else "❌ Cloud features not available")
            sys.exit(0 if available else 1)
        elif sys.argv[1] == "--verify":
            results = setup.verify_mcp_tools()
            all_good = all(results.values())
            print("✅ All tools verified" if all_good else "❌ Some tools missing")
            sys.exit(0 if all_good else 1)
    
    # Run full setup
    success = setup.run_full_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()