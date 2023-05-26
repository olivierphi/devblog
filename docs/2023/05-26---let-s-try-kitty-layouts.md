---
title: "Let's try Kitty layouts"
date: "2023-05-26"
categories:
  - "webdev"
tags:
  - "terminal"
---

# Let's try Kitty layouts

## A terminal multiplexer...

As I spend a lot of my time in the terminal emulator, I find it useful to be
able to display several shell sessions at once in the same window - so I can have one session
running my backend app and one running the frontend one for example.

In order to do this I've been using the _terminal multiplexer_ [tmux](https://github.com/tmux/tmux/wiki) for several years, 
and I've been quite happy with it.

## ...And a terminal emulator...

However, I've also been using the awesome terminal emulator [Kitty](https://sw.kovidgoyal.net/kitty/) for a while,
and I have great respect for its author as they're also the developer behind the open source e-books management software
[Calibre](https://calibre-ebook.com/demo#tour) - which is, like Kitty, a fine-tuned mix of C and Python code  :ok_hand: 

And in Kitty's FAQ they say the following:  
> terminal multiplexers are a bad idea, do not use them, if at all possible. kitty contains features that do all of what tmux does, but better

Alright, let's trust them and give Kitty's layouts a try then!

## ...Let's drop tmux, and just use Kitty's layouts!

After having fiddled for a while with Kitty's config, here is the setup I ended up with:

```unixconfig
# ~/.config/kitty/kitty.conf

# My default layout will be "splits". 
# (i.e. on-demand tmux-like panes, "windows" in Kitty's terminology)
# But I also want to be able to switch to "stack" in order to temporarily
# render the active window in full screen within Kitty: 
enabled_layouts splits,stack

# With "f1" I can toggle between the two layouts:
# i.e. with "f1" the windows I'm working in goes full screen, and pressing 
# "f1" again brings back the other windows.
map f1 toggle_layout stack

# With "f5" I can create a new window splitting the space used by the
# existing one, so that the two windows are placed one above the other:
map f5 launch --cwd=current --location=hsplit

# With "f6" I can create a new window splitting the space used by the 
# existing one, so that the two windows are placed side by side:
map f6 launch --cwd=current --location=vsplit
```

Main Kitty documentation pages I've used:

 - https://sw.kovidgoyal.net/kitty/layouts/
 - https://sw.kovidgoyal.net/kitty/conf/

Using only Kitty _feels_ faster indeed, in term of how the terminal emulator's UI reacts. :zap:

Now, I "just" (might take a while :sweat_smile:) have to replace my previous mental map of keyboard shortcuts with the new one, and I should be good to go! :slight_smile:
