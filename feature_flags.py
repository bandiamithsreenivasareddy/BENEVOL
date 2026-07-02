"""
DAANLOOP Feature Toggle System
==============================
Toggle these flags to control which sprint features are active.

- ENABLE_SPRINT_1 = True  -> Core: Auth, Listings, Search
- ENABLE_SPRINT_2 = True  -> Advanced: Bookmarks, Ratings, Reports, Activity Logs, Admin
- ENABLE_SPRINT_3 = True  -> Analytics & REST API

NOTE: Sprint 2 depends on Sprint 1. Sprint 3 depends on Sprint 1 & 2.
      If you enable Sprint 2, Sprint 1 will be auto-enabled.
      If you enable Sprint 3, Sprint 1 & 2 will be auto-enabled.
"""

ENABLE_SPRINT_1 = True
ENABLE_SPRINT_2 = True
ENABLE_SPRINT_3 = True 


def resolve_flags():
    """Resolve dependencies between sprint flags."""
    s1, s2, s3 = ENABLE_SPRINT_1, ENABLE_SPRINT_2, ENABLE_SPRINT_3
    if s3:
        s2 = True
        s1 = True
    if s2:
        s1 = True
    return s1, s2, s3
