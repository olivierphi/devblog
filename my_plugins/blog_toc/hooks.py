import re
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import NamedTuple

from mkdocs.structure.pages import Page


def on_page_markdown(markdown: str, page: Page, **kwargs) -> str:
    """
    Quick (and probably rather inefficient in terms of performance 😅) implementation of a "[BLOG_TOC]" placeholder.
    Modeled after having looked at the source code of the built-in `tags`plugin of Material for MKDocs,
    and built with the nice "mkdocs-simple-hooks" package to make it easier to plug to MKDocs :-)

    # @link https://github.com/aklajnert/mkdocs-simple-hooks
    """
    if page.abs_url != "/":
        return markdown  # we generate the blog TOC only on the homepage

    if "[BLOG_TOC]" not in markdown:
        return markdown

    return markdown.replace(
        "[BLOG_TOC]",
        "Blog posts:\n\n- "
        + "\n- ".join([f"{post.publication_date} -- [{post.title}]({post.url})" for post in _get_blog_posts()]),
    )


_BLOG_POST_MARKDOWN_FILENAME_PATTERN = re.compile(r"^(?P<month>\d{2})-(?P<day>\d{2})---(?P<slug>.*)\.md$")
_BLOG_POST_METADATA_QUICK_TITLE_PATTERN = re.compile(r'^title:\s*"([^"]+)"\s*$', flags=re.MULTILINE)


class BlogPostSummary(NamedTuple):
    title: str
    url: str
    publication_date: date


def _get_blog_posts() -> Sequence[BlogPostSummary]:
    posts = []

    posts_folder_path = Path(__file__).parent / ".." / ".." / "docs"
    for markdown_file_path in posts_folder_path.glob("**/*.md"):
        if not (file_name_match := _BLOG_POST_MARKDOWN_FILENAME_PATTERN.match(markdown_file_path.name)):
            continue

        with markdown_file_path.open(mode="r") as f:
            # Our title being our first metadata, it should be contained in the first 500 bytes of the Markdown file:
            file_head = f.read(500)
        if not (metadata_title_match := _BLOG_POST_METADATA_QUICK_TITLE_PATTERN.search(file_head)):
            continue

        month, day, slug = file_name_match.groups()
        year = markdown_file_path.parent.name
        publication_date = date.fromisoformat(f"{year}-{month}-{day}")

        title = metadata_title_match[1]

        url = f"/{year}/{month}-{day}---{slug}"

        posts.append(BlogPostSummary(title=title, url=url, publication_date=publication_date))

    return sorted(posts, key=lambda post: post.publication_date, reverse=True)
