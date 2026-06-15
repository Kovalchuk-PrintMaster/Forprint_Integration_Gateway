# Gateway v0.6 Contract Deprecation Policy

A Gateway contract can be deprecated only after Blueprint approval.

Old fixtures must remain readable for compatibility checks until the Blueprint
explicitly retires them.

Compatibility gates catch breaking changes by rechecking accepted v0.3, v0.4 and
v0.5 concepts.

Modules should report incompatible contract versions through structured Gateway
compatibility states.

Breaking changes are not allowed silently.