---
title: "'From scratch to online in production' in a single day, with Django - Part 2"
date: "2022-07-22"
categories:
  - "webdev"
tags:
  - "django"
  - "project layout"
---

# _'From scratch to online in production'_ in a single day, with Django - Part 2

## Quick summary of the previous part

In [part 1](/2022/07-19---from-scratch-to-online-in-production-in-a-single-day-with-django-part-1) we saw
a way to set up a Django project in a quite generic way, that can be used for _any_ kind of project:

 - Dependencies are managed by [Poetry](https://python-poetry.org/)
 - Settings that differ from an environment to another come from environment variables, and are populated from
      optional `.env` files in "local development" mode, powered by [django-environ](https://django-environ.readthedocs.io/en/latest/).  
      ``` python
      SECRET_KEY = env.str("SECRET_KEY")
   
      DATABASES = {
          "default": env.db_url("DATABASE_URL"),
      }
      ```
      On top of this we also have a Python module for each type of environment - so we'll use 
      the [DJANGO_SETTINGS_MODULE](https://docs.djangoproject.com/en/4.0/topics/settings/#designating-the-settings) environment variable 
      to point to `project.settings.development` during  local development , `project.settings.heroku` on Heroku, 
      `project.settings.test` when running our test suite, etc.

!!! info
    Having such multiple settings files is a best practice I learned by reading
    the great book _[Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)_ - which itself 
    cites [this talk](https://www.slideshare.net/jacobian/the-best-and-worst-of-django) from  Jacob Kaplan-Moss.
      
 - A `src/` folder contains all the application code, within 2 top-level packages for our Python modules:
     * `project`, which contains the Django settings and the WSGI/ASGI HTTP entrypoints
     * `apps` for the Django apps - so each of them is free to have any name we want, without any risks of collisions
    with an existing 3rd-party package.

## Next step: we have to organise the business logic inside our Django apps

Django has some built-in recommendations about how to structure a project.  
Its [applications](https://docs.djangoproject.com/en/4.0/ref/applications/) concept for example is a good start to split the code into smaller units, 
and some basic rules like this one are good guidelines:

!!! quote
    If there are 20+ models in a single app, think about ways to break it down into smaller apps,
    as it probably means your app is doing too much.  
    In practice, we like to lower this number to **no more than five to ten models per app**.
    
    From _[Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)_


Now, let's take a look at an aspect that is probably a mystery for every new developer who enter a new ecosystem they're not
familiar with yet - like me a few years ago when I switched from _"PHP + Symfony :elephant:"_ to _"Python + Django :snake:"_ : 
> How to organise the business logic **inside** each Django app?

## An efficient pattern for the business logic: simplicity that scales well :ok_hand:

When I started to learn Django I was lucky enough to stumble upon this [Django Styleguide](https://github.com/HackSoftware/Django-Styleguide),
published on GitHub by the software development company HackSoft.  
And more specifically this part, where they explain "services" and "selectors":

 - https://github.com/HackSoftware/Django-Styleguide#services

#### My own adaptation of the "services" and "selectors" concept from HackSoft

As I'm mostly working with [GraphQL](https://graphql.org/) in my day-to-day job, I opted for a terminology that rings a bell a bit more to my hears 
than _"services"_ and _"selectors"_: `mutations` and `queries`.  
The former is a package that contains code that _alter_ a database (adding, modifying or deleting data from it), while the
latter is specialised in _fetching_ data.

Here is how it looks like applied to my "Gin Rummy leaderboard" mini project:  
_(the parts of the tree that don't matter in this case are replaced with three dots)_
``` bash
gin-scoring/
├── src/                                                                                                                                                                                                   
│     ├── apps/                                                                                                                                                                                              
│     │     ├── authentication/                                                                                                                                                                                
│     │     │     └── ...                                                                                                                                                                              
│     │     ├── gin_scoring/                                                                                                                                                                                   
│     │     │     ├── domain/                                                                                                                                                                                    
│     │     │     │     ├── commands/ # (1)
│     │     │     │     │     ├── __init__.py
│     │     │     │     │     └── _save_game_result.py
│     │     │     │     ├── queries/ # (2)
│     │     │     │     │     ├── __init__.py
│     │     │     │     │     ├── _hall_of_fame_monthly.py
│     │     │     │     │     ├── _hall_of_fame.py
│     │     │     │     │     └── _last_game_results.py
│     │     │     │     └── gin_rummy.py
│     │     │     ├── jinja2/
│     │     │     │     └── ...
│     │     │     ├── migrations/
│     │     │     │     └── ...
│     │     │     ├── admin.py
│     │     │     ├── apps.py
│     │     │     ├── helpers.py
│     │     │     ├── http_payloads.py
│     │     │     ├── models.py
│     │     │     ├── urls.py
│     │     │     └── views.py
│     │     └── __init__.py
│     ├── project/
│     │     ├── settings/
│     │     │     └── ...
│     │     ├── asgi.py # (3)
│     │     ├── jinja2.py
│     │     ├── urls.py
│     │     └── wsgi.py
│     └── manage.py*
├── tests/
│     └── ...
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── poetry.lock
└── pyproject.toml
```

1. In this package we have the code that _alters_ data
2. In this package we have the code that _fetches_ data
3. `asgi.py`, `urls.py` and `wsgi.py` were created by the [startproject](https://docs.djangoproject.com/en/4.0/ref/django-admin/#startproject)
    command.  
    `jinja2.py` is where I quickly configure Jinja, following the Django documentation:  
    > https://docs.djangoproject.com/en/4.0/topics/templates/#django.template.backends.jinja2.Jinja2

We can see that for each Django app we have 2 sub-packages:

 - `domain.mutations` is where the code that _alter_ data lives
 - `domain.queries` is where the code that _fetch_ data lives

They're both structured the same way, following these principles from HackSoft's styleguide:

 - Each of their module **exposes only one public function** - and optionally some types if it has to,
    in order to describe the shape of its input and/or output.
 - Each of these one-per-module-functions only accepts keyword arguments.
 - These functions' signatures should be fully "type hinted".
 - Each module is free to use as many private functions it needs to achieve the job described by its single
    public function.
 - For the mutations, these functions' name should start with _a verb_, since they're the reflection of a business logic _action_
 - Each module's name is prefixed with an underscore, to emphasise that it should not be imported directly
 - The `__init__.py` file is in charge of exposing the public function of each module to the "outside world" - i.e. the Python
    code that doesn't live in the same package.

!!! info 
    The goal of the last 2 points is to avoid this kind of imports, where we have to repeat
    the same name twice - once of the module name and once for the function itself:
    ``` python
    from .domain.mutations.save_game_result import save_game_result
    ```
    So instead of this repetition we can simply do:
    ``` python
    from .domain.mutations import save_game_result
    ```

## A concrete example, with the Gin Rummy leaderboard app

#### The `domain.mutations` package of our Django app

For this minimalist project we need only one mutation, which is triggered when the user
submits the "New game result" HTML form:
``` python
# file: src/apps/gin_scoring/domain/_save_game_result.py
from ...domain.gin_rummy import GAME_OUTCOME, calculate_round_score
from ...models import GameResult


def save_game_result(
    *, # (1)
    player_north_name: str,
    player_south_name: str,
    outcome: GAME_OUTCOME, # (2)
    winner_name: str | None,
    deadwood_value: int,
) -> GameResult:
    is_draw = outcome == "draw"

    winner_score = None
    if is_draw:
        winner_name = None
    else:
        winner_score = calculate_round_score(game_outcome=outcome, deadwood_value=deadwood_value)

    game_result_model = GameResult(
        player_north_name=player_north_name,
        player_south_name=player_south_name,
        outcome=outcome,
        winner_name=winner_name,
        deadwood_value=deadwood_value,
        winner_score=winner_score,
    ) # (3)
    game_result_model.save()

    return game_result_model

```

1. We force this function to be used only with the "keyword arguments" syntax
2. `GAME_OUTCOME` is just a literal type:
   ``` python
   GAME_OUTCOME = t.Literal["knock", "gin", "big_gin", "undercut", "draw"]
   ``` 
3. The model also has a `created_at` field, but it will automatically be set by the Django ORM.  
    This model looks like this: 
   ``` python
   class GameResult(models.Model):
       player_north_name = models.CharField(max_length=50)
       player_south_name = models.CharField(max_length=50)
       outcome = models.CharField(max_length=10, choices=[(end_type, end_type) for end_type in GAME_OUTCOME.__args__])  # type: ignore
       # These 2 ones can be `null` when the outcome is `draw`:
       winner_name = models.CharField(max_length=50, null=True)
       deadwood_value = models.PositiveSmallIntegerField(null=True)
       # Computed from the previous `end_type` and `deadwood_value` fields:
       winner_score = models.PositiveSmallIntegerField(null=True)
       
       created_at = models.DateTimeField(default=timezone.now)
       
       @property
       def is_draw(self) -> bool:
           return self.outcome == "draw"
       
       @cached_property
       def loser_name(self) -> str:
           return [name for name in (self.player_north_name, self.player_south_name) if name != self.winner_name][0]
       
       def __str__(self) -> str:
           return f"{self.player_north_name.title()} vs {self.player_south_name.title()}, on {self.created_at.strftime('%a %d %b at %H:%M')}"
   ``` 

And then, we expose that function to the rest of the Python code:
``` python
# file: src/apps/gin_scoring/domain/__init__.py
from ._save_game_result import save_game_result
``` 

We use it like this in the Django view:
``` python
# file: src/apps/gin_scoring/views.py
@require_POST
def post_game_result(request: HttpRequest) -> HttpResponse:
    try:
        game_result_payload = GameResultPayload(**request.POST.dict())
    except pydantic.ValidationError:
        return HttpResponseBadRequest()

    commands.save_game_result(
        player_north_name=game_result_payload.player_north_name,
        player_south_name=game_result_payload.player_south_name,
        outcome=game_result_payload.outcome,
        winner_name=game_result_payload.winner_name,
        deadwood_value=game_result_payload.deadwood_value,
    )

    return redirect("index")
``` 

!!! note "Validating the input of our Django views"
    There are multiple ways to **validate** and **normalise** the input of our Django views, before
    passing its data to the "domain" layer.  
    In this case I chose to use [Pydantic](https://pydantic-docs.helpmanual.io/).
    ``` python
    # file: src/apps/gin_scoring/http_payloads.py
    from typing import Any
    
    import pydantic
    
    from .domain.gin_rummy import GAME_OUTCOME
    from .helpers import normalize_player_name
    
    
    class GameResultPayload(pydantic.BaseModel):
        player_north_name: str
        player_south_name: str
        outcome: GAME_OUTCOME
        winner_name: str | None
        deadwood_value: int
    
        @property
        def is_draw(self) -> bool:
            return self.outcome == "draw"
    
        @pydantic.root_validator(pre=True)
        def normalize_player_names(cls, values: dict[str, Any]):
            # In order to have consistent recording when players "Alice" and "Bob" add a game result, whether
            # "Alice" is "north" and "Bob" is "south" or vice-versa, we sort their names alphabetically
            # and then always set the "north" player to the first one and the "south" one to the second one:
            player_north_name, player_south_name = tuple(
                sorted(
                    (
                        normalize_player_name(values["player_north_name"]),
                        normalize_player_name(values["player_south_name"]),
                    )
                )
            )
            values["player_north_name"] = player_north_name
            values["player_south_name"] = player_south_name
            if values["winner_name"]:
                values["winner_name"] = normalize_player_name(values["winner_name"])
            return values
    
        @pydantic.validator("winner_name")
        def validate_winner_name(cls, v: str, values: dict[str, Any]) -> str | None:
            is_draw = values["outcome"] == "draw"
            if is_draw:
                # No winner name for "draw" games:
                v = None  # type: ignore
            if not is_draw:
                if not v:
                    raise ValueError(f"non-draw games must have a winner name")
                player_names = (values["player_north_name"], values["player_south_name"])
                if v not in player_names:
                    raise ValueError(f"winner name {v} is not part of the players' names '{','.join(player_names)}'")
    
            return normalize_player_name(v) if v else None

    ``` 


#### The `domain.queries` package of our Django app

For this simple app we need only 3 queries:

 - One to get the _global_ "Hall of fame", where we determine the ranking of players
    based on _all_ the games played so far
 - One to get the _monthly_ "Hall of fame", which does the same but with a distinct ranking
    _for each month_
 - One that returns exhaustive data for the last 10 games that were played

Let's take a look at the second one, for example:
``` python
# file: src/apps/gin_scoring/queries/_hall_of_fame_monthly.py
from datetime import datetime
from typing import NamedTuple

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

from ...models import GameResult  # (1)


class HallOfFameMonthResult(NamedTuple): # (2)
    month: datetime
    winner_name: str
    game_counts: int
    win_counts: int
    score_delta: int


def hall_of_fame_monthly() -> list[HallOfFameMonthResult]:
    # @link https://docs.djangoproject.com/en/4.0/topics/db/aggregation/
    win_counts = Count("winner_score")
    total_score = Sum("winner_score")

    raw_results = (
        GameResult.objects.filter(winner_name__isnull=False)
        .annotate(month=TruncMonth("created_at")) # (3)
        .values("month", "winner_name")
        .distinct()
        .annotate(win_counts=win_counts, total_score=total_score)
        # Each won round is worth 25 points:
        .annotate(grand_total=(win_counts * 25) + total_score)
        .order_by("-month", "-grand_total")
    )
    raw_results_per_month = {}
    for raw_result in raw_results: # (4)
        raw_results_per_month.setdefault(raw_result["month"], []).append(raw_result)

    returned_results: list[HallOfFameMonthResult] = []
    for month, month_results in raw_results_per_month.items():
        winner_result = month_results[0]
        winner_grand_total = winner_result["grand_total"] or 0
        second_best_grand_total = 0 if len(month_results) < 2 else (month_results[1]["grand_total"] or 0)
        games_count = sum([res["win_counts"] for res in month_results])

        returned_results.append(
            HallOfFameMonthResult(
                month=month,
                winner_name=winner_result["winner_name"],
                game_counts=games_count,
                win_counts=winner_result["win_counts"],
                score_delta=winner_grand_total - second_best_grand_total,
            )
        )

    return returned_results

```
 
1. I like using _relative_ imports for things we import _that live in the same Django app_.  
    In all other cases I'd use _absolute_ imports. 
2. We're not returning ActiveRecord items directly from a Django QuerySet there,
    but aggregated results.  
    There are several data structures we can use in Python for that
    kind of "value objects", but I generally opt for [typing.NamedTuple](https://docs.python.org/3/library/typing.html#typing.NamedTuple)
3. This is where we group the database rows by month
4. Yes, I could probably have used [itertools.groupby](https://docs.python.org/3/library/itertools.html#itertools.groupby) instead ^_^

!!! note
    Note that we could have split this into several functions - in which case
    they would all be private functions (their name would start with an underscore),
    and only the "domain" one would be public :slight_smile:

Probably not the very best way to achieve this... but this is a project I gave myself one single day to build
so that will do the job :smile:

And similarly, the `__init__.py` file is in charge of exposing only what the rest of the Python
``` python
from ._hall_of_fame import hall_of_fame
from ._hall_of_fame_monthly import (
    HallOfFameMonthResult, # (1)
    hall_of_fame_monthly
) 
from ._last_game_results import last_game_results # (2)
```

1. Sometimes it's useful to not only export the one public function of the module,
    but also a dedicated type it's using for its input or output - so other Python modules
    can also use type hints when interacting with the "domain" layer
2. But most of the time, all we need is to expose the public function of the module :smile:

## And that's it! :slight_smile:

As we can see the pattern is very simple to implement, and its few principles are a very good guideline
for developers when they have to add some code.

 - **Is it code that creates, updates or deletes data in the database?**  
    :point_right: Let's create a new module in the `domain.mutations` package of the related Django app, 
    that will expose one single "kwargs-only" function - its name will start with a verb. 
 - **Is it code that reads data from the database?**  
    :point_right: Let's create a new module in the `domain.queries` package of the related Django app,
    that will expose one single "kwargs-only" function.

Its beauty is that it really scales very well: my team and I used it for years on ever-growing code bases without
ever reaching a limitation of it. :ok_hand:

The 3rd (and last) article of this series will be a quick one, about how I hosted this app - for free - at the
end of that single day.  
I might also share a bit about the "code quality" tools I've used.

## Acknowledgements

Thank you so much HackSoft for your [Django Styleguide](https://github.com/HackSoftware/Django-Styleguide#services)! :green_heart:

I would also like to thank Audrey and Daniel Roy Greenfeld for their book [Two Scoops Of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x),
which was a very helpful resource for me when I started to learn Django and tried to see what the best practices could be 
in this ecosystem - definitely worth the purchase! :slight_smile:
