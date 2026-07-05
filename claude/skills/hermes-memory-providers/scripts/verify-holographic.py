#!/usr/bin/env python3
"""Verify Holographic memory provider is working correctly.

Run this script after switching to Holographic to confirm:
1. Plugin imports successfully
2. Database is created and writable
3. Core tools (fact_store, fact_feedback) function correctly
4. Search retrieval works

Usage:
    python3 scripts/verify-holographic.py

Exit codes:
    0 — All checks passed
    1 — One or more checks failed
"""

import sys
import os
import json

HERMES_AGENT_PATH = os.path.expanduser("~/.hermes/hermes-agent")
if HERMES_AGENT_PATH not in sys.path:
    sys.path.insert(0, HERMES_AGENT_PATH)


def check_import() -> bool:
    """Test 1: Holographic plugin imports."""
    try:
        from plugins.memory.holographic import HolographicMemoryProvider
        print("✅ Holographic plugin imports successfully")
        return True
    except Exception as e:
        print(f"❌ Holographic plugin import failed: {e}")
        return False


def check_instance() -> bool:
    """Test 2: Provider instance creation and availability."""
    try:
        from plugins.memory.holographic import HolographicMemoryProvider
        provider = HolographicMemoryProvider()
        assert provider.name == "holographic"
        assert provider.is_available() is True
        print("✅ Provider instance created (name='holographic', available=True)")
        return True
    except Exception as e:
        print(f"❌ Provider instance creation failed: {e}")
        return False


def check_tools() -> bool:
    """Test 3: Tool schemas are registered."""
    try:
        from plugins.memory.holographic import HolographicMemoryProvider
        provider = HolographicMemoryProvider()
        schemas = provider.get_tool_schemas()
        names = {s["name"] for s in schemas}
        assert "fact_store" in names
        assert "fact_feedback" in names
        print(f"✅ Tool schemas registered: {names}")
        return True
    except Exception as e:
        print(f"❌ Tool schema registration failed: {e}")
        return False


def check_storage() -> bool:
    """Test 4: Database initialization and fact storage."""
    try:
        from plugins.memory.holographic import HolographicMemoryProvider
        provider = HolographicMemoryProvider()
        provider.initialize(session_id="verify_session")

        result = provider.handle_tool_call("fact_store", {
            "action": "add",
            "content": "Holographic memory verification test fact",
            "category": "general",
            "tags": "test,verification"
        })
        data = json.loads(result)
        assert data["status"] == "added"
        assert "fact_id" in data
        print(f"✅ Fact storage works (fact_id={data['fact_id']})")
        return True
    except Exception as e:
        print(f"❌ Fact storage failed: {e}")
        return False


def check_search() -> bool:
    """Test 5: Search retrieval."""
    try:
        from plugins.memory.holographic import HolographicMemoryProvider
        provider = HolographicMemoryProvider()
        provider.initialize(session_id="verify_session")

        # Add a searchable fact
        provider.handle_tool_call("fact_store", {
            "action": "add",
            "content": "User prefers Python for scripting and C++ for performance",
            "category": "user_pref",
            "tags": "language,preference"
        })

        # Search for it
        result = provider.handle_tool_call("fact_store", {
            "action": "search",
            "query": "Python"
        })
        data = json.loads(result)
        assert data["count"] >= 1
        print(f"✅ Search retrieval works ({data['count']} results)")
        return True
    except Exception as e:
        print(f"❌ Search retrieval failed: {e}")
        return False


def check_database_file() -> bool:
    """Test 6: Database file exists on disk."""
    db_path = os.path.expanduser("~/.hermes/memory_store.db")
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"✅ Database file exists ({size} bytes): {db_path}")
        return True
    else:
        print(f"⚠️ Database file not yet created: {db_path}")
        return True  # Not a failure — may not be created until first use


def check_system_prompt() -> bool:
    """Test 7: System prompt block generation."""
    try:
        from plugins.memory.holographic import HolographicMemoryProvider
        provider = HolographicMemoryProvider()
        provider.initialize(session_id="verify_session")

        prompt = provider.system_prompt_block()
        assert "Holographic Memory" in prompt
        print(f"✅ System prompt block generated")
        return True
    except Exception as e:
        print(f"❌ System prompt block failed: {e}")
        return False


def main() -> int:
    print("=== Holographic Memory Provider Verification ===\n")

    checks = [
        check_import,
        check_instance,
        check_tools,
        check_storage,
        check_search,
        check_database_file,
        check_system_prompt,
    ]

    passed = 0
    failed = 0
    for check in checks:
        if check():
            passed += 1
        else:
            failed += 1

    print(f"\n=== Results: {passed}/{len(checks)} passed ===")
    if failed > 0:
        print(f"⚠️  {failed} check(s) failed. Review errors above.")
        return 1
    print("✅ Holographic memory provider is fully operational!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
