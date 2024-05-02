#!/bin/bash

angles=(-90 -60 -30 0 30 60 90)

for angle in "${angles[@]}"; do
    mosquitto_pub -t "hpt" -m "{\"degree\": $angle}"
    sleep 2
done