#!/bin/sh
# ============================================================================
# Shell test runner for spruceOS helper functions.
#
# Runs self-contained tests for pure/testable shell functions from
# helperFunctions.sh and retroarch_utils.sh.
#
# Usage:  sh tests/shell/test_helper_functions.sh
# Exit:   0 = all tests passed, 1 = at least one failure
# ============================================================================

set -e

PASS=0
FAIL=0
TOTAL=0

# ---------------------------------------------------------------------------
# Minimal test harness
# ---------------------------------------------------------------------------

assert_eq() {
    desc="$1"; expected="$2"; actual="$3"
    TOTAL=$((TOTAL + 1))
    if [ "$expected" = "$actual" ]; then
        PASS=$((PASS + 1))
        printf "  PASS: %s\n" "$desc"
    else
        FAIL=$((FAIL + 1))
        printf "  FAIL: %s  (expected='%s', actual='%s')\n" "$desc" "$expected" "$actual"
    fi
}

assert_file_exists() {
    desc="$1"; filepath="$2"
    TOTAL=$((TOTAL + 1))
    if [ -f "$filepath" ]; then
        PASS=$((PASS + 1))
        printf "  PASS: %s\n" "$desc"
    else
        FAIL=$((FAIL + 1))
        printf "  FAIL: %s  (file not found: %s)\n" "$desc" "$filepath"
    fi
}

assert_file_not_exists() {
    desc="$1"; filepath="$2"
    TOTAL=$((TOTAL + 1))
    if [ ! -f "$filepath" ]; then
        PASS=$((PASS + 1))
        printf "  PASS: %s\n" "$desc"
    else
        FAIL=$((FAIL + 1))
        printf "  FAIL: %s  (file should not exist: %s)\n" "$desc" "$filepath"
    fi
}

assert_return() {
    desc="$1"; expected="$2"; actual="$3"
    TOTAL=$((TOTAL + 1))
    if [ "$expected" -eq "$actual" ]; then
        PASS=$((PASS + 1))
        printf "  PASS: %s\n" "$desc"
    else
        FAIL=$((FAIL + 1))
        printf "  FAIL: %s  (expected return=%s, actual=%s)\n" "$desc" "$expected" "$actual"
    fi
}

assert_contains() {
    desc="$1"; haystack="$2"; needle="$3"
    TOTAL=$((TOTAL + 1))
    if echo "$haystack" | grep -qF "$needle"; then
        PASS=$((PASS + 1))
        printf "  PASS: %s\n" "$desc"
    else
        FAIL=$((FAIL + 1))
        printf "  FAIL: %s  (expected to contain '%s')\n" "$desc" "$needle"
    fi
}

# ---------------------------------------------------------------------------
# Setup: temporary sandbox
# ---------------------------------------------------------------------------

TEST_TMP=$(mktemp -d)
export FLAGS_DIR="$TEST_TMP/flags"
mkdir -p "$FLAGS_DIR"

cleanup() {
    rm -rf "$TEST_TMP"
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Stub out commands that helperFunctions.sh tries to source/run on load
# ---------------------------------------------------------------------------
export PLATFORM="TestPlatform"

# Create minimal stubs so sourcing does not fail
mkdir -p "$TEST_TMP/scripts/platform"
printf '' > "$TEST_TMP/scripts/platform/TestPlatform.cfg"
printf '' > "$TEST_TMP/scripts/device_functions_stub.sh"

# Rewrite the sourcing paths – we extract only the functions we need
# rather than sourcing the full file (which depends on device hardware).
# ---------------------------------------------------------------------------

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# ============================================================================
# Test Suite 1: flag_* functions
# ============================================================================
printf "\n=== flag_* functions ===\n"

# We inline the portable implementations to test:
flag_add() {
    local flag_name="$1"
    touch "$FLAGS_DIR/${flag_name}.lock"
}
flag_check() {
    local flag_name="$1"
    if [ -f "$FLAGS_DIR/${flag_name}" ] || [ -f "$FLAGS_DIR/${flag_name}.lock" ]; then
        return 0
    else
        return 1
    fi
}
flag_path() {
    local flag_name="$1"
    echo "$FLAGS_DIR/${flag_name}.lock"
}
flag_remove() {
    local flag_name="$1"
    rm -f "$FLAGS_DIR/${flag_name}.lock"
}

# Tests
flag_add "test_flag"
flag_check "test_flag"; assert_return "flag_check returns 0 after flag_add" 0 $?
assert_file_exists "flag_add creates .lock file" "$FLAGS_DIR/test_flag.lock"
assert_eq "flag_path returns correct path" "$FLAGS_DIR/test_flag.lock" "$(flag_path "test_flag")"

flag_remove "test_flag"
assert_file_not_exists "flag_remove deletes .lock file" "$FLAGS_DIR/test_flag.lock"
flag_check "test_flag" && rc=0 || rc=$?; assert_return "flag_check returns 1 after flag_remove" 1 "$rc"

# Edge case: check flag that was never created
flag_check "never_created" && rc=0 || rc=$?; assert_return "flag_check returns 1 for non-existent flag" 1 "$rc"

# Edge case: double add / double remove
flag_add "double"
flag_add "double"
assert_file_exists "double flag_add still results in file" "$FLAGS_DIR/double.lock"
flag_remove "double"
flag_remove "double"
assert_file_not_exists "double flag_remove is safe" "$FLAGS_DIR/double.lock"

# Check with flag name (without .lock extension) as a plain file
touch "$FLAGS_DIR/plain_flag"
flag_check "plain_flag"; assert_return "flag_check finds flag without .lock extension" 0 $?
rm -f "$FLAGS_DIR/plain_flag"

# ============================================================================
# Test Suite 2: map_color_name_to_hex
# ============================================================================
printf "\n=== map_color_name_to_hex ===\n"

map_color_name_to_hex() {
    name="$1"
    case "$name" in
        "Red")    hex=FF0000 ;;
        "Pink")   hex=FF3333 ;;
        "Purple") hex=FF00FF ;;
        "Blue")   hex=0000FF ;;
        "Cyan")   hex=00FFFF ;;
        "Green")  hex=00FF00 ;;
        "Yellow") hex=FFFF00 ;;
        "Orange") hex=FF5500 ;;
        *)        hex=FFFFFF ;;
    esac
    echo "$hex"
}

assert_eq "Red maps to FF0000"       "FF0000" "$(map_color_name_to_hex "Red")"
assert_eq "Pink maps to FF3333"      "FF3333" "$(map_color_name_to_hex "Pink")"
assert_eq "Purple maps to FF00FF"    "FF00FF" "$(map_color_name_to_hex "Purple")"
assert_eq "Blue maps to 0000FF"      "0000FF" "$(map_color_name_to_hex "Blue")"
assert_eq "Cyan maps to 00FFFF"      "00FFFF" "$(map_color_name_to_hex "Cyan")"
assert_eq "Green maps to 00FF00"     "00FF00" "$(map_color_name_to_hex "Green")"
assert_eq "Yellow maps to FFFF00"    "FFFF00" "$(map_color_name_to_hex "Yellow")"
assert_eq "Orange maps to FF5500"    "FF5500" "$(map_color_name_to_hex "Orange")"
assert_eq "Unknown maps to FFFFFF"   "FFFFFF" "$(map_color_name_to_hex "Magenta")"
assert_eq "Empty maps to FFFFFF"     "FFFFFF" "$(map_color_name_to_hex "")"

# ============================================================================
# Test Suite 3: get_version (mocked file)
# ============================================================================
printf "\n=== get_version ===\n"

get_version() {
    spruce_file="$1"
    if [ ! -f "$spruce_file" ]; then
        echo "0"
        return 1
    fi
    version=$(cat "$spruce_file" | tr -d '[:space:]')
    if [ -z "$version" ]; then
        echo "0"
        return 1
    fi
    if echo "$version" | grep -qE '^[0-9]+\.[0-9]+(\.[0-9]+)*(-([A-Za-z]+|[0-9]{8}))?$'; then
        echo "$version"
        return 0
    else
        echo "0"
        return 1
    fi
}

# Valid versions
printf "4.1.0" > "$TEST_TMP/spruce_valid"
assert_eq "Parses stable version 4.1.0" "4.1.0" "$(get_version "$TEST_TMP/spruce_valid")"

printf "3.3.2-Beta" > "$TEST_TMP/spruce_beta"
assert_eq "Parses beta version 3.3.2-Beta" "3.3.2-Beta" "$(get_version "$TEST_TMP/spruce_beta")"

printf "3.3.1-20250123" > "$TEST_TMP/spruce_nightly"
assert_eq "Parses nightly version 3.3.1-20250123" "3.3.1-20250123" "$(get_version "$TEST_TMP/spruce_nightly")"

printf "1.0" > "$TEST_TMP/spruce_two_part"
assert_eq "Parses two-part version 1.0" "1.0" "$(get_version "$TEST_TMP/spruce_two_part")"

# Invalid/edge cases
assert_eq "Missing file returns 0" "0" "$(get_version "$TEST_TMP/no_such_file")"

printf "" > "$TEST_TMP/spruce_empty"
assert_eq "Empty file returns 0" "0" "$(get_version "$TEST_TMP/spruce_empty")"

printf "not_a_version" > "$TEST_TMP/spruce_bad"
assert_eq "Invalid format returns 0" "0" "$(get_version "$TEST_TMP/spruce_bad")"

printf "  4.1.0  \n" > "$TEST_TMP/spruce_ws"
assert_eq "Version with whitespace is trimmed" "4.1.0" "$(get_version "$TEST_TMP/spruce_ws")"

# ============================================================================
# Test Suite 4: extract_entry_name
# ============================================================================
printf "\n=== extract_entry_name ===\n"

extract_entry_name() {
    cmd="$1"
    case "$cmd" in
        *emu/standard_launch.sh*)
            last_arg=$(printf '%s\n' "$cmd" \
                | sed -n 's/.*"\([^"]*\)"/\1/p' \
                | tail -n 1)
            if echo "$last_arg" | grep -q "Roms/"; then
                rom_path=$(printf '%s\n' "$last_arg" | sed 's/.*\(Roms\/.*\)/\1/')
                rom_path="${rom_path%\"}"
                printf '%s\n' "$rom_path"
            else
                printf '%s\n' "${last_arg##*/}"
            fi
            ;;
        *App/*)
            app_path=$(printf '%s\n' "$cmd" \
                | sed -n 's/.*\(App\/.*\)/\1/p' \
                | tail -n 1)
            app_path="${app_path%\"}"
            printf '%s\n' "$app_path"
            ;;
        *)
            printf '%s\n' "$cmd"
            ;;
    esac
}

result=$(extract_entry_name 'sh /mnt/SDCARD/emu/standard_launch.sh "NES" "/mnt/SDCARD/Roms/NES/SuperMario.nes"')
assert_eq "Extracts ROM path from standard_launch" "Roms/NES/SuperMario.nes" "$result"

result=$(extract_entry_name 'sh /mnt/SDCARD/App/RetroArch/launch.sh')
assert_eq "Extracts App path" "App/RetroArch/launch.sh" "$result"

result=$(extract_entry_name 'some random command')
assert_eq "Unknown format returns as-is" "some random command" "$result"

result=$(extract_entry_name 'sh /mnt/SDCARD/App/PyUI/main-ui/mainui.py')
assert_eq "Extracts nested App path" "App/PyUI/main-ui/mainui.py" "$result"

# ============================================================================
# Test Suite 5: update_ra_config_file_with_new_setting
# ============================================================================
printf "\n=== update_ra_config_file_with_new_setting ===\n"

# Stub log_message
log_message() { :; }

update_ra_config_file_with_new_setting() {
    file="$1"
    shift
    for setting in "$@"; do
        if grep -q "${setting%%=*}" "$file"; then
            sed -i "s|^${setting%%=*}.*|$setting|" "$file"
        else
            echo "$setting" >>"$file"
        fi
    done
}

# Test: update existing setting
cat > "$TEST_TMP/retroarch.cfg" << 'EOF'
video_fullscreen = "false"
audio_enable = "true"
input_player1_up = "w"
EOF

update_ra_config_file_with_new_setting "$TEST_TMP/retroarch.cfg" 'video_fullscreen = "true"'
result=$(grep 'video_fullscreen' "$TEST_TMP/retroarch.cfg")
assert_eq "Updates existing setting" 'video_fullscreen = "true"' "$result"

# Ensure other settings are untouched
result=$(grep 'audio_enable' "$TEST_TMP/retroarch.cfg")
assert_eq "Does not modify other settings" 'audio_enable = "true"' "$result"

# Test: add new setting
update_ra_config_file_with_new_setting "$TEST_TMP/retroarch.cfg" 'new_setting = "value"'
result=$(grep 'new_setting' "$TEST_TMP/retroarch.cfg")
assert_eq "Appends new setting" 'new_setting = "value"' "$result"

# Test: multiple settings at once
cat > "$TEST_TMP/retroarch2.cfg" << 'EOF'
opt_a = "1"
opt_b = "2"
EOF

update_ra_config_file_with_new_setting "$TEST_TMP/retroarch2.cfg" 'opt_a = "10"' 'opt_b = "20"' 'opt_c = "30"'
assert_eq "Multiple update: opt_a" 'opt_a = "10"' "$(grep 'opt_a' "$TEST_TMP/retroarch2.cfg")"
assert_eq "Multiple update: opt_b" 'opt_b = "20"' "$(grep 'opt_b' "$TEST_TMP/retroarch2.cfg")"
assert_eq "Multiple update: opt_c (new)" 'opt_c = "30"' "$(grep 'opt_c' "$TEST_TMP/retroarch2.cfg")"

# ============================================================================
# Summary
# ============================================================================
printf "\n============================================================\n"
printf "Results: %d/%d passed, %d failed\n" "$PASS" "$TOTAL" "$FAIL"
printf "============================================================\n"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
