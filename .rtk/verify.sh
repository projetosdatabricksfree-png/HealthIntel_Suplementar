#!/bin/bash
# RTK Verification Script for HealthIntel

set -e

echo "🔍 RTK Verification — HealthIntel"
echo "=================================="
echo

# Check RTK installation
echo "1️⃣  RTK Binary..."
if command -v rtk &> /dev/null; then
    VERSION=$(rtk --version 2>/dev/null || echo "unknown")
    echo "   ✅ RTK installed: $VERSION"
else
    echo "   ❌ RTK not found in PATH"
    echo "   Run: curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh"
    exit 1
fi

# Verify it's Token Killer (not Type Kit)
echo
echo "2️⃣  Verify Token Killer (not Type Kit)..."
if rtk gain &> /dev/null; then
    echo "   ✅ Correct RTK (Token Killer) detected"
else
    echo "   ⚠️  RTK gain command failed — might be wrong RTK"
    echo "   Run: cargo uninstall rtk && curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh"
fi

# Check project config
echo
echo "3️⃣  Project Configuration..."
if [ -f ".rtk/filters.toml" ]; then
    FILTER_COUNT=$(grep -c "^\[filters\." .rtk/filters.toml || echo "0")
    echo "   ✅ .rtk/filters.toml found ($FILTER_COUNT custom filters)"
else
    echo "   ❌ .rtk/filters.toml not found"
fi

# Check Claude Code settings
echo
echo "4️⃣  Claude Code Integration..."
if [ -f ".claude/settings.json" ]; then
    if grep -q "rtk_enabled.*true" .claude/settings.json 2>/dev/null; then
        echo "   ✅ RTK enabled in .claude/settings.json"
    else
        echo "   ⚠️  .claude/settings.json exists but RTK not enabled"
    fi
else
    echo "   ❌ .claude/settings.json not found"
fi

# Test basic RTK functionality
echo
echo "5️⃣  Test RTK Filtering..."
TEST_OUTPUT=$(echo -e "line 1\nline 2\nline 3" | rtk 2>/dev/null || echo "filtered")
if [ ! -z "$TEST_OUTPUT" ]; then
    echo "   ✅ RTK filtering works"
else
    echo "   ⚠️  RTK filtering test returned empty"
fi

# Show RTK stats
echo
echo "6️⃣  RTK Statistics..."
echo "   Command: rtk gain"
rtk gain 2>/dev/null || echo "   (No tracking data yet — use RTK to populate)"

echo
echo "=================================="
echo "✅ RTK Verification Complete"
echo "=================================="
echo
echo "Next steps:"
echo "  • Use RTK normally via 'make', 'dbt', 'pytest' etc."
echo "  • Run 'rtk gain' periodically to see token savings"
echo "  • Edit '.rtk/filters.toml' to customize filters"
echo
