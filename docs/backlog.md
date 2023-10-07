# Backlog


## Iteration +1

### Functionality
- Upload images and translate references
- Check if there are console responses about created/deleted entities
- Learning from https://cratedb.com/blog/full-text-search-exploring-the-netflix-catalog?hs_preview=dhgOjRFi-136979202693
  - Use HubSpot title from Markdown
  - Remove MyST specialities, e.g. `(full-text)=`
- File bug: Uploading/updating blog post via identifier does not work
- Don't upload files over and over again
- Release 0.1.0

### Documentation
- Document new operations
- Collect a few typical glitches to reference within the "problem statement"
  section of the documentation
- Improve README
  - Refer to "typical glitches"
  - Educate users about `--content-group-id=`


## Iteration +2
- Image optimization: ImageMagick resize + oxipng
- > Blog posts may not contain embedded images
  => Strip all embedded images, and warn about it
- Table of contents
  https://cratedb.com/blog/how-to-automatically-create-and-manage-database-backups#table-of-contents
- Linter
  - Run link checker
  - Warn about missing or duplicate alt texts, or `img alt="Alt text"` for images
  - Warn about asymmetric heading levels
  - markuplint and htmlhint
  - Markdown and reStructuredText linters
- Also check missing links to inline [foo]
- Converge content from Discourse,
  e.g. https://community.crate.io/t/how-to-connect-your-cratedb-data-to-llm-with-llamaindex-and-azure-openai/1612/1
- How to get hold of the preview token for a certain page, like
  `?hs_preview=ccUoRckH-136775588263`?

## Iteration +3

### Integration: Quarto
- https://quarto.org/docs/get-started/hello/jupyter.html
- https://github.com/quarto-dev/quarto-cli/pkgs/container/quarto-full

### Integration: Observable
- https://observablehq.com/plot
- https://observablehq.com/solutions/sql-users
- https://observablehq.com/@observablehq/databases?collection=@observablehq/getting-data-in-and-out
- https://observablehq.com/@observablehq/database-client-specification
- https://observablehq.com/@observablehq/introduction-to-ai-assist
- https://observablehq.com/blog/improving-ai-assist

### write freely
- https://writefreely.org/
- https://github.com/writefreely/writefreely


## Done
- Permalinks for headers
- Upload blog post
- Upload files
- Delete blog posts and files
