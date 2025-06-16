#!/bin/bash

INPUT_DIR="/var/opt/netsage-grafana/netsage-grafana-configs/org_main-org"
BIN_DIR="/home/tierney/src/netsage-grafana-configs/scripts"
OUTPUT_DIR="/var/opt/netsage-grafana/netsage-grafana-configs/output"
LOG_DIR="/tmp"

cd "$INPUT_DIR" || exit 1

$BIN_DIR/generate_dashboards.py -org TACC -o "$OUTPUT_DIR" > "$LOG_DIR/TACC.out"
$BIN_DIR/generate_dashboards.py -org GPN -o "$OUTPUT_DIR" > "$LOG_DIR/GPN.out"
$BIN_DIR/generate_dashboards.py -org FRGP -o "$OUTPUT_DIR" > "$LOG_DIR/FRGP.out"
$BIN_DIR/generate_dashboards.py -org LEARN -o "$OUTPUT_DIR" > "$LOG_DIR/LEARN.out"
$BIN_DIR/generate_dashboards.py -org SoX -o "$OUTPUT_DIR" > "$LOG_DIR/SoX.out"
$BIN_DIR/generate_dashboards.py -org SCN -o "$OUTPUT_DIR" > "$LOG_DIR/SCN.out"
$BIN_DIR/generate_dashboards.py -org PIREN -o "$OUTPUT_DIR" > "$LOG_DIR/PIREN.out"
$BIN_DIR/generate_dashboards.py -org ACCESS -o "$OUTPUT_DIR" > "$LOG_DIR/ACCESS.out"
$BIN_DIR/generate_dashboards.py -org Globus -o "$OUTPUT_DIR" > "$LOG_DIR/Globus.out"
$BIN_DIR/generate_dashboards.py -org EPOC -o "$OUTPUT_DIR" > "$LOG_DIR/EPOC.out"

