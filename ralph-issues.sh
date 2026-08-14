#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <iterations>"
  exit 1
fi

for ((i=1; i<=$1; i++)); do
  echo "=== Iteration $i ==="

  result=$(claude --permission-mode acceptEdits \
	  --allowedTools "Bash(gh:*)" "Bash(git:*)" "Bash(npm:*)" "Bash(pnpm:*)" \
	  -p "@progress.txt \
  1. Run 'gh issue list --state open --json number,title,body,labels' to see all open issues. \
  2. For each issue, check if it's blocked: \
     - Skip it if it has a 'blocked' label. \
     - Skip it if its body contains 'Blocked by #<N>' and issue #N is still open (run 'gh issue view <N> --json state' to check). \
  3. From the remaining unblocked issues, pick the one with the lowest issue number (oldest/first). \
  4. Run 'gh issue view <number>' to read its full description. \
  5. Implement that issue. \
  6. Run tests and type checks; make sure they pass. \
  7. Commit your changes referencing the issue number (e.g. 'fixes #<number>'). \
  8. Run 'gh issue close <number> --comment \"<summary of what was done>\"'. \
  9. Append a one-line summary to progress.txt: '[Iteration $i] Closed #<number>: <summary>'. \
  ONLY WORK ON ONE ISSUE THIS RUN. \
  If there are no unblocked open issues remaining, do nothing else and output <promise>COMPLETE</promise>.")

  echo "$result"

  if [[ "$result" == *"<promise>COMPLETE</promise>"* ]]; then
    echo "All unblocked issues resolved after $i iterations."
    exit 0
  fi
done

echo "Reached iteration cap ($1) without exhausting the backlog."
