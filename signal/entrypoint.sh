#!/bin/sh

set -x
set -e

export SIGNAL_CLI_CONFIG_DIR=/home/.local/share/signal-cli

# Fix permissions to ensure backward compatibility
chown 1000:1000 -R ${SIGNAL_CLI_CONFIG_DIR} 

# Show warning on docker exec
cat <<EOF >> /root/.bashrc
echo "WARNING: signal-cli-rest-api runs as signal-api (not as root!)" 
echo "Run 'su signal-api' before using signal-cli!"
echo "If you want to use signal-cli directly, don't forget to specify the config directory. e.g: \"signal-cli --config ${SIGNAL_CLI_CONFIG_DIR}\""
EOF

cap_prefix="-cap_"
caps="$cap_prefix$(seq -s ",$cap_prefix" 0 $(cat /proc/sys/kernel/cap_last_cap))"

# Start API as signal-api user
exec setpriv --reuid=1000 --regid=1000 --init-groups --inh-caps=$caps signal-cli-rest-api $@
