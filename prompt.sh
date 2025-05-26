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
# refine
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

Fix the error:
$(run uv run refine --input uris "painting")

EOF
}

main

#
#
#\`\`\`python
#from openai import OpenAI
#from pydantic import BaseModel
#
#client = OpenAI()
#
#class CalendarEvent(BaseModel):
#    name: str
#    date: str
#    participants: list[str]
#
#response = client.responses.parse(
#    model="gpt-4o-mini",
#    input=[
#        {"role": "system", "content": "Extract the event information."},
#        {
#            "role": "user",
#            "content": "Alice and Bob are going to a science fair on Friday.",
#        },
#    ],
#    text_format=CalendarEvent,
#)
#
#event = response.output_parsed
#\`\`\`
#
#Make sure the code you write can handle images as well! See below for reference -
#that 'image_url' can be a base64 encoded string, which is what we will want
#for transmitting local images
#
#\`\`\`python
#from openai import OpenAI
#
#client = OpenAI()
#
#response = client.responses.create(
#    model="gpt-4.1",
#    input=[
#        {
#            "role": "user",
#            "content": [
#                { "type": "input_text", "text": "what is in this image?" },
#                {
#                    "type": "input_image",
#                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
#                }
#            ]
#        }
#    ]
#)
#
#print(response)
#\`\`\`
