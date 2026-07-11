## Dynamic windows and data-driven state

Tumbling and sliding windows are aligned to the clock — you know their boundaries
in advance. **Session windows** are different: their boundaries are **defined by
the data itself**. A session grows as long as events keep arriving within the gap,
and closes only after a quiet stretch. You can't know how long a session will be
until you've seen the silence that ends it.

That data-driven shape makes session windows the most *stateful* of the family,
and reveals a subtlety of how engines manage window state:

- Each new event may **extend** an open session, or two nearby sessions may need to
  **merge** when an event arrives that bridges them.
- The engine holds each open session's state until the gap elapses (bounded by the
  watermark), then finalizes and emits it.

Sessions are how you measure real human behavior — a browsing visit, an app usage
session, a support conversation — none of which respect a fixed clock. Web
analytics' "30-minute inactivity = new session" rule is exactly this. When your
unit of analysis is "a burst of related activity," the session window is the tool.

*Go deeper: session windows; session merging; gap-based state management.*
