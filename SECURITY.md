# Security Policy

YouTube Playlist Builder is a personal desktop utility, not a maintained product with an SLA. It
does handle real credentials though — a Google OAuth `client_secret.json` and the resulting
`token.json`, which grants playlist management access to whatever Google account authorizes it —
so a vulnerability here could mean unauthorized access to a user's YouTube account/playlists.

## Reporting a vulnerability

Please use GitHub's [private vulnerability reporting](../../security/advisories/new) — the
**"Report a vulnerability"** button under this repo's **Security** tab — instead of a public
issue. It opens a private draft advisory so nothing gets disclosed before a fix ships.

There's no bug bounty and no guaranteed response time, but reports will be looked at and a fix
or mitigation will be pushed as soon as practical. Credit is welcome if you'd like it.

## Scope

In scope: `main.py`, `gui.py`, and the CI/release tooling around them — in particular anything
that could expose `client_secret.json`/`token.json` contents, weaken the OAuth flow, or let
untrusted input reach the YouTube API in an unexpected way.

Out of scope: the YouTube Data API, Google's OAuth infrastructure, and CustomTkinter/tkinterdnd2
— report issues in those upstream.

## A note on credentials

`client_secret.json`, `token.json`, and `cache.json` are all git-ignored and live only in your
local working directory — never commit them. If you believe real credentials ever landed in this
repo's tracked history, please report it privately rather than filing a public issue.
