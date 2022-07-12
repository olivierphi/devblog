---
title: "Choosing a tech stack for my card game platform"
date: "2022-07-10"
categories:
  - "webdev"
tags:
  - "next.js"
  - "django"
  - "laravel"
  - "rails"
  - "golang"
hide:
  - footer
---

# Quick overview of the tech stacks I should choose from

Here are some of the technologies I have professional experience with, in no particular order.  
Let's check their pros and cons for this card game :material-cards-playing: platform project I want to start building...

Note that these bullets points are strictly subjective and personal - I think that all these stacks are perfectly good
and valid, and choosing one or another is always a good option anyhow! :slight_smile:

### Next.js

* Pros :white_check_mark:
    - Modern, evolving at a quick pace, tons of best practices built-in. Very well documented.
    - I love TypeScript, I like React :slightly_smiling_face:
    - Now that it's rather mainstream there is a huge ecosystem for it
    - One language (TypeScript) to rule them all!
    - With new runtime such as Cloudflare Workers, Deno and Bun coming in,
      and all converging towards the use of standard Web APIs, it's a quite exciting time for JavaScript 
      on the backend!
    
* Cons :negative_squared_cross_mark:
    - Even though it can be used a fullstack framework
      _(as Theo, from ping.gg fame, explains [here](https://youtu.be/2cB5Fh46Vi4))_,
      and despite the numerous benefits of Node.js...  
      I can't help thinking that Node.js doesn't give me the same level of productivity than what I can have by
      using a "fully featured" mature backend framework such as Rails, Laravel or Django -
      where all the core features such as a typical backend, like an ORM, database migrations, logging, etc, are
      features that are already plugged together out of the box :electric_plug:
    - I gave a quick shot at [Prisma](https://www.prisma.io/), the trendy Node.js ORM; even though it has some undeniable
      qualities I didn't really fall in love with it - for various reasons.
  
### Laravel

* Pros :white_check_mark:
    - Probably the framework that comes with the highest number of features built-in.  
      Asynchronous jobs, websockets, authentication, support of Vite.js, you name it... Laravel has it by default. :slight_smile:
    - Easy deployment: whether it's via Forge or Vapor, Laravel comes with charged-but-very-handy solutions
      for deployment.

* Cons :negative_squared_cross_mark:
    - PHP has been my main programming language for backend stuff for more than 15 years,
      and even though it's never been better than today I grew a bit tired of its `$peculiarities` :sweat_smile:

### Ruby On Rails

* Pros :white_check_mark:
    - Almost as _"all features built-in"_ as Laravel
    - Huge and mature ecosystem
    - Ruby is a very expressive language

* Cons :negative_squared_cross_mark:
    - After having worked with languages that have inlined type annotations during the last
      few years, I struggle with languages like Ruby which don't have this
    - So much magic that it can be really hard sometimes to trace what method comes from where and
      really understand what's going on :sweat_smile:

### Django

* Pros :white_check_mark:
    - Python :snake: :green_heart:
    - My favourite ORM, with (for me) the right balance between power and pragmatism.  
      Also comes with great support for modern database features, such as JSON operators.
    - It's been my tech stack for the last 4 years, so I'm pretty productive with it :zap: :slight_smile:
    - Has excellent GraphQL libraries (and I love GraphQL! ^_^)
    - The Django Admin website is a huge gain of time while prototyping stuff

* Cons :negative_squared_cross_mark:
    - Some old-school aspects :older_adult:  
      (no routing via HTTP verbs for example - which can be solved by using
      Django REST Framework, but for some reason I've never really liked it :person_shrugging:)
    - Features such as websockets and asynchronous jobs are not built-in, but Django's ecosystem
      is vast enough to be able to add them with a good integrations 
      ([Channels](https://channels.readthedocs.io/en/stable/) for the former and
      [Dramatiq](https://dramatiq.io/) for the latter)

### Go

* Pros :white_check_mark:
    - I love the minimalism of the language :blue_heart:
    - Very stable over time
    - Strongly typed, with a very smart compiler
    - It's really nice to work with a programming language that have features such as
      code formatting or testing built-in :slight_smile: 
    
* Cons :negative_squared_cross_mark:
    - Whether it's at the database or the GraphQL layer, `null` values have to be handled
      and I'm not a big fans of the solutions Go has to offer for that
      (`sql.NullString` and friends, or pointers to primitive values) 
    - Can be _really_ verbose sometimes :sweat_smile:
