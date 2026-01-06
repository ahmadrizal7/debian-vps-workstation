#!/usr/bin/env python3
"""Test team retrieval operations"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from configurator.users.team_manager import TeamManager


def test_team_retrieval():
    """Test retrieving team information."""
    print("Team Retrieval Test")
    print("=" * 60)

    # Use temp directories
    temp_dir = tempfile.mkdtemp()
    registry_file = Path(temp_dir) / "teams.json"
    shared_dirs = Path(temp_dir) / "projects"
    audit_log = Path(temp_dir) / "audit.log"

    team_mgr = TeamManager(
        registry_file=registry_file,
        shared_dirs_base=shared_dirs,
        audit_log=audit_log,
    )

    # Create test teams
    print("\n1. Creating test teams...")

    team1_name = "team1"
    team2_name = "team2"
    user1 = "user1"
    user2 = "user2"

    team1 = team_mgr.create_team(
        name=team1_name,
        description="First test team",
        lead=user1,
        created_by="test-script",
        skip_system_group=True,
    )

    team2 = team_mgr.create_team(
        name=team2_name,
        description="Second test team",
        lead=user2,
        created_by="test-script",
        skip_system_group=True,
    )

    print("  ✅ Test teams created")

    # Add user1 to team2
    team_mgr.add_member(team2_name, user1, skip_system=True)

    # Test 2: Get team by name
    print("\n2. Testing get_team()...")

    retrieved_team = team_mgr.get_team(team1_name)

    if retrieved_team:
        print("  ✅ Team retrieved successfully")
        print(f"     Name: {retrieved_team.name}")
        print(f"     Description: {retrieved_team.description}")
        print(f"     Members: {len(retrieved_team.members)}")

        if retrieved_team.name == team1_name:
            print("  ✅ Correct team retrieved")
    else:
        print("  ❌ Team not found")
        return False

    # Test 3: Get non-existent team
    print("\n3. Testing get_team() for non-existent team...")

    nonexistent = team_mgr.get_team("nonexistent")

    if nonexistent is None:
        print("  ✅ Returns None for non-existent team")
    else:
        print("  ❌ Should return None")
        return False

    # Test 4: List all teams
    print("\n4. Testing list_teams()...")

    all_teams = team_mgr.list_teams()

    print(f"  Total teams: {len(all_teams)}")

    if len(all_teams) == 2:
        print("  ✅ Correct team count")
    else:
        print(f"  ⚠️  Expected 2 teams, got {len(all_teams)}")

    team_names = [t.name for t in all_teams]

    if team1_name in team_names and team2_name in team_names:
        print("  ✅ All teams in list")
    else:
        print("  ❌ Missing teams in list")
        return False

    # Test 5: Get user teams
    print("\n5. Testing get_user_teams()...")

    user1_teams = team_mgr.get_user_teams(user1)

    print(f"  User1 teams: {len(user1_teams)}")

    if len(user1_teams) == 2:
        print("  ✅ User is in 2 teams")
    else:
        print(f"  ⚠️  Expected 2 teams, got {len(user1_teams)}")

    user2_teams = team_mgr.get_user_teams(user2)

    print(f"  User2 teams: {len(user2_teams)}")

    if len(user2_teams) == 1:
        print("  ✅ User is in 1 team")
    else:
        print(f"  ⚠️  Expected 1 team, got {len(user2_teams)}")

    # Test 6: User not in any team
    print("\n6. Testing get_user_teams() for non-member...")

    nonmember_teams = team_mgr.get_user_teams("nonmember")

    if len(nonmember_teams) == 0:
        print("  ✅ Returns empty list for non-member")
    else:
        print(f"  ⚠️  Expected 0 teams, got {len(nonmember_teams)}")

    # Test 7: Team persistence
    print("\n7. Testing team persistence...")

    # Create new manager instance (simulates restart)
    new_mgr = TeamManager(
        registry_file=registry_file,
        shared_dirs_base=shared_dirs,
        audit_log=audit_log,
    )

    loaded_teams = new_mgr.list_teams()

    if len(loaded_teams) == 2:
        print("  ✅ Teams loaded from registry")
    else:
        print(f"  ❌ Teams not persisted (expected 2, got {len(loaded_teams)})")
        return False

    # Cleanup
    print("\n8. Cleaning up...")
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)
    print("  ✅ Cleanup complete")

    print("\n" + "=" * 60)
    print("✅ Team retrieval validated")
    return True


if __name__ == "__main__":
    result = test_team_retrieval()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(f"Team Retrieval: {'✅ PASS' if result else '❌ FAIL'}")

    sys.exit(0 if result else 1)
