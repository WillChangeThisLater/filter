#!/bin/bash

set -euo pipefail

reference_links=(
  "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html"
  "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Message.html"
  "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ContentBlock.html"
  "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ImageBlock.html"
  "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ImageSource.html"
  "https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-examples.html"
)

# Function to display references in a readable manner
references() {
  echo "# Reference Index"
  for reference_link in "${reference_links[@]}"; do
    # Print a header with Markdown style
    echo -e "\n## Reference: $reference_link\n"
    lynx -dump -nolist "$reference_link"
    echo -e "\n"
  done
}

run() {
    echo "$@" >&2
    echo "\`\`\`bash"
    echo "\$ $@"
    $@ 2>&1
    echo "\`\`\`"
}

about() {
  cat <<EOF
# filter
## Project structure and files
$(tree)
$(files-to-prompt . --ignore prompt.sh --ignore uv.lock)

## Project purpose
This tool responds to 'uri's passed in
via stdin (newline delimited). These uris
could be things like:

\`\`\`uris
/path/to/book.txt
/path/to/image.jpg
\`\`\`
EOF
}

main() {
  cat <<EOF
$(about)

'filter' works, but it can hit intermittent 403 and 503 errors.
Add retries to the script (GET requests should retry up to N times
with exponential backoff. N should default to 3)

\`\`\`bash
$ crawl -s -d 1 https://www.hackernews.com/ | grep "item?id" | filter "Related to AI, LLMs, Bash scripting, or Python/Go" --concurrency 2
HTTP error occurred: Client error '403 Forbidden' for url 'https://news.ycombinator.com/item?id=44098579'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403
HTTP error occurred: Client error '403 Forbidden' for url 'https://news.ycombinator.com/item?id=44097637'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403
HTTP error occurred: Server error '503 Service Temporarily Unavailable' for url 'https://news.ycombinator.com/item?id=44074775'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503
https://news.ycombinator.com/item?id=44098706
https://news.ycombinator.com/item?id=44099187
https://news.ycombinator.com/item?id=44096395
https://news.ycombinator.com/item?id=44098772
https://news.ycombinator.com/item?id=44096251
https://news.ycombinator.com/item?id=44097490
https://news.ycombinator.com/item?id=44093334
https://news.ycombinator.com/item?id=44095608
https://news.ycombinator.com/item?id=44070626
\`\`\`

EOF
}

main
