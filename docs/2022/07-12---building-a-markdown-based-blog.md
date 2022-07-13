---
title: "Building a Markdown-based blog"
date: "2022-07-12"
categories:
  - "webdev"
tags:
  - "blog"
  - "mkdocs"
  - "python"
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

## Material for MKDocs

Or:
> Using a documentation engine to make a blog, what could go wrong? :sweat_smile:

_(spoiler: it was quick and fun to do, I regret nothing :-)_

### MkDocs and its modern Material theme

[MkDocs](https://www.mkdocs.org/) is a static documentation generator, programmed in Python and configurable in YAML,
created (if I'm not wrong) by Tom Christie - who's also behind huge Python projects like 
[Django REST Framework](https://www.django-rest-framework.org/) or [Starlette](https://www.starlette.io/).   

!!! question
    I don't know the history of MkDocs, but I guess Tom Christie created it to document Django REST Framework?
  
[Material for MKDocs](https://squidfunk.github.io/mkdocs-material/) is a theme for MKDocs, based on Google's
Material UI guidelines, that make MKDocs look much more modern 
(as great as the project is, MKDocs' default theme shows its age nowadays).

### Why they can be relevant to build a simple devblog

Neither MKDocs or _Material for MKDocs_ are designed to make blogs (even though [it's on the roadmap](https://squidfunk.github.io/mkdocs-material/insiders/?h=blog#12000-piri-piri)),
but they have some common aspects with what I wanted to do:

 - Treats folders of Markdown files (with YAML metadata in their header) as a tree of Web pages
 - Built-in ability to publish static pages to [GitHub Pages](https://pages.github.com/), for free
 - Simple but good-looking user interface theme **by default** :art: , so I don't have to fiddle with HTML and CSS but
   can focus on the content itself 
 - Made with a technology I'm familiar with (Python in this case)
 - Excellent syntax highlighting (will be useful for my snippets :-), powered by Pygments

The plugin [mkdocs-awesome-pages-plugin](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin) also helps,
so I don't have to build the whole navigation tree manually in the `mkdocs.yml` file :ok_hand:

### Quick setup of "_Material for MKDocs_ as a blog" 

I found two good resources explaining how to use _Material for MKDocs_ as a blog engine, so I could hit the ground
running (I really didn't want to spend hours on this setup :slight_smile:):

 - https://www.dirigible.io/blogs/2021/11/2/material-blogging-capabilities/
 - https://ultrabug.fr/Tech%20Blog/2021/2021-07-28-create-beautiful-and-localized-documentations-and-websites-using-mkdocs-github/

The documentation of _Material for MKDocs_ itself if really nice, and pragmatic - 
explaining very simply for example how one can publish the generated static HTML content to GitHub Pages:

 - https://squidfunk.github.io/mkdocs-material/publishing-your-site

It was looking doable! :-)  
Let's give it a shot, with a quick Python setup:
``` bash
$ mkdir devblog && cd devblog/
$ pyenv shell 3.10.4 # (1) 
$ python -m venv .venv # (2)
$ source .venv/bin/activate # (3)
$ pip install -U pip poetry # (4)
$ poetry init # (5)
$ poetry add \ # (6)
    mkdocs-material \
    mkdocs-awesome-pages-plugin
```

1. let's use a recent version of Python 
2. create a virtual env in a ".venv" folder
3. activate the virtual env: from now on the Python-related commands we type only impact the ".venv" folder
4. in the virtual env, update pip and install the Poetry package manager
5. initialise Poetry for this project
6. ask Poetry to install the few packages we need for this blog

Now all I had to do was to follow what these 2 articles were explaining, browse a bit the 
_Material for MKDocs_ documentation, use the [really nice icons and emojis search](https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/?h=emoji#search)
provided by this documentation (it's the little things ^_^)...  
and a couple of hours later my first blog post was online, automatically
published by a GitHub Action every time I push my `main` branch! :v:

### My quick personal touch :ok_hand:

Compared to these two very useful articles, my only personal touch was to add two things I always use in my projects:

 - The modern package manager [Poetry](https://python-poetry.org/) rather than pip (the Python default one)
 - Create a Makefile at the root of the git repository, for the common tasks

I also wanted to automate the "posts table of content" on the blog homepage.  
I chose to do it myself, mainly because it's the kind of things I really enjoy coding ^_^  

The logic lives in the [my_plugins/blog_toc/hooks.py](https://github.com/DrBenton/devblog/blob/main/my_plugins/blog_toc/hooks.py) 
Python file, plugged to the MKDocs generation lifecycle with the nice 
[mkdocs-simple-hooks](https://github.com/aklajnert/mkdocs-simple-hooks) 
package for the sake of simplicity :slight_smile:

Later on I added the generation of a RSS feed when the blog is built, powered by the
[mkdocs-rss-plugin](https://guts.github.io/mkdocs-rss-plugin/) package.
