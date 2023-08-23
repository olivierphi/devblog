---
title: "business_logic.py"
date: "2023-08-18"
categories:
  - "webdev"
tags:
  - "python"
  - "django"
---

# Implementing the business logic in a Django project

## The "startup project" way

In a previous post I explained how I usually manage business logic
in a [Django](https://www.djangoproject.com/) "startup" project, in an approximation
of the [CQS](https://en.wikipedia.org/wiki/Command%E2%80%93query_separation) design pattern:

- [How I manage business logic in a Django project](/2022/07-22---from-scratch-to-online-in-production-in-a-single-day-with-django-part-2/#next-step-we-have-to-organise-the-business-logic-inside-our-django-apps)
 
I still love this way of organising the code, and how it allows one to **fully focus on
writing and maintaining the code**, rather than wondering where to put this or that piece of code. :slight_smile:

!!! abstract "The importance of having a guideline to organise the code"
    When building a platform mostly made of **bespoke code tailored to implement the
    specific business logic of a "startup" project**, in my personal experience writing the business logic is what takes the most effort
    for the development team - especially when using a "batteries included" framework such as Django, Laravel, Symfony or Rails.  
    This is why having that sort of simple guidelines to organise that
    vast quantity of code and **avoid wasting time with "which code goes where" considerations** is crucial in my opinion. 

## The "CMS-driven" way

However, in the last few months I've been working for a digital agency, 
creators of the [Wagtail](https://wagtail.org/) CMS, and I realised that in such projects
the topics around business logic are quite different. 

When building a CMS-driven website, there is actually much less bespoke business logic to implement, since
the project is heavily based on content management.  
And its is the CMS, and all its built-in features dedicated to
content management workflow, permissions, notifications, etc, that really are the conductor of the project.

Some of the Django apps will still require custom business logic in such a project, but it's less often the case
than for a "startup" project.  
This is why I went for a simpler approach, where I put **all the business logic of each Django app
in a single Python module**.

### Naming things

As for the name of that module, I was going to opt for `domain`, but I thought back
of this article and decided to call it `business_logic` instead, as it's really a name
that leaves **no room for ambiguity** :slight_smile:  
!!! quote "David Winterbottom, _Why your models are fat_"
    Your web framework is not your boss.   
    As a rule-of-thumb, your application logic should live in modules that aren’t Django-specific modules 
    (eg not in `views.py`, `models.py` or `forms.py`).  
    If I had my way, Django would create an empty `business_logic.py` in each new app to encourage this.
     
    - https://codeinthehole.com/lists/why-your-models-are-fat/

### What that file looks like

Inside that file, I basically follow the same rules than in the CQS-inspired approach:

  - The only classes are ones that describe **data structures**, and they are immutable every time it is possible.  
    The classes I typically use or that are [typing.NamedTuple](https://docs.python.org/3/library/typing.html#typing.NamedTuple), 
    [dataclasses.dataclass](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) or 
    [typing.TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict).  
    Choosing one or another depends on the specific use case (`typing.NamedTuple` always being my own first choice 💚), 
    but they all pretty much address the same need anyhow :slight_smile:
  - The business logic is implemented in plain **functions**, and as soon as a function has more than one argument
     it must use the syntax that makes it a "kwargs-only" function.

In a nutshell, it looks like this:

```py
# business_logic.py

import enum
from datetime import datetime
from typing import NamedTuple, TypedDict

from django.core.files import File

from .models import Group


# --- Constants

EVENTBRITE_API_URL = "https://www.eventbriteapi.com/v3/"


# --- Types

class EventType(enum.IntEnum):
    CONFERENCE = 1
    QUICK_TALK = 2
    WORKSHOP = 3

    
class EventbriteNotificationParameters(NamedTuple):
    target_group: Group | None
    in_realtime: bool = False

    
class EventbriteAPIEventData(TypedDict):
    """
    Non-exhaustive description of the data 
    returned by the Eventbrite API.
    """
    id: str
    name: str
    description: str
    start: str
    end: str
    url: str
    logo: str

    
# --- Queries

def fetch_eventbrite_events_data(
    *,
    from_date: datetime | None = None,
    only_in_location: str | None = None,
) -> list[EventbriteAPIEventData]:
    ...
    

def fetch_eventbrite_event_data_by_id(event_id: str) -> EventbriteAPIEventData:
    ...


# --- Mutations

def create_eventbrite_event(
    *,
    name: str,
    description: str,
    start: datetime,
    end: datetime,
    logo: File,     
) -> EventbriteAPIEventData:
    ...


```

## Conclusion

By following this very simple rule, every Django app that needs custom business logic has 
its own `business_logic.py` file, at the same level than its `models.py` and `views.py` ones.

As always, it's better to start simple - some people even start their Django projects 
[with a single folder](https://noumenal.es/notes/django/single-folder-layout/) after all! :smile:  
The idea is the same here: start with a single file, and then adapt by splitting this file into a package
made of several modules **only** if the volume of code in that file makes it too tedious to work with. :slight_smile: 

*[CQS]: Command Query Separation
