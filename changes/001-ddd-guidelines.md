# 001 — DDD Guidelines

Created a CLAUDE.md file at the user's home directory to serve as a reusable DDD architecture template.
Defined the standard folder structure organised by Bounded Context rather than by technical layer.
Wrote a naming table covering every DDD concept: Entity, Value Object, Aggregate Root, Domain Service, Repository, Command, Query, Domain Event, DTO, and Exception.
Documented layer rules: domain has zero framework dependencies, application holds no business logic, infrastructure depends on domain not the reverse, presentation is the only layer that knows about HTTP.
Added a pre-flight checklist for Claude to run before proposing or writing any code.
