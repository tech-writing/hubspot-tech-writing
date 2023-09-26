# Test Data


## About

This folder includes data suitable for testing.

- The blog post.
  https://cratedb.com/blog/introduction-to-time-series-modeling-with-cratedb

- Full JSON and `postBody` representations sourced from HubSpot API.
  https://app.hubspot.com/api/blogs/v3/blog-posts/136061503799

- The original source file, written in Markdown.

- A single instance of a HubSpot module block. In this case, it defines
  a code block. Its name is `/sf2-crate/modules/Code Block`.
  https://developers.hubspot.com/docs/cms/building-blocks/modules/using-modules-in-templates


## Details

- The JSON file has been formatted using `jq`.
- The HTML has been generated using this command:
  ```shell
  cat hubspot-blog-post-all.json | jq -r .postBody > hubspot-blog-post-body.html
  ```
- The code block has been manually reformatted for improved readability.
