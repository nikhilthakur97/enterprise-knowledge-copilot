# IT Security and Acceptable Use Policy

**Owner:** Security
**Effective date:** 2026-01-01
**Applies to:** All Lumina employees, contractors, and anyone with
access to Lumina systems or data.

This policy describes the minimum security requirements for using
Lumina systems and handling Lumina data. It is mandatory and is
audited.

## 1. Identity and authentication

- Single sign-on (SSO) is required for all Lumina applications that
  support it. Local accounts are not permitted on shared systems.
- **Multi-factor authentication (MFA)** is required for every Lumina
  account. Hardware security keys are issued on request and are the
  recommended second factor for engineering and finance roles.
- Passwords for Lumina accounts must be at least **14 characters**,
  unique to Lumina, and stored only in the company-approved password
  manager. Never reuse a personal password for a Lumina account.

## 2. Devices

- Only company-managed devices may access Lumina production
  systems, customer data, or source code.
- Personal devices ("BYOD") may be used for email, calendar, and
  chat through the company-managed mobile profile only.
- All devices must have full-disk encryption enabled and the
  company-managed endpoint agent installed.
- Devices must lock automatically after **5 minutes** of inactivity
  and require a password, fingerprint, or face unlock to resume.

## 3. Networks

- Use the corporate VPN whenever you access internal systems from
  outside a Lumina office. The VPN is required for production
  systems regardless of network.
- Public Wi-Fi (cafés, airports, hotels) is acceptable only with
  the VPN connected.
- Personal hotspots are preferred over untrusted public networks.

## 4. Data classification and handling

| Class | Examples | Handling |
|---|---|---|
| **Public** | Marketing pages, public docs. | No restrictions. |
| **Internal** | Project plans, internal wiki. | Lumina employees only. |
| **Confidential** | Customer data, financials, employee data. | Need-to-know; access reviewed quarterly. |
| **Restricted** | Production credentials, security incident data. | Access logged; explicit approval per use. |

Do not move data from a higher class to a lower one without an
approved process. In particular, do not paste customer data into
external chat tools, ticket descriptions, or AI assistants that have
not been reviewed by Security.

## 5. Acceptable use

You may use Lumina systems for incidental personal tasks (browsing,
personal email) within reason, provided that doing so:

- Does not interfere with your work.
- Does not access content prohibited by law or this Code.
- Does not consume excessive bandwidth or storage.

You should have **no expectation of privacy** on company-managed
devices and accounts. Lumina may inspect them, with notice where
practical, for security or legal reasons.

## 6. Reporting suspicious activity

Report any of the following immediately to
`security@lumina.example` or via the `#security-help` channel:

- Suspected phishing emails (use the "Report Phishing" button if
  available).
- A lost or stolen device.
- Unexpected MFA prompts you did not initiate.
- Any sign that an account, device, or system has been accessed
  without authorisation.

It is always better to report something benign than to ignore
something real. Lumina explicitly does not punish employees for
reporting in good faith, even if the report turns out to be a false
positive.

## 7. Credentials and secrets

- Never share a password or MFA code with anyone, including IT.
  Lumina IT will never ask you for either.
- Production credentials, API keys, and tokens must be stored only
  in the company secret manager. Never commit them to source
  control. Pre-commit hooks scan for known secret patterns.
- Suspected leaked credentials must be rotated within **24 hours**
  of discovery. Security can assist with the rotation.

## 8. Software installation

- Use the company-approved software portal whenever possible.
- Other software requires a security review. Open-source libraries
  used in production must be tracked in the software bill of
  materials (SBOM).

## 9. Departing employees

On the last day of employment:

- All access is revoked at end of business.
- Devices are returned and wiped.
- Outstanding access from third parties is terminated by IT.

## 10. Annual training

All employees complete the Information Security training annually.
Failure to complete the training within 30 days of assignment results
in temporary access suspension until completion.
