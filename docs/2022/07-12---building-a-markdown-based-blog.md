---
title: "Building a Markdown-based blog"
date: "2022-07-12"
categories:
  - "webdev"
tags:
  - "blog"
  - "mkdocs"
  - "python"
hide:
  - footer
---

I've put this devblog online the other day, but haven't documented how I built it yet - 
which will be useful for my future self if I have to do something like this again, and could 
potentially be of some help for other people.    
Here is how I determined what was the quickest way (for me) to put a "devblog"
online as quickly as possible, without hours of setup. :slight_smile:

## Why not Next.js?

My natural "go-to" option would be Next.js, with its [SSG capacities](https://nextjs.org/docs/basic-features/pages#static-generation-with-data)
and [built-in support of MDX](https://nextjs.org/docs/advanced-features/using-mdx).  
Also, I like managing this kind of stuff manually myself - i.e. traversing a folder of Markdown files
at deployment time when Vercel runs `npm run build`, sorting my content, providing the result to 
[getStaticProps](https://nextjs.org/docs/basic-features/data-fetching/get-static-props)... It's genuinely fun :slight_smile:

However, even though I really enjoy doing this kind of work on the Node.js side there is a drawback for me:
I would then have to build the user interface myself.:pensive:  
And my skills in terms of design being as bad as they can be :sweat_smile: , I really don't want to
work for hours on the React side only to end up with an ugly UI.

There are open source or free turnkey blog templates for React/Next.js, of course, but I haven't really 
seen any of their design that I like (that's obviously highly subjective).

Hence my second option...

## Using a documentation engine to make a blog, what could go wrong? :sweat_smile:

...[Material for MKDocs](https://squidfunk.github.io/mkdocs-material/)!

It's not designed to make blogs (even though [it's on the roadmap](https://squidfunk.github.io/mkdocs-material/insiders/?h=blog#12000-piri-piri)),
but it has some common aspects with what I wanted to do:

 - Treats folders of Markdown files (with YAML metadata in their header) as a tree of Web pages
 - Built-in ability to publish static pages to [GitHub Pages](https://pages.github.com/), for free
 - Simple but good-looking user interface theme by default :art:
 - Made with a technology I'm familiar with (Python in this case)
 - Excellent syntax highlighting (will be useful for my snippets :-), powered by Pygments

## Quick setup of "_Material for MKDocs_ as a blog" 

I found two good resources explaining how to use _Material for MKDocs_ as a blog engine, so I could hit the ground
running (I really didn't want to spend hours on this setup :slight_smile:):

 - https://www.dirigible.io/blogs/2021/11/2/material-blogging-capabilities/
 - https://ultrabug.fr/Tech%20Blog/2021/2021-07-28-create-beautiful-and-localized-documentations-and-websites-using-mkdocs-github/

The documentation of _Material for MKDocs_ itself if really nice, and pragmatic - 
explaining very simply for example how one can publish the generated static HTML content to GitHub Pages:

 - https://squidfunk.github.io/mkdocs-material/publishing-your-site

It looked doable! :-)  
Let's give it a shot, with a quick Python setup:
``` bash
$ mkdir devblog && cd devblog/
$ pyenv shell 3.10.4 # (1) 
$ python -m venv .venv # (2)
$ pip install -U pip poetry # (3)
$ poetry init
$ poetry add mkdocs-material mkdocs-awesome-pages-plugin
```

1.  let's use a recent version of Python 
2.  create a virtual env in a ".venv" folder
3.  update pip, install the Poetry package manager

Now all I had to do was to follow what these 2 articles were explaining, browse a bit the 
_Material for MKDocs_ documentation, use the [really nice icons and emojis search](https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/?h=emoji#search)
provided by this documentation (it's the little things ^_^)...  
and a couple of hours later my first blog post was online, automatically
published by a GitHub Action every time I push my `main` branch! :v:

Compared to these two very useful articles, my only personal touch was to add two things I always use in my projects:

 - The modern package manager [Poetry](https://python-poetry.org/) rather than pip (the Python default one)
 - Create a Makefile at the root of the git repository, for the common tasks
