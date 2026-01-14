#!/bin/bash

TARGET_URL="https://localhost"
USERS=1000
DURATION="60s"
THREADS=$(nproc)
LUA_SCRIPT="/tmp/stress_logic.lua"

# --- Get parameters from the command line ---
while getopts "u:t:h:" opt; do
    case ${opt} in
        u) USERS=$OPTARG ;;
        t) DURATION=$OPTARG ;;
        h) TARGET_URL=$OPTARG ;;
        *) echo "How to use: $0 -u [Number of users] -t [Times] -h [url]"; exit 1 ;;
    esac
done

# --- Tuning System ---
echo ">>> [1/3] Optimizing Linux systems..."
sudo prlimit --pid $$ --nofile=65535:65535 > /dev/null 2>&1
sudo sysctl -w net.ipv4.ip_local_port_range="1024 65535" > /dev/null 2>&1

# --- Create a Lua Scenario ---
cat <<'EOF' > $LUA_SCRIPT
local guest_paths = {
    "/",
    "/courses/",
    "/courses/search/autocomplete/?term=react",
    "/courses/react-for-beginners/",
    "/api/docs/",
    "/api/courses/"
}
local student_paths = {
    "/dashboard/",
    "/courses/complete-python-bootcamp/",
    "/courses/complete-python-bootcamp/learning-process/",
    "/courses/complete-python-bootcamp/discussions/",
    "/notifications/",
    "/api/notifications/api/unread-count/"
}
local instructor_paths = {
    "/dashboard/courses/create/",
    "/dashboard/courses/list/legacy/"
}

setup = function(thread)
    local id = tonumber(thread:get("id")) or math.random(1, 1000)
    math.randomseed(os.time() + id)
end

request = function()
    local val = math.random(1, 10)
    local target_path = ""

    if val <= 6 then
        target_path = guest_paths[math.random(#guest_paths)]
    elseif val <= 9 then
        target_path = student_paths[math.random(#student_paths)]
    else
        target_path = instructor_paths[math.random(#instructor_paths)]
    end

    local headers = {}
    headers["X-Stress-Test"] = "True"
    headers["X-User-ID"] = "user_" .. math.random(1, 10000)

    return wrk.format(nil, target_path, headers)
end
EOF

# Clean the file to avoid CRLF errors when copying from Windows
sed -i 's/\r$//' $LUA_SCRIPT

# --- Enforcement ---

echo -e "\e[1;32m>>> [2/3] Running Stress Test: $TARGET_URL | Users: $USERS | Time: $DURATION\e[0m"

wrk -t$THREADS -c$USERS -d$DURATION -s $LUA_SCRIPT --latency $TARGET_URL

# --- Cleanup ---
rm -f $LUA_SCRIPT
echo -e "\n\e[1;34m>>> [3/3] Complete the test.\e[0m"