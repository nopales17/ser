# Phase 5A.4 transport-failure autopsy

This is an offline analysis of the immutable Phase 5A.4 records. It does not modify or rerun that experiment.

## Exact observed sequence

- The first **8** transport attempts completed in **48.047 seconds** and returned provider responses.
- They were followed by **37** curl code 28 failures, each lasting approximately **15.027 seconds**, the frozen connection timeout.
- One curl code 97 proxy-handshake failure followed, then **202** immediate curl code 7 connection failures.
- All **240** failed attempts had empty response bodies. No post-prefix provider or authentication error was recorded.

## Strongest supported cause

The long-lived SSH/SOCKS forwarding path stopped completing new connections and later ceased accepting local proxy connections.

Every request used a new curl process with no shared connection pool or curl session. Persistent HTTP connection reuse therefore cannot explain the cross-call transition. The only long-lived network component was the externally managed SSH SOCKS process.

## Evidentiary limit

The old records did not retain curl stderr, HTTP timing phases, per-attempt SSH process state, or per-attempt listener state. They therefore cannot distinguish remote SOCKS DNS failure, wiseau egress failure, or endpoint unavailability during the initial 37 timeouts, nor identify the exact instant the SSH process exited.
