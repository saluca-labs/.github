# Security Policy

This is the default security policy for every public repository in the `saluca-labs` organization.
If a repository carries its own `SECURITY.md`, that file takes precedence for that repository.

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

Email **security@saluca.com**.

Include, as far as you can:

- the repository, and the commit or version you tested
- what you did and what happened
- the impact you think it has
- how you want to be credited, or that you would rather not be

## What to expect

- We acknowledge receipt within 48 hours on business days.
- We tell you whether we consider it in scope, and why if we do not.
- If it is in scope, we give you a fix timeline and tell you when it is fixed.
- We do not pay a bounty. There is none, and saying so is better than implying one.
- If you want credit, we credit you in the commit and in the advisory. If you do not, we do not.

We ask that you give us a reasonable chance to fix an issue before publishing it. In exchange, we
will not pursue anyone who reports in good faith and stays inside the scope and safe harbour below.

## Scope

In scope:

- the code in these repositories, as published
- the packaging and release artefacts a repository names in its own README

Out of scope:

- third-party services these repositories talk to. Report those to the vendor.
- vulnerabilities in dependencies. Report those upstream, and tell us as well if a repository
  pins an affected version.
- anything about an instance you deploy and configure yourself
- findings that need access to another person's account, data or systems

If you cannot tell whether something is in scope, report it and we will tell you.

## Safe harbour

We will not take legal action against you, or report you to a platform, for research that:

- stays within the scope above
- does not access, change or delete data that is not yours
- does not degrade anything for anyone else
- does not use social engineering against Saluca Labs staff or anyone else
- gives us a reasonable chance to fix the issue before publishing

## Supported versions

Most repositories here do not maintain supported release branches: fixes land on the default
branch of the affected repository. Where a repository does maintain versions, its own `SECURITY.md`
says which ones are supported. `tiresias-core` is the only such repository today.

## What is in place, and what is not

We would rather name the gaps than let a policy imply more than it delivers.

In place:

- a published address for reports, and the acknowledgement above
- fixes on a branch, merged with a public commit that says what changed and why
- a per-repository policy wherever a repository has a specific guarantee to make, currently
  `tiresias-core`

Not in place:

- no bug bounty
- no PGP key published for the address yet. If you need to encrypt, say so in a first message and
  we will arrange it before you send details.
- no formal disclosure deadline. The timeline we give you is the one we commit to, and we will tell
  you if we are going to miss it.
- no hosted service to attack. Almost everything here is research and reproduction code, so the
  attack surface is the code you read and run, not a service you reach.

## Credit and disclosure

When an issue is fixed, the fix commit and any advisory name the reporter unless they asked not to be
named. If a finding turns out to affect something we published as a result, we correct the published
result rather than leaving it standing.

_Last updated: 2026-10-23_
