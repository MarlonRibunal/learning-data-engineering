## PII, masking, and privacy by design

Some columns are radioactive: names, emails, SSNs, card numbers — **PII**
(Personally Identifiable Information). Mishandling it isn't just embarrassing;
it's illegal under **GDPR, CCPA, HIPAA**, with real fines. The engineer's job is
to make sensitive data *usable for analysis without exposing the sensitive part*.

The toolkit:

- **Masking / redaction** — expose `a***@example.com` instead of the address.
- **Tokenization / pseudonymization** — replace the value with a reversible token,
  so joins still work but the raw value is vaulted.
- **Hashing** — one-way; good for matching/counting, useless for reading back.
- **A safe view** (this task) — a view exposing only non-sensitive columns, so the
  raw PII table can be locked down and analysts query the view.

The governing idea is **privacy by design**: minimize what you collect, restrict
who sees it, and default to *not* exposing PII rather than exposing it and hoping
no one looks. Data you never store can never leak — the cheapest security control
there is.

*Go deeper: GDPR/CCPA basics; masking vs. tokenization vs. hashing; data
minimization.*
