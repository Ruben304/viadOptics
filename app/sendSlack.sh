#!/bin/bash

# Slack webhook URL
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/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"

# Get IP address
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)

# Get network name
NETWORK_NAME=$(iwgetid -r)  # Assumes you have the 'iw' package installed for wireless networks

# Get current time
CURRENT_TIME=$(date +"%Y-%m-%d %H:%M:%S")

# Attribution information
ATTRIBUTION="Message sent from a Raspberry Pi using a script created by OpenAI's GPT-3.5 model."

# Create JSON payload for Slack message
PAYLOAD='{
  "text": "Raspberry Pi Notification",
  "attachments": [
    {
      "fallback": "IP and Network Details",
      "color": "#36a64f",
      "fields": [
        {
          "title": "IP Address",
          "value": "'"$IP_ADDRESS"'",
          "short": true
        },
        {
          "title": "Network Name",
          "value": "'"$NETWORK_NAME"'",
          "short": true
        },
        {
          "title": "Time",
          "value": "'"$CURRENT_TIME"'",
          "short": true
        },
        {
          "title": "Attribution",
          "value": "'"$ATTRIBUTION"'",
          "short": false
        }
      ]
    }
  ]
}'

# Send message to Slack
curl -X POST -H 'Content-type: application/json' --data "$PAYLOAD" $SLACK_WEBHOOK_URL