---
title: "Triggering a GitHub Action from an external source"
date: "2022-07-26"
categories:
  - "webdev"
tags:
  - "TIL"
  - "github"
---

# Triggering a GitHub Action from an external source

!!! abstract
    TIL: **a GitHub Action on a given repository can trigger Actions on other GitHub repositories** - which is really handy, 
    and enables fancy scenarios of cooperation between repositories! :fontawesome-solid-plug-circle-bolt: 

## Setting up a self-updating GitHub profile, following the steps shared by [Simon Willison](https://simonwillison.net/)

Yesterday I've set up a custom GitHub profile, and that README file includes a "code-generated" part that
automatically displays the last entries from this devblog.  
It was fun! :slight_smile:

I've followed the instructions from GitHub themselves, as well as the content
generously shared by Simon Willison on his blog about explaining how his own (shiny :star2:) GitHub profile
is automatically updated once an hour with quite a lot of dynamic content:

 - https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme
 - https://simonwillison.net/2020/Jul/10/self-updating-profile-readme/

So far so good, by copy-pasting most of his code and adapting it to my own case I got
[my own GitHub profile](https://github.com/olivierphi) also updated automatically once an hour.

!!! note
    The main difference between Simon Willison's build script and mine is that
    the dynamic content I have in my own README is much smaller, as **I only want to display
    the last 10 items of this devblog there**.  
    As a result the process can be simpler - and even managed only with Python and its standard library!  

    Using the standard library to fetch the RSS feed of this devblog over HTTP and
    then parse it is a bit less straightforward than what I could have done with higher level packages
    like [Requests](https://requests.readthedocs.io/en/latest/) and [feedparser](https://feedparser.readthedocs.io/en/latest/),
    but it's still pretty simple :slight_smile:

    The main drawback is probably that Python's [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html)
    has a big red warning saying it is **"not secure against maliciously constructed data"** - but in my case
    what I parse is the RSS feed from my own blog, so it shouldn't be a problem :fingers_crossed:

My own "README update" script is there:

 - https://github.com/olivierphi/olivierphi/blob/main/build_readme.py

## Updating the GitHub profile only when the devblog is updated

My friend [Yann](https://www.einenlum.com/) noticed that triggering this README generation once an hour
doesn't really make sense, since contrary to Simon Willison the only source of dynamic data in this profile
is the devblog: so what would be ideal would be **to automatically update the README only when the devblog is updated**.

Two hours in the GitHub Actions documentation later, I got it working - let's keep a note of how to do this,
so I can do it again later on more easily :sweat_smile:

### Triggering a GitHub Action from an external source

It seems that the only way to trigger a GitHub Action from an event that is not on the GitHub repository itself is to use
[the `repository_dispatch` event](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#repository_dispatch).

In my case the emitter of the event will be a GitHub Action living on this `devblog` repository,
while the receiver will be another GitHub Action, living in the `olivierphi` repository.  
_(since my GitHub profile is "olivierphi", according to [the doc](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme)
my GitHub profile must be a README file living in a GitHub repository that has the sane name)_

Of course, triggering a GitHub Action in a given repository must not be something that anyone can do,
as it would be annoying to have such Actions triggered randomly by 3rd-party people or scripts - and even more annoying, 
running an Action can leak sensitive information :grimacing:

Which is why **the emitter of a `repository_dispatch` event have to authenticate itself**.  
GitHub's [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github#authenticating-with-the-api) are a way to do this.

### Generating a GitHub Personal Access Token

Unfortunately, it seems that Personal Access Tokens have quite a poor granularity: 
the emitter of a `repository_dispatch` event must use a token with the `repo` [scope](https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes),
which gives it _"full access to repositories, including private repositories"_ :warning:

!!! note
    I thought I could create such a Token that would be limited to my GitHub profile repository, but it seems
    that Personal Access Tokens don't have such a level of granularity, so I do have to give
    such a "god-like" access to my `devblog` repository :pensive:

The steps to generate such a token are documented here:

 - https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

### Storing the Token on the event emitter's side

This Token having such great power, I should store it in a safe place...  
It seems that GitHub Actions' _Encrypted Secrets_ is what I need! :slight_smile:

 - https://docs.github.com/en/actions/security-guides/encrypted-secrets

### Sending the `repository_dispatch` event when this DevBlog is updated

Right, now I have a (overpowered :zap:) Token, and it's safely stored in the `devblog` repository as an Encrypted Secret...  
Now all I have to do is to use it to send such an event to the repo that hosts my GitHub profile!

There are multiple ways to do this, and I went for the one that was looking the most straightforward to me.  
So at the end of the GitHub Action file that deploys the blog generated by 
[Material for MKDocs](https://squidfunk.github.io/mkdocs-material/) when I push an update to the git repo,
I just added the following [step](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idsteps):
``` yaml
- name: Notify my Github profile repo
  env:
    TOKEN: ${{ secrets.MY_TOKEN_SECRET_NAME }} # (1)
  run:  # (2) |-
    curl \
      --silent \
      -X POST \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: token ${TOKEN}" \
      "https://api.github.com/repos/olivierphi/olivierphi/dispatches" \ 
      -d '{"event_type":"devblog-gh-pages-pushed","client_payload":{"wait_for_deployment":true}}'
```

1. We ask GitHub to extract the encrypted secret to an environment variable that I name "TOKEN"
2. The target URL includes `olivierphi/olivierphi`: the first one is the name of my GitHub profile, while the second
    one is the name of the GitHub repository.  
    They have to be identical in the case of the GitHub profile.

I copy-pasted this `curl` command from there:

 - https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event

### Receiving the `repository_dispatch` event on the GitHub profile repo

I already have a GitHub Action file that is in charge of re-building dynamically
the content of my GitHUb profile's README when I push some content.

All I have to do now is to remove the hourly build, and subscribe to the `repository_dispatch` event:
``` {.yaml hl_lines="6-7 10-12"}
on:
  push:
  workflow_dispatch: # (1)
  
  # This is removed:
  schedule:
    - cron:  '33 * * * *' # rebuilt once an hour at xx:33
    
  # This is added:
  repository_dispatch:
    # triggered by my "devblog" repo when something is pushed on the GH Pages branch
    types: [devblog-gh-pages-pushed] 
```

1. Thanks to this `workflow_dispatch` we can also 
    [manually trigger the GitHub Action](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow). 

### Conditionally waiting for the DevBlog's deployment

There is one last thing I have to manage: at the time when this GitHub Action is triggered,
the DevBlog's static content was just pushed to the `gh-pages` branch by MKDocs, 
so **the updated DevBlog is not online yet**!

So just doing this is not enough, and we need to wait for the RSS feed to be up-to-date before
re-generating the README of the GitHub profile... :clock:

It seems that most of the time this deployment takes about 30 to 40 seconds, but sometimes it took a little more than
a minute; right, **let's wait for 90 seconds** before reading the RSS feed, and it should do the job. :fingers_crossed:

However, I don't want to have this waiting time when I push an updated version of the README file itself,
or when I trigger the GitHub Action manually!

15 browser tabs opened on the GH Actions documentation later, I found a solution :sweat_smile:

``` {.yaml hl_lines="1-5"}
- name: Wait for devblog deployment on GitHub Pages
  if: ${{ github.event_name == 'repository_dispatch' && github.event.client_payload.wait_for_deployment }}
  run: |-
    echo "Deployment can take up to 1 minute, let's wait for 90 seconds"
    sleep 90
- name: Update README
  run: |-
    python build_readme.py
    cat README.md
```

So the Action will [sleep](https://man7.org/linux/man-pages/man3/sleep.3.html) for 90 seconds **before** running
the Python script that fetches the blog's content and update the README accordingly, but **only if**:

 - The Action was triggered by a "repository_dispatch" event.  
    We can detect this with:  
    `github.event_name == 'repository_dispatch'`
 - The emitter sent a parameter - that I arbitrarily called `wait_for_deployment` - in its JSON payload, with a _truthy_ value
   (which is what I did in the `curl` command earlier :point_up:).  
    We can detect this with:  
    `github.event.client_payload.wait_for_deployment`

## Job's done! :v:

Now when I push to this DevBlog repo it sends a `repository_dispatch` event to the repository of my GitHub profile,
which will trigger the generation of the README after having waited a bit to let some time for the up-to-date RSS feed
to be online :slight_smile:

In the end, all this happens between these 2 YAML files:

 - https://github.com/olivierphi/olivierphi/blob/main/.github/workflows/build.yml
 - https://github.com/olivierphi/devblog/blob/main/.github/workflows/ci.yml

*[TIL]: Today I Learned
