**Schema migration.** An upstream team renamed columns and added a field —
without asking. Your pipeline breaks, or worse, keeps running on the wrong
columns. Migrations are among the riskiest things a data engineer does, because
a mistake silently corrupts data that downstream teams trust. The craft is doing
it **safely**: map the old shape to the new, backfill missing values sensibly,
and *reconcile* before and after so you can prove nothing was lost.

This track walks one migration end to end — reshape, backfill, verify — the
same three moves whether you're renaming a column or re-platforming a warehouse.
