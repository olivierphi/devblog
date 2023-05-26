---
title: "TIL: Hashing data in the form of a UUID"
date: "2023-05-17"
categories:
  - "webdev"
tags:
  - "til"
  - "python"
---

# TIL: Hashing data in the form of a UUID

A quick trick I learned today as I was working on a codebase related to the awesome [Wagtail](https://wagtail.org/) CMS.

When we need to get a unique digest of some data - that will be the same over time if we apply the same
function to the same data later on, while hiding what the original data was - we usually look at 
the [classic hash functions](https://en.wikipedia.org/wiki/List_of_hash_functions) such as SHA-1, HMAC and such...

However, it turns out that we can also use UUIDs for such a purpose - which gives us a piece of data that is both a digest and an UUID, which
can be quite handy! :slight_smile:

The original trick is there, in the Wagtail code:  
_(note that it might be a trick that I was aware of but that that is commonly used elsewhere, of course)_  

 * https://github.com/wagtail/wagtail/blob/85c9b66/wagtail/models/reference_index.py#L388-L404


## Quick check

We can check that in a quick Python shell:
```py
import uuid

# Generated previously with `uuid.uuid4()`
# --> we can now hard-code it in our code to get consistent hashes from here:
hash_base_uuid = uuid.UUID("e1fb6cc4-4843-4433-91a7-f7639640cb8d")

# Let's create some dummy data we want to create hashes for:
data_to_hash_1, data_to_hash_2 = "little bobby", "tables"

hash_1_round_1 = uuid.uuid5(hash_base_uuid, data_to_hash_1)
# --> hashing "little bobby" with this base UUID will *always* 
# gives us `UUID('218fde61-5b70-5a33-9e0a-daa7f2a7c388')`

# Hashing the same data again:
hash_1_round_2 = uuid.uuid5(hash_base_uuid, data_to_hash_1) 

# Hashing the same data does give us the same digest-as-a-UUID:  ✅
assert hash_1_round_1 == hash_1_round_2

# Now hashing another bit of data
hash_2_round_1 = uuid.uuid5(hash_base_uuid, data_to_hash_2) 
# --> hashing "tables" with this base UUID will *always* 
# gives us `UUID('189a5a73-6e52-5885-ba68-8432f5632e2d')`

# Hashing different data does give us different digests-as-a-UUID:  ✅
assert hash_1_round_1 != hash_2_round_1
```


## Potential vulnerability

According to the Python documentation of the [uuid](https://docs.python.org/3/library/uuid.html#uuid.uuid5) module, 
it's a SHA-1 hash that will be used behind the scenes.  
This is way better than the other algorithm that can also be used according to
[RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122.html#section-4.3),
which is the much weaker MD5.  

However, SHA-1 seems to be potentially vulnerable to some attacks nowadays,   
so I reckon it might not be something to use when the hashed data 
is susceptible to be attacked by brute-force? (user passwords, etc.)

 * https://en.wikipedia.org/wiki/SHA-1#Attacks


*[TIL]: Today I Learned
*[CMS]: Content Management System
