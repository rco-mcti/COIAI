
import subprocess
import json
import argparse
import sys
import os

# Ensure clean output encoding
sys.stdout.reconfigure(encoding='utf-8')

def run_command(command):
    try:
        # shell=True on Linux (Action runner) might behave differently, but list args are safer if no shell features needed.
        # However, for 'gh' command string, shell=True is often easier.
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return None

def get_issues(state='open'):
    # Get all open issues. Limit to a reasonable number to avoid timeouts, or loop.
    cmd = 'gh issue list --state open --limit 500 --json number,title'
    output = run_command(cmd)
    if output:
        return json.loads(output)
    return []

def delete_issue(number):
    print(f"Deleting issue #{number}...")
    # --yes to confirm deletion without prompt
    run_command(f'gh issue delete {number} --yes')

def main():
    parser = argparse.ArgumentParser(description="Cleanup GitHub Issues.")
    parser.add_argument("--delete", action="store_true", help="Delete issues instead of just listing.")
    parser.add_argument("--pattern", type=str, default="[HU", help="Pattern to match in title (default: '[HU')")
    args = parser.parse_args()

    print(f"--- Cleaning up issues matching: '{args.pattern}' ---")
    issues = get_issues()
    print(f"Found {len(issues)} open issues total.")
    
    count = 0
    for issue in issues:
        title = issue.get('title', '')
        number = issue.get('number')
        
        if args.pattern in title:
            if args.delete:
                delete_issue(number)
            else:
                print(f"[Would Delete] #{number}: {title}")
            count += 1
            
    print(f"Processed {count} issues.")

if __name__ == "__main__":
    main()
