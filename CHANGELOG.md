# Changelog

## 0.1.1 — 2026-10-28

- Update ECDSA, P-256 and P-384 dependencies to remove the crypto-bigint versions affected by RUSTSEC-2026-0387. Require crypto-bigint 0.7.10 or later within the 0.7 series, including for consumers with existing lockfiles.
- Preserve the public verification API, supported algorithms and Rust 1.88 minimum.
