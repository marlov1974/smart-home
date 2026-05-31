# P0033 attempts

## Attempt 1

Status: completed

Plan:

1. Bootstrap and consistency review.
2. Implement P0033 feature DB builder.
3. Build local generated feature DB.
4. Run package tests and validation.
5. Update evidence, docs, commit and push.

Result:

- Review/design/function design completed.
- Initial real build returned `unable to open database file` inside sandbox; reran with approved local feature-DB write permission.
- One build attempt reported `database weather_source is locked` during source detachment; implementation was adjusted to avoid explicit detach during the short-lived build connection.
- Full real build then completed successfully with 34944 rows.
- M1 was corrected to use Python ISO week rather than SQLite `%W`; M1/M2 bucket normal calculation was optimized and the feature DB was rebuilt successfully.
- Added M1/M2 `bucket_year_count` diagnostics and rebuilt the feature DB as schema version 2. Local M1/M2 buckets aggregate across at least 4 years.
- Validation and diagnostics passed.

Knowhow promotion: skipped. The SQLite detach behavior and bucket precomputation fix are package-local implementation details, not a durable cross-package rule.
