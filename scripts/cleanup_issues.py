
import subprocess
import json
import argparse
import sys
import os

# Ensure default encoding for prints
sys.stdout.reconfigure(encoding='utf-8')

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        if e.stderr:
            print(e.stderr)
        return None

def get_issues(state='open'):
    cmd = f'gh issue list --state {state} --limit 100 --json number,title'
    output = run_command(cmd)
    if output:
        return json.loads(output)
    return []

def close_issue(number):
    print(f"Closing issue #{number}...")
    run_command(f'gh issue close {number}')

def delete_issue(number):
    print(f"Deleting issue #{number}...")
    run_command(f'gh issue delete {number} --yes')

def main():
    parser = argparse.ArgumentParser(description="Cleanup GitHub Issues.")
    parser.add_argument("--delete", action="store_true", help="Delete issues instead of closing.")
    parser.add_argument("--pattern", type=str, default="[HU", help="Pattern to match in title (default: '[HU')")
    args = parser.parse_args()

    print(f"Searching issues matching pattern: '{args.pattern}'...")
    issues = get_issues()
    print(f"Found {len(issues)} open issues.")

    count = 0
    for issue in issues:
        title = issue['title']
        number = issue['number']
        
        if args.pattern and args.pattern not in title:
            continue
            
        if args.delete:
            delete_issue(number)
        else:
            close_issue(number)
        count += 1
    
    print(f"Processed {count} issues.")

if __name__ == "__main__":
    main()
