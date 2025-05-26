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

Fix the error. In these sort of cases it's fine to the code to just log out an
error and return False

\`\`\`python
Traceback (most recent call last):
  File "/root/.local/bin/refine", line 10, in <module>
    sys.exit(main())
             ~~~~^^
  File "/root/.local/share/uv/tools/refine/lib/python3.13/site-packages/refine/main.py", line 152, in main
    asyncio.run(cli())
    ~~~~~~~~~~~^^^^^^^
  File "/usr/lib/python3.13/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "/usr/lib/python3.13/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/usr/lib/python3.13/asyncio/base_events.py", line 719, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "/root/.local/share/uv/tools/refine/lib/python3.13/site-packages/refine/main.py", line 144, in cli
    results = await asyncio.gather(*tasks)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.local/share/uv/tools/refine/lib/python3.13/site-packages/refine/main.py", line 114, in uri_is_relevant
    return await url_is_relevant(client, uri, query)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.local/share/uv/tools/refine/lib/python3.13/site-packages/refine/main.py", line 93, in url_is_relevant
    response.raise_for_status()
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/root/.local/share/uv/tools/refine/lib/python3.13/site-packages/httpx/_models.py", line 829, in raise_for_status
    raise HTTPStatusError(message, request=request, response=self)
httpx.HTTPStatusError: Redirect response '301 Moved Permanently' for url 'https://jvns.ca/newsletter'
Redirect location: '/newsletter/'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301
\`\`\`

EOF
}

main
