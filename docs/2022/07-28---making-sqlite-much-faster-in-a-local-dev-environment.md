---
title: "Making SQLite much faster in a local dev environment"
date: "2022-07-28"
categories:
  - "webdev"
tags:
  - "TIL"
  - "django"
  - "sqlite"
---

# Making SQLite much faster in a local dev environment

!!! abstract
    TIL: it is possible to make SQLite data insertions 3 times faster :rocket: in a "local development" environment - 
    where data integrity is not a crucial criteria.

## Inserting data in a SQLite database can be quite slow

A Quick "TIL" this time... :slight_smile:

Contrary to my "Postgres" habits, for one of my side projects I'm using SQLite quite heavily.

Everything works fine, except that... Data insertions  are **very slow** :snail:

I suspected it could be caused by the extra work SQLite has to do to maintain data integrity,
and started to check if it was possible to tune the level of strictness we want for this.

## SQLite has a "journal mode", and it can be customised

That's how I found about the **journal mode** of SQLite:

 - https://www.sqlite.org/pragma.html#pragma_journal_mode

We can see on this documentation that it can be set to `DELETE`, `TRUNCATE`, `PERSIST`, `MEMORY`, `WAL` or `OFF`.

:star2: Right, let's try to change that!    
At the beginning of the Python function that processes my big batch of data to insert, I've added a SQL query that - given that I understand
that doc correctly - _should_ make my data insertions faster:
``` sql
pragma journal_mode = memory;
```

Let's launch my data insertion script with this update! :fingers_crossed:

**:point_right: Result**: nothing has changed, the insertion of my ≈2.000 rows still takes 50 seconds :pensive:

Ah, but maybe I need to send this query when the database connection is initiated, rather than on the
fly when I need it?

> **Note also that the journal_mode cannot be changed while a transaction is active.**
> 
> _The SQLite documentation_
 
## Setting the "journal mode" when the database connection is initialised

As I'm using Django for this side project, I had to find a way to send a SQL query as soon as possible to the database,
right after the connection is initialised.

According to [this (old) ticket](https://code.djangoproject.com/ticket/24018) on the Django bug tracker, which refers to
[that Stack Overflow thread](https://stackoverflow.com/a/6843199), a way to do this is to plug a custom function to
the signal that Django sends when the connection is initialised, and send the query there.

:star2: Alright, let's try this!  
I want to lower the data integrity work only on my "local dev" environment, so I'll have to add this code
to my `project.settings.development` module.  
_(explanations about this module [in this other post](https://devblog.dunsap.com/2022/07-19---from-scratch-to-online-in-production-in-a-single-day-with-django-part-1/#django-settings-management))_

``` {.python hl_lines="7-24"}
# file: src/project/settings/development.py

# My existing settings...
...
# ...to which I'm adding the following:

# Setting SQLite journal mode to 'memory' - much faster writes, 
# at the expense of database safety and integrity.
# @link https://www.sqlite.org/pragma.html#pragma_journal_mode
# @link https://code.djangoproject.com/ticket/24018#comment:4

from django.db.backends.signals import connection_created


def _disable_sqlite_journal(sender, connection, **kwargs):
    import logging

    if connection.vendor == "sqlite":
        logging.getLogger("apps").warning("Setting SQLite journal mode to 'memory'")
        cursor = connection.cursor()
        cursor.execute("PRAGMA journal_mode = memory;")


connection_created.connect(_disable_sqlite_journal) 
```

Let's launch my data insertion script again! :fingers_crossed:_(x2)_

**:point_right: Result**: the insertion of my ≈2.000 rows now takes **15 seconds, instead of 50**! :v:

## Closing notes

The trade-off is clear:

> The MEMORY journaling mode stores the rollback journal in volatile RAM.  
> This saves disk I/O but at the expense of database safety and integrity.  
> 
> If the application using SQLite crashes in the middle of a transaction when the MEMORY journaling mode is set, then the database file will very likely go corrupt.
> 
> _The SQLite documentation_

That's why in my case I want to customise this journal mode **only on my local environment**,
and won't do it in production.  
**But being able to opt in for 3 times faster data insertions is still a pretty good discovery**, 
as being able to iterate quickly is crucial when working on such a local environment! :slight_smile:

*[TIL]: Today I Learned
