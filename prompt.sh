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


EOF
}

main
