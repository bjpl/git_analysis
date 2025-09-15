#!/usr/bin/env python3
"""
Real-time Collaboration Features for Algorithms & Data Structures CLI
Provides study groups, peer learning, and real-time progress sharing.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid

from ..ui.windows_formatter import WindowsFormatter
from .flow_nexus import FlowNexusMCPWrapper


@dataclass
class StudyGroup:
    """Study group data structure"""
    group_id: str
    name: str
    description: str
    owner_id: str
    members: List[str]
    created_at: str
    is_public: bool = True
    max_members: int = 10
    current_lesson: Optional[str] = None
    
    def __post_init__(self):
        if not self.members:
            self.members = [self.owner_id]


@dataclass
class StudySession:
    """Active study session data"""
    session_id: str
    group_id: str
    lesson_id: str
    started_by: str
    started_at: str
    participants: List[str]
    status: str = "active"  # active, paused, completed
    shared_notes: List[Dict] = None
    
    def __post_init__(self):
        if self.shared_notes is None:
            self.shared_notes = []


@dataclass
class PeerActivity:
    """Peer activity for real-time updates"""
    user_id: str
    username: str
    activity_type: str  # lesson_start, lesson_complete, note_share, challenge_solve
    lesson_id: Optional[str] = None
    challenge_id: Optional[str] = None
    timestamp: str = None
    details: Dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.details is None:
            self.details = {}


class CollaborationManager:
    """Manages real-time collaboration features"""
    
    def __init__(self, flow_nexus_integration):
        self.flow_nexus = flow_nexus_integration
        self.mcp = FlowNexusMCPWrapper()
        self.formatter = WindowsFormatter()
        
        # Local state for collaboration
        self.current_study_group: Optional[StudyGroup] = None
        self.active_session: Optional[StudySession] = None
        self.recent_activities: List[PeerActivity] = []
        self.collaboration_enabled = True
    
    async def create_study_group(self, name: str, description: str, 
                               is_public: bool = True) -> Optional[StudyGroup]:
        """Create a new study group"""
        if not self.flow_nexus.is_authenticated:
            print(self.formatter.warning("⚠️ Login required to create study groups"))
            return None
        
        group = StudyGroup(
            group_id=str(uuid.uuid4()),
            name=name,
            description=description,
            owner_id=self.flow_nexus.current_user.user_id,
            members=[self.flow_nexus.current_user.user_id],
            created_at=datetime.now().isoformat(),
            is_public=is_public
        )
        
        # In a real implementation, this would sync to cloud
        if await self._sync_group_to_cloud(group):
            print(self.formatter.success(f"✅ Study group '{name}' created!"))
            print(f"📋 Group ID: {group.group_id}")
            return group
        
        return None
    
    async def join_study_group(self, group_id: str) -> bool:
        """Join an existing study group"""
        if not self.flow_nexus.is_authenticated:
            print(self.formatter.warning("⚠️ Login required to join study groups"))
            return False
        
        # Mock implementation - in reality would fetch from cloud
        group = await self._fetch_group_from_cloud(group_id)
        if group:
            if len(group.members) < group.max_members:
                group.members.append(self.flow_nexus.current_user.user_id)
                await self._sync_group_to_cloud(group)
                self.current_study_group = group
                print(self.formatter.success(f"✅ Joined study group: {group.name}"))
                return True
            else:
                print(self.formatter.error("❌ Study group is full"))
        else:
            print(self.formatter.error("❌ Study group not found"))
        
        return False
    
    async def start_study_session(self, lesson_id: str) -> Optional[StudySession]:
        """Start a collaborative study session"""
        if not self.current_study_group:
            print(self.formatter.warning("⚠️ Join a study group first"))
            return None
        
        session = StudySession(
            session_id=str(uuid.uuid4()),
            group_id=self.current_study_group.group_id,
            lesson_id=lesson_id,
            started_by=self.flow_nexus.current_user.user_id,
            started_at=datetime.now().isoformat(),
            participants=[self.flow_nexus.current_user.user_id]
        )
        
        if await self._sync_session_to_cloud(session):
            self.active_session = session
            print(self.formatter.success("🎓 Study session started!"))
            print(f"📚 Lesson: {lesson_id}")
            print(f"👥 Group: {self.current_study_group.name}")
            
            # Notify group members
            await self._notify_group_members("study_session_started", {
                "lesson_id": lesson_id,
                "session_id": session.session_id
            })
            
            return session
        
        return None
    
    async def share_note_with_group(self, note_content: str, lesson_id: str):
        """Share a note with the current study group"""
        if not self.current_study_group:
            print(self.formatter.warning("⚠️ No active study group"))
            return
        
        shared_note = {
            "id": str(uuid.uuid4()),
            "author_id": self.flow_nexus.current_user.user_id,
            "author_name": self.flow_nexus.current_user.username,
            "content": note_content,
            "lesson_id": lesson_id,
            "timestamp": datetime.now().isoformat(),
            "likes": 0,
            "comments": []
        }
        
        # Add to active session if exists
        if self.active_session:
            self.active_session.shared_notes.append(shared_note)
            await self._sync_session_to_cloud(self.active_session)
        
        # Notify group
        await self._notify_group_members("note_shared", {
            "note_id": shared_note["id"],
            "lesson_id": lesson_id,
            "preview": note_content[:100] + "..." if len(note_content) > 100 else note_content
        })
        
        print(self.formatter.success("📝 Note shared with study group!"))
    
    async def get_peer_activities(self, limit: int = 10) -> List[PeerActivity]:
        """Get recent peer activities from study group"""
        if not self.current_study_group:
            return []
        
        # Mock activities - in reality would fetch from real-time feed
        activities = [
            PeerActivity(
                user_id="peer1",
                username="alice_learner",
                activity_type="lesson_complete",
                lesson_id="binary-search",
                details={"score": 95, "time_spent": 12}
            ),
            PeerActivity(
                user_id="peer2", 
                username="bob_coder",
                activity_type="challenge_solve",
                challenge_id="two-sum",
                details={"difficulty": "easy", "time": "5:34"}
            ),
            PeerActivity(
                user_id="peer3",
                username="carol_algorithms",
                activity_type="note_share",
                lesson_id="quicksort",
                details={"note_preview": "Key insight: pivot selection affects performance..."}
            )
        ]
        
        return activities[:limit]
    
    async def get_group_leaderboard(self) -> Dict[str, Any]:
        """Get leaderboard for current study group"""
        if not self.current_study_group:
            return {"error": "No active study group"}
        
        # Mock leaderboard - would fetch real data from cloud
        leaderboard = {
            "group_name": self.current_study_group.name,
            "rankings": [
                {"rank": 1, "username": "alice_learner", "score": 450, "lessons": 15},
                {"rank": 2, "username": "bob_coder", "score": 380, "lessons": 12}, 
                {"rank": 3, "username": self.flow_nexus.current_user.username if self.flow_nexus.current_user else "you", 
                 "score": 280, "lessons": 9, "current_user": True},
                {"rank": 4, "username": "carol_algorithms", "score": 220, "lessons": 7}
            ],
            "your_rank": 3,
            "total_members": len(self.current_study_group.members)
        }
        
        return leaderboard
    
    def display_collaboration_status(self):
        """Display current collaboration status"""
        print(self.formatter.header("\n👥 Collaboration Status"))
        
        if not self.flow_nexus.is_authenticated:
            print(self.formatter.warning("🔒 Login required for collaboration features"))
            return
        
        if self.current_study_group:
            print(self.formatter.success(f"📚 Study Group: {self.current_study_group.name}"))
            print(f"  • Members: {len(self.current_study_group.members)}/{self.current_study_group.max_members}")
            print(f"  • Owner: {'You' if self.current_study_group.owner_id == self.flow_nexus.current_user.user_id else 'Other'}")
            print(f"  • Public: {'Yes' if self.current_study_group.is_public else 'No'}")
            
            if self.active_session:
                print(f"  • Active Session: {self.active_session.lesson_id}")
                print(f"  • Participants: {len(self.active_session.participants)}")
                print(f"  • Shared Notes: {len(self.active_session.shared_notes)}")
        else:
            print(self.formatter.info("📭 No active study group"))
            print("  • Create or join a group to enable collaboration")
        
        print(f"  • Real-time sync: {'✅ Enabled' if self.collaboration_enabled else '❌ Disabled'}")
    
    async def show_collaboration_menu(self):
        """Show collaboration features menu"""
        while True:
            print(self.formatter.header("\n👥 Collaboration Features"))
            print("1. 📚 Join/Create Study Group")
            print("2. 🎓 Start Study Session")
            print("3. 📝 Share Note with Group")
            print("4. 📊 View Group Leaderboard")
            print("5. 🔔 Recent Peer Activities")
            print("6. ⚙️  Collaboration Settings")
            print("0. 🔙 Back to Main Menu")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                await self._study_group_menu()
            elif choice == "2":
                await self._start_session_menu()
            elif choice == "3":
                await self._share_note_menu()
            elif choice == "4":
                await self._show_group_leaderboard()
            elif choice == "5":
                await self._show_peer_activities()
            elif choice == "6":
                await self._collaboration_settings()
            elif choice == "0":
                break
            else:
                print(self.formatter.error("Invalid choice"))
    
    async def _study_group_menu(self):
        """Study group management menu"""
        print(self.formatter.header("\n📚 Study Groups"))
        
        if self.current_study_group:
            print(f"Current group: {self.current_study_group.name}")
            print("1. Leave current group")
            print("2. Invite members")
            print("3. View group details")
            print("0. Back")
        else:
            print("1. Create new study group")
            print("2. Join existing group")
            print("3. Browse public groups")
            print("0. Back")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            if self.current_study_group:
                await self._leave_group()
            else:
                await self._create_group_interactive()
        elif choice == "2":
            if self.current_study_group:
                await self._invite_members()
            else:
                await self._join_group_interactive()
        elif choice == "3":
            if self.current_study_group:
                self._show_group_details()
            else:
                await self._browse_public_groups()
    
    async def _create_group_interactive(self):
        """Interactive group creation"""
        name = input("Group name: ").strip()
        description = input("Description: ").strip()
        is_public = input("Make public? (y/n): ").lower() == 'y'
        
        group = await self.create_study_group(name, description, is_public)
        if group:
            self.current_study_group = group
    
    async def _join_group_interactive(self):
        """Interactive group joining"""
        group_id = input("Enter group ID: ").strip()
        await self.join_study_group(group_id)
    
    async def _start_session_menu(self):
        """Start study session menu"""
        if not self.current_study_group:
            print(self.formatter.warning("⚠️ Join a study group first"))
            return
        
        lesson_id = input("Enter lesson ID to study together: ").strip()
        await self.start_study_session(lesson_id)
    
    async def _share_note_menu(self):
        """Share note menu"""
        if not self.current_study_group:
            print(self.formatter.warning("⚠️ Join a study group first"))
            return
        
        lesson_id = input("Lesson ID: ").strip()
        print("Enter your note (press Enter twice to finish):")
        
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        note_content = "\n".join(lines)
        await self.share_note_with_group(note_content, lesson_id)
    
    async def _show_group_leaderboard(self):
        """Show group leaderboard"""
        leaderboard = await self.get_group_leaderboard()
        
        if leaderboard.get("error"):
            print(self.formatter.error(leaderboard["error"]))
            return
        
        print(self.formatter.header(f"\n🏆 {leaderboard['group_name']} Leaderboard"))
        
        for entry in leaderboard["rankings"]:
            rank_str = f"#{entry['rank']}"
            username = entry["username"]
            score = entry["score"]
            lessons = entry["lessons"]
            
            if entry.get("current_user"):
                line = self.formatter.success(f"{rank_str:3} {username:20} {score:4} pts  {lessons:2} lessons (YOU)")
            else:
                line = f"{rank_str:3} {username:20} {score:4} pts  {lessons:2} lessons"
            
            print(line)
        
        input("\nPress Enter to continue...")
    
    async def _show_peer_activities(self):
        """Show recent peer activities"""
        activities = await self.get_peer_activities()
        
        print(self.formatter.header("\n🔔 Recent Peer Activities"))
        
        if not activities:
            print(self.formatter.info("No recent activities"))
            return
        
        for activity in activities:
            timestamp = datetime.fromisoformat(activity.timestamp).strftime("%H:%M")
            
            if activity.activity_type == "lesson_complete":
                msg = f"completed lesson {activity.lesson_id}"
                if activity.details.get("score"):
                    msg += f" (score: {activity.details['score']})"
            elif activity.activity_type == "challenge_solve":
                msg = f"solved challenge {activity.challenge_id}"
                if activity.details.get("time"):
                    msg += f" in {activity.details['time']}"
            elif activity.activity_type == "note_share":
                msg = f"shared note on {activity.lesson_id}"
                if activity.details.get("note_preview"):
                    msg += f": \"{activity.details['note_preview']}\""
            else:
                msg = activity.activity_type
            
            print(f"{timestamp} 👤 {activity.username} {msg}")
        
        input("\nPress Enter to continue...")
    
    async def _collaboration_settings(self):
        """Collaboration settings menu"""
        print(self.formatter.header("\n⚙️ Collaboration Settings"))
        print(f"1. Real-time sync: {'✅ Enabled' if self.collaboration_enabled else '❌ Disabled'}")
        print("2. Leave current study group")
        print("3. Privacy settings")
        print("0. Back")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            self.collaboration_enabled = not self.collaboration_enabled
            status = "enabled" if self.collaboration_enabled else "disabled"
            print(self.formatter.success(f"✅ Real-time sync {status}"))
        elif choice == "2":
            await self._leave_group()
        elif choice == "3":
            print(self.formatter.info("Privacy settings coming soon!"))
    
    async def _leave_group(self):
        """Leave current study group"""
        if self.current_study_group:
            confirm = input(f"Leave '{self.current_study_group.name}'? (y/n): ")
            if confirm.lower() == 'y':
                self.current_study_group = None
                self.active_session = None
                print(self.formatter.success("👋 Left study group"))
    
    # Helper methods for cloud sync (mock implementations)
    async def _sync_group_to_cloud(self, group: StudyGroup) -> bool:
        """Sync study group to cloud storage"""
        if self.flow_nexus.offline_mode:
            return True  # Simulate success in offline mode
        
        # In real implementation, would use Flow Nexus storage APIs
        try:
            bucket = "study-groups"
            path = f"{group.group_id}/group.json"
            content = json.dumps(asdict(group), indent=2)
            
            result = await self.mcp._run_mcp_command(
                "mcp__flow-nexus__storage_upload",
                bucket=bucket,
                path=path,
                content=content
            )
            
            return not result.get("error")
        except:
            return True  # Graceful fallback
    
    async def _fetch_group_from_cloud(self, group_id: str) -> Optional[StudyGroup]:
        """Fetch study group from cloud"""
        # Mock implementation
        return StudyGroup(
            group_id=group_id,
            name="Algorithms Study Circle",
            description="Daily algorithm practice and discussion",
            owner_id="other_user",
            members=["other_user", "user2", "user3"],
            created_at=datetime.now().isoformat(),
            is_public=True
        )
    
    async def _sync_session_to_cloud(self, session: StudySession) -> bool:
        """Sync study session to cloud"""
        return True  # Mock success
    
    async def _notify_group_members(self, event_type: str, data: Dict):
        """Notify group members of events"""
        # In real implementation, would use real-time messaging APIs
        pass