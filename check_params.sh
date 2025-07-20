#!/bin/bash

# The script retrieves the list of current subnet and the hyperparameters set for a specific subnet, multiple subnets or all subnets.
# Results: Subnet list directed to log file, hyperparameters directed to <netuid>_results file.

# Check 1: bash check_params.sh <netuid>
# Check all: bash check_params.sh all
# Check many: bash check_params.sh <netuid> <netuid>

YELLOW='\033[1;33m'
RED='\033[1;31m'
RES='\033[0m'

# Determine target netuids
if [ $# -eq 0 ]; then
  echo -e "${RED}Error: Please provide subnet ID(s) or 'all' to process all subnets.${RES}"
  exit 1
fi

# Generate log file name with accurate timestamp
log_file="subnets_$(date +%Y-%m-%d_%H-%M-%S).log"
echo -e "${YELLOW}Log file created${RES}"

# Run btcli s list and redirect to log file
btcli s list > "$log_file"
echo -e "${YELLOW}Subnets retrieved${RES}"

# Extract netuids from the list output (skips header, assuming first line is header)
netuids=$(btcli s list | tail -n +2 | awk '{print $1}' | grep -E '^[0-9]+$')

# Count the total number of subnets
total_subnets=$(echo "$netuids" | wc -w)
echo -e "${YELLOW}Subnets found: $total_subnets${RES}"

echo -e "${YELLOW}Checking hyperparameters${RES}"

if [ $# -eq 1 ] && [ "$1" = "all" ]; then
  echo -e "${YELLOW}No specific subnet(s) provided. Processing all subnets.${RES}"
  target_netuids="$netuids"
else
  target_netuids=""
  for arg in "$@"; do
    if [[ "$arg" =~ ^[0-9]+$ ]] && echo "$netuids" | grep -qw "$arg"; then
      target_netuids="$target_netuids $arg"
    else
      echo -e "${RED}Skipping invalid subnet ID: $arg${RES}"
    fi
  done
fi

# Check if there are any to process
if [ -z "$target_netuids" ]; then
  echo -e "${RED}No valid subnets to process.${RES}"
  exit 1
fi

# Output hyperparameters of each target subnet (netuid) to separate file
for netuid in $target_netuids; do
  echo -e "${YELLOW}Processing subnet $netuid${RES}"
  subnet_file="$netuid"_results""
  btcli s hyperparameters --netuid $netuid > "$subnet_file"
done

echo -e "${YELLOW}Done. Check log file and subnet files for results.${RES}"