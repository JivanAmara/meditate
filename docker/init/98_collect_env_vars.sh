#!/bin/bash
# Environment variables, such as those set when docker container is started aren't available to
#   cron by default.
# This gives cron scripts a place to collect these settings from.
cat /dev/null > /opt/meditate/env_vars

# for ev in $(env | grep -v '%s'); do echo export $ev >> /opt/meditate/env_vars; done
env | while IFS='' read -r line || [[ -n "$line" ]]; do
    echo export $line | grep -v '%s' >> /opt/meditate/env_vars
done;
