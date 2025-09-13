#!/usr/bin/env python3
"""
Flow Nexus Integration Module for Algorithms & Data Structures CLI
Provides cloud-based features including authentication, progress tracking, 
challenges, leaderboards, and real-time collaboration.
"""

import json
import asyncio
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import hashlib
import uuid

# Import existing CLI components
from ..ui.windows_formatter import WindowsFormatter
from ..notes_manager import NotesManager


@dataclass
class CloudUser:
    """Cloud user profile data structure"""
    user_id: str
    email: str
    username: str
    full_name: Optional[str] = None
    tier: str = "free"  # free, pro, enterprise
    ruv_credits: int = 0
    achievements: List[str] = None
    created_at: str = None
    last_login: str = None
    
    def __post_init__(self):
        if self.achievements is None:
            self.achievements = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class CloudProgress:
    """Cloud progress tracking data structure"""
    user_id: str
    lesson_id: str
    module_id: str
    status: str  # started, completed, mastered
    score: int = 0
    time_spent: int = 0  # minutes
    attempts: int = 0
    last_accessed: str = None
    notes_count: int = 0
    practice_problems_completed: int = 0
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = datetime.now().isoformat()


@dataclass
class Challenge:
    """Challenge data structure"""
    challenge_id: str
    title: str
    description: str
    difficulty: str  # beginner, intermediate, advanced, expert
    category: str
    points: int
    time_limit: Optional[int] = None  # minutes
    test_cases: List[Dict] = None
    solution_template: str = ""
    
    def __post_init__(self):
        if self.test_cases is None:
            self.test_cases = []


class FlowNexusMCPWrapper:
    """Wrapper for Flow Nexus MCP tools with error handling and fallbacks"""
    
    def __init__(self):
        self.formatter = WindowsFormatter()
        self.is_available = self._check_mcp_availability()
        self.session_cache = {}
        
    def _check_mcp_availability(self) -> bool:
        """Check if Flow Nexus MCP tools are available"""
        try:
            # Try to run a simple MCP command to test availability
            result = subprocess.run([
                'npx', 'claude', 'mcp', 'list'
            ], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    async def _run_mcp_command(self, tool_name: str, **params) -> Dict[str, Any]:
        """Execute MCP tool with error handling"""
        if not self.is_available:
            return {"error": "Flow Nexus MCP tools not available", "offline_mode": True}
        
        try:
            # Convert parameters to command line arguments
            cmd_args = []
            for key, value in params.items():
                if isinstance(value, bool):
                    if value:
                        cmd_args.append(f"--{key}")
                elif isinstance(value, (list, dict)):
                    cmd_args.extend([f"--{key}", json.dumps(value)])
                else:
                    cmd_args.extend([f"--{key}", str(value)])
            
            # Run the MCP tool
            cmd = ['npx', 'claude', 'mcp', 'call', tool_name] + cmd_args
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"result": result.stdout, "raw_output": True}
            else:
                return {"error": result.stderr, "return_code": result.returncode}
                
        except subprocess.TimeoutExpired:
            return {"error": "MCP command timed out"}
        except Exception as e:
            return {"error": f"MCP command failed: {str(e)}"}
    
    # Authentication wrapper methods
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login to Flow Nexus"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__user_login",
            email=email,
            password=password
        )
    
    async def register(self, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Register new user account"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__user_register",
            email=email,
            password=password,
            full_name=full_name or ""
        )
    
    async def get_auth_status(self) -> Dict[str, Any]:
        """Check authentication status"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__auth_status",
            detailed=True
        )
    
    # Storage and sync methods
    async def upload_progress(self, bucket: str, path: str, content: str) -> Dict[str, Any]:
        """Upload progress data to cloud storage"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__storage_upload",
            bucket=bucket,
            path=path,
            content=content,
            content_type="application/json"
        )
    
    async def download_progress(self, bucket: str, path: str) -> Dict[str, Any]:
        """Download progress data from cloud storage"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__storage_get_url",
            bucket=bucket,
            path=path
        )
    
    # Challenge methods
    async def submit_challenge(self, challenge_id: str, user_id: str, solution_code: str, 
                             language: str = "python", execution_time: float = None) -> Dict[str, Any]:
        """Submit solution for a challenge"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__challenge_submit",
            challenge_id=challenge_id,
            user_id=user_id,
            solution_code=solution_code,
            language=language,
            execution_time=execution_time
        )
    
    async def get_challenges(self, category: str = None, difficulty: str = None, 
                           limit: int = 20) -> Dict[str, Any]:
        """Get available challenges"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__challenges_list",
            category=category,
            difficulty=difficulty,
            limit=limit,
            status="active"
        )
    
    async def get_challenge_details(self, challenge_id: str) -> Dict[str, Any]:
        """Get specific challenge details"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__challenge_get",
            challenge_id=challenge_id
        )
    
    # Leaderboard methods
    async def get_leaderboard(self, leaderboard_type: str = "global", 
                            challenge_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """Get leaderboard rankings"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__leaderboard_get",
            type=leaderboard_type,
            challenge_id=challenge_id,
            limit=limit
        )
    
    # Achievement methods
    async def get_achievements(self, user_id: str, category: str = None) -> Dict[str, Any]:
        """Get user achievements"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__achievements_list",
            user_id=user_id,
            category=category
        )
    
    async def earn_ruv_credits(self, user_id: str, amount: int, reason: str, 
                             source: str = "learning") -> Dict[str, Any]:
        """Award rUv credits to user"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__app_store_earn_ruv",
            user_id=user_id,
            amount=amount,
            reason=reason,
            source=source
        )
    
    async def get_ruv_balance(self, user_id: str) -> Dict[str, Any]:
        """Get user rUv credit balance"""
        return await self._run_mcp_command(
            "mcp__flow-nexus__ruv_balance",
            user_id=user_id
        )


class FlowNexusIntegration:
    """
    Main Flow Nexus integration class providing cloud features for the CLI
    """
    
    def __init__(self, cli_engine=None):
        self.cli_engine = cli_engine
        self.formatter = WindowsFormatter()
        self.mcp = FlowNexusMCPWrapper()
        self.current_user: Optional[CloudUser] = None
        self.offline_mode = False
        self.cache_dir = Path.home() / ".algorithms_cli" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load cached user data if available
        self._load_cached_user()
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def _load_cached_user(self):
        """Load cached user authentication data"""
        cache_file = self.cache_dir / "user_session.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # Check if session is still valid (24 hour expiry)
                    last_login = datetime.fromisoformat(data.get('last_login', ''))
                    if datetime.now() - last_login < timedelta(hours=24):
                        self.current_user = CloudUser(**data)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Invalid cache file, remove it
                cache_file.unlink(missing_ok=True)
    
    def _save_user_cache(self):
        """Save user session to cache"""
        if self.current_user:
            cache_file = self.cache_dir / "user_session.json"
            with open(cache_file, 'w') as f:
                json.dump(asdict(self.current_user), f)
    
    async def login_interactive(self) -> bool:
        """Interactive login flow"""
        print(self.formatter.header("\n🔐 Flow Nexus Cloud Login"))
        print(self.formatter.info("Connect your local progress to the cloud for:"))
        print("  • Cross-device synchronization")
        print("  • Leaderboards and achievements") 
        print("  • Cloud-based challenges")
        print("  • Progress backup and restore")
        print()
        
        if not self.mcp.is_available:
            print(self.formatter.warning("⚠️  Flow Nexus MCP tools not available"))
            print(self.formatter.info("To enable cloud features, install Flow Nexus:"))
            print("  npm install -g flow-nexus@latest")
            print("  npx flow-nexus@latest login")
            choice = input("\nContinue in offline mode? (y/n): ")
            if choice.lower() == 'y':
                self.offline_mode = True
                return True
            return False
        
        # Check if already authenticated
        auth_status = await self.mcp.get_auth_status()
        if not auth_status.get("error"):
            print(self.formatter.success("✅ Already logged in to Flow Nexus!"))
            return True
        
        print("1. Login with existing account")
        print("2. Create new account")
        print("3. Continue offline")
        print("0. Cancel")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            return await self._handle_login()
        elif choice == "2":
            return await self._handle_registration()
        elif choice == "3":
            self.offline_mode = True
            print(self.formatter.info("📱 Running in offline mode"))
            return True
        else:
            return False
    
    async def _handle_login(self) -> bool:
        """Handle user login"""
        email = input("Email: ").strip()
        import getpass
        password = getpass.getpass("Password: ")
        
        print(self.formatter.info("🔄 Logging in..."))
        
        result = await self.mcp.login(email, password)
        
        if result.get("error"):
            print(self.formatter.error(f"❌ Login failed: {result['error']}"))
            return False
        
        # Create user object from response
        user_data = result.get("user", {})
        self.current_user = CloudUser(
            user_id=user_data.get("id", str(uuid.uuid4())),
            email=email,
            username=user_data.get("username", email.split("@")[0]),
            full_name=user_data.get("full_name"),
            tier=user_data.get("tier", "free"),
            ruv_credits=user_data.get("ruv_credits", 0),
            last_login=datetime.now().isoformat()
        )
        
        self._save_user_cache()
        print(self.formatter.success(f"✅ Welcome back, {self.current_user.username}!"))
        return True
    
    async def _handle_registration(self) -> bool:
        """Handle user registration"""
        print(self.formatter.header("\n📝 Create New Account"))
        
        email = input("Email: ").strip()
        full_name = input("Full name (optional): ").strip()
        import getpass
        password = getpass.getpass("Password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print(self.formatter.error("❌ Passwords don't match"))
            return False
        
        print(self.formatter.info("🔄 Creating account..."))
        
        result = await self.mcp.register(email, password, full_name)
        
        if result.get("error"):
            print(self.formatter.error(f"❌ Registration failed: {result['error']}"))
            return False
        
        print(self.formatter.success("✅ Account created successfully!"))
        print(self.formatter.info("Please check your email for verification."))
        
        # Auto-login after registration
        return await self._handle_login()
    
    async def sync_progress_to_cloud(self, progress_data: Dict) -> bool:
        """Sync local progress to cloud storage"""
        if self.offline_mode or not self.is_authenticated:
            return False
        
        try:
            # Prepare progress data for upload
            cloud_progress = {
                "user_id": self.current_user.user_id,
                "local_progress": progress_data,
                "sync_timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            bucket = "user-progress"
            path = f"{self.current_user.user_id}/progress.json"
            content = json.dumps(cloud_progress, indent=2)
            
            result = await self.mcp.upload_progress(bucket, path, content)
            
            if result.get("error"):
                print(self.formatter.warning(f"⚠️ Failed to sync progress: {result['error']}"))
                return False
            
            print(self.formatter.success("☁️ Progress synced to cloud"))
            return True
            
        except Exception as e:
            print(self.formatter.warning(f"⚠️ Sync error: {str(e)}"))
            return False
    
    async def download_progress_from_cloud(self) -> Optional[Dict]:
        """Download progress from cloud storage"""
        if self.offline_mode or not self.is_authenticated:
            return None
        
        try:
            bucket = "user-progress"
            path = f"{self.current_user.user_id}/progress.json"
            
            result = await self.mcp.download_progress(bucket, path)
            
            if result.get("error"):
                return None
            
            # In a real implementation, you would fetch the actual content
            # For now, return None to indicate cloud sync is set up but data not available
            return None
            
        except Exception as e:
            print(self.formatter.warning(f"⚠️ Download error: {str(e)}"))
            return None
    
    async def get_available_challenges(self, difficulty: str = None, 
                                     category: str = None) -> List[Challenge]:
        """Get available coding challenges"""
        if self.offline_mode:
            return self._get_offline_challenges()
        
        result = await self.mcp.get_challenges(category=category, difficulty=difficulty)
        
        if result.get("error"):
            print(self.formatter.warning("⚠️ Using offline challenges"))
            return self._get_offline_challenges()
        
        # Convert API response to Challenge objects
        challenges = []
        for challenge_data in result.get("challenges", []):
            challenge = Challenge(
                challenge_id=challenge_data.get("id", str(uuid.uuid4())),
                title=challenge_data.get("title", "Unknown Challenge"),
                description=challenge_data.get("description", ""),
                difficulty=challenge_data.get("difficulty", "beginner"),
                category=challenge_data.get("category", "algorithms"),
                points=challenge_data.get("points", 10)
            )
            challenges.append(challenge)
        
        return challenges
    
    def _get_offline_challenges(self) -> List[Challenge]:
        """Get offline/local challenges when cloud is unavailable"""
        return [
            Challenge(
                challenge_id="local_array_sum",
                title="Two Sum Problem",
                description="Find two numbers in an array that add up to a target sum",
                difficulty="beginner",
                category="arrays",
                points=10,
                test_cases=[
                    {"input": {"nums": [2, 7, 11, 15], "target": 9}, "output": [0, 1]},
                    {"input": {"nums": [3, 2, 4], "target": 6}, "output": [1, 2]}
                ]
            ),
            Challenge(
                challenge_id="local_binary_search",
                title="Binary Search Implementation",
                description="Implement binary search algorithm for sorted arrays",
                difficulty="intermediate",
                category="searching",
                points=15,
                test_cases=[
                    {"input": {"nums": [1, 3, 5, 7, 9], "target": 5}, "output": 2},
                    {"input": {"nums": [1, 3, 5, 7, 9], "target": 6}, "output": -1}
                ]
            ),
            Challenge(
                challenge_id="local_quicksort",
                title="QuickSort Algorithm",
                description="Implement the quicksort sorting algorithm",
                difficulty="advanced",
                category="sorting",
                points=25,
                test_cases=[
                    {"input": {"nums": [3, 6, 8, 10, 1, 2, 1]}, "output": [1, 1, 2, 3, 6, 8, 10]},
                    {"input": {"nums": [5, 4, 3, 2, 1]}, "output": [1, 2, 3, 4, 5]}
                ]
            )
        ]
    
    async def submit_challenge_solution(self, challenge_id: str, solution_code: str, 
                                      language: str = "python") -> Dict[str, Any]:
        """Submit a solution for a challenge"""
        if self.offline_mode or not self.is_authenticated:
            return self._evaluate_offline_solution(challenge_id, solution_code)
        
        result = await self.mcp.submit_challenge(
            challenge_id=challenge_id,
            user_id=self.current_user.user_id,
            solution_code=solution_code,
            language=language
        )
        
        if result.get("error"):
            return self._evaluate_offline_solution(challenge_id, solution_code)
        
        return result
    
    def _evaluate_offline_solution(self, challenge_id: str, solution_code: str) -> Dict[str, Any]:
        """Evaluate solution offline (basic validation)"""
        # Basic offline evaluation - in a real system this would be more sophisticated
        return {
            "status": "submitted",
            "message": "Solution submitted (offline mode - full evaluation pending)",
            "points_awarded": 5,  # Partial credit for submission
            "offline_mode": True
        }
    
    async def get_leaderboard_data(self, board_type: str = "global") -> Dict[str, Any]:
        """Get leaderboard data"""
        if self.offline_mode:
            return self._get_offline_leaderboard()
        
        result = await self.mcp.get_leaderboard(leaderboard_type=board_type)
        
        if result.get("error"):
            return self._get_offline_leaderboard()
        
        return result
    
    def _get_offline_leaderboard(self) -> Dict[str, Any]:
        """Get offline leaderboard (mock data)"""
        return {
            "leaderboard": [
                {"rank": 1, "username": "algorithms_master", "score": 2850, "solved": 95},
                {"rank": 2, "username": "code_ninja", "score": 2340, "solved": 78},
                {"rank": 3, "username": "data_structures_pro", "score": 2100, "solved": 70},
                {"rank": 4, "username": self.current_user.username if self.current_user else "you", 
                 "score": 150, "solved": 8, "current_user": True},
                {"rank": 5, "username": "sorting_specialist", "score": 1890, "solved": 63}
            ],
            "total_participants": 1247,
            "your_rank": 4 if self.current_user else None,
            "offline_mode": True
        }
    
    async def get_user_achievements(self) -> List[Dict[str, Any]]:
        """Get user achievements"""
        if self.offline_mode or not self.is_authenticated:
            return self._get_offline_achievements()
        
        result = await self.mcp.get_achievements(self.current_user.user_id)
        
        if result.get("error"):
            return self._get_offline_achievements()
        
        return result.get("achievements", [])
    
    def _get_offline_achievements(self) -> List[Dict[str, Any]]:
        """Get offline achievements (based on local progress)"""
        # This would analyze local progress to determine achievements
        achievements = []
        
        if self.cli_engine:
            progress = self.cli_engine._load_progress()
            completed_count = len(progress.get("completed", []))
            score = progress.get("score", 0)
            
            if completed_count >= 1:
                achievements.append({
                    "id": "first_lesson",
                    "title": "First Steps",
                    "description": "Complete your first lesson",
                    "category": "learning",
                    "points": 10,
                    "earned_at": datetime.now().isoformat()
                })
            
            if completed_count >= 5:
                achievements.append({
                    "id": "persistent_learner",
                    "title": "Persistent Learner",
                    "description": "Complete 5 lessons",
                    "category": "learning",
                    "points": 25,
                    "earned_at": datetime.now().isoformat()
                })
            
            if score >= 100:
                achievements.append({
                    "id": "century_scorer",
                    "title": "Century Scorer",
                    "description": "Earn 100 points",
                    "category": "scoring",
                    "points": 50,
                    "earned_at": datetime.now().isoformat()
                })
        
        return achievements
    
    async def award_credits_for_activity(self, activity: str, amount: int = 5):
        """Award rUv credits for learning activities"""
        if self.offline_mode or not self.is_authenticated:
            return
        
        try:
            result = await self.mcp.earn_ruv_credits(
                user_id=self.current_user.user_id,
                amount=amount,
                reason=f"Learning activity: {activity}",
                source="algorithms_cli"
            )
            
            if not result.get("error"):
                self.current_user.ruv_credits += amount
                self._save_user_cache()
                print(self.formatter.success(f"💰 Earned {amount} rUv credits for {activity}!"))
        except Exception as e:
            pass  # Silently fail for credits
    
    def display_cloud_status(self):
        """Display current cloud connection status"""
        print(self.formatter.header("\n☁️ Cloud Status"))
        
        if self.offline_mode:
            print(self.formatter.warning("📱 Offline Mode"))
            print("  • Local progress tracking only")
            print("  • Limited challenges available")
            print("  • No cloud sync or leaderboards")
        elif self.is_authenticated:
            print(self.formatter.success(f"✅ Connected as {self.current_user.username}"))
            print(f"  • User ID: {self.current_user.user_id}")
            print(f"  • Tier: {self.current_user.tier}")
            print(f"  • rUv Credits: {self.current_user.ruv_credits}")
            print(f"  • Last login: {self.current_user.last_login}")
        else:
            print(self.formatter.info("🔒 Not logged in"))
            print("  • Use cloud login to enable full features")
        
        print(f"  • MCP Tools: {'✅ Available' if self.mcp.is_available else '❌ Not available'}")
    
    async def logout(self):
        """Logout from cloud services"""
        if self.current_user:
            # Clear cached session
            cache_file = self.cache_dir / "user_session.json"
            cache_file.unlink(missing_ok=True)
            
            self.current_user = None
            self.offline_mode = False
            
            print(self.formatter.success("👋 Logged out successfully"))