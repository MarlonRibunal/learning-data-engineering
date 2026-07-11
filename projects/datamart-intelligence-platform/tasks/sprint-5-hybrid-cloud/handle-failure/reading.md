## Fail fast, fail loud

Raising when a remote job fails encodes a hard-won operational principle: **a
pipeline should fail fast and loud, not slow and silent.** The worst outcome
isn't a crash — it's a pipeline that *thinks* it succeeded and ships wrong data
downstream, where the error compounds invisibly until a stakeholder acts on it.

The ideas at play:

- **Error propagation.** A failure must travel *up* — a failed remote job becomes a
  raised exception becomes a failed Airflow task becomes a stopped DAG becomes an
  alert. Break that chain anywhere (swallow the exception, ignore the status) and
  the failure goes dark.
- **Fail-fast.** Stop at the first unrecoverable error rather than pressing on with
  bad inputs. Downstream tasks that depend on a failed one should *not* run — which
  is exactly what raising achieves in a DAG.
- **The poison pill.** One bad job that silently "succeeds" can corrupt every table
  built from it. Loud failure contains the blast radius.

There's a real tension with the *resilience* you built elsewhere (retries, circuit
breakers): retry the *transient*, fail-fast the *permanent*. Knowing which is which
is the judgment; the constant is that a genuine failure must never be hidden.

*Go deeper: fail-fast; error propagation; silent failures as the worst failures.*
