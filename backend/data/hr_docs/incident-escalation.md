# Incident Response and Escalation Policy

**Owner:** Engineering, in coordination with Security and Customer Support
**Effective date:** 2026-01-01
**Applies to:** All Lumina production and customer-facing systems.

This document defines how incidents are detected, classified,
escalated, and reviewed at Lumina. It applies to availability,
performance, and security incidents.

## 1. Incident severity levels

| Severity | Definition | Initial response SLA |
|---|---|---|
| **P0** | Complete outage of a customer-facing service, or confirmed data breach. | **15 minutes** |
| **P1** | Major degradation affecting many customers or a critical internal system. | **30 minutes** |
| **P2** | Partial degradation, single-tenant outage, or workaround available. | **2 hours** |
| **P3** | Minor bug, cosmetic, or impacting an internal tool. | **1 business day** |
| **P4** | Tracked issue with no customer impact. | Best effort |

Severity is set by the incident commander and may be revised as the
situation evolves.

## 2. How to declare an incident

Anyone at Lumina can declare an incident. To declare one:

1. Post in the `#incidents` channel using the template:
   `/incident declare severity=<P0|P1|P2|P3> summary="..."`.
2. The on-call engineer for the affected service automatically
   receives a page.
3. The first responder becomes the **incident commander (IC)** until
   formally handed off.

Do not wait for "certainty" before declaring. It is always cheaper to
downgrade or close an incident than to discover one late.

## 3. On-call rotation

- Each engineering team owns a 24/7 on-call rotation for its
  services. Rotations are weekly and visible in the on-call tool.
- The on-call engineer is paged on any P0 or P1 alert.
- A secondary on-call is paged if the primary does not acknowledge
  within **5 minutes**.
- Manager-on-call is paged automatically for any P0 lasting longer
  than 30 minutes.

## 4. Escalation path

Escalation is intended for unblocking, not for blame. Escalate when:

- The incident commander needs additional expertise.
- Customer impact is broader than initially scoped.
- The incident has been open longer than the response SLA.

Escalation order for engineering incidents:

1. Service-team on-call engineer.
2. Service-team manager-on-call.
3. Director of Engineering.
4. VP of Engineering.

For security incidents, the path is:

1. Security on-call.
2. Head of Security.
3. CISO and Legal.

For customer-trust incidents (e.g., visible data error), the IC
notifies Customer Support leadership in parallel.

## 5. Customer communication

For any P0 or P1 incident:

- Update the public status page within **15 minutes** of the
  incident being declared.
- Refresh the status page at least every **30 minutes** until
  resolution.
- After resolution, post a written incident summary on the status
  page within 24 hours.

The IC owns status-page updates. Customer Support is notified via the
`#cs-incidents` channel and may take the comms lead for prolonged
outages.

## 6. After-action review

Every P0 and P1 incident requires a written post-incident review
("retrospective" or "RCA") within **5 working days** of resolution.

The review must include:

- Timeline (detection → mitigation → resolution).
- Customer impact in concrete terms.
- Root cause(s), distinguishing technical, process, and contributing
  factors.
- Action items with owners and due dates.

Reviews are blameless. The goal is system improvement, not
attribution to individuals.

## 7. Severe security incidents

Suspected breaches of customer data, credential exposure, or
malicious access trigger the **Security Incident Response Plan**:

- The IC role passes to Security on-call immediately.
- Legal and the CISO are notified within 1 hour.
- Affected customers are notified within the timelines required by
  applicable regulations and the customer contract, never later than
  72 hours after confirmation.

## 8. Practice and readiness

- Each team runs an incident response drill at least once per
  quarter.
- New on-call engineers shadow at least one incident before going
  primary.
- Runbooks are reviewed annually or after any incident that exposes
  a gap.
