# oxidize-webpki

RustCrypto implementations of `rustls_pki_types::SignatureVerificationAlgorithm`
for certificate signature verification. Requires Rust 1.88 and `std`.

```rust
use oxidize_webpki::ALL_VERIFICATION_ALGS;

// Supply this explicit list as supported_sig_algs to WebPKI's
// EndEntityCert::verify_for_usage, together with trust anchors, intermediates,
// time, intended key usage, and the application's revocation policy.
assert!(!ALL_VERIFICATION_ALGS.is_empty());
```

The crate has no PDF, WebPKI, or TLS dependency. It implements public signature
verification only; it is not a rustls CryptoProvider (no key exchange, ciphers,
randomness, or signing). WebPKI remains responsible for path building, trust,
algorithm identifier matching, dates, key usage, constraints, and CRLs.
Applications must perform those checks; a successful primitive verification
alone does not establish certificate trust.

## Contract

The public `ALL_VERIFICATION_ALGS` slice contains 14 algorithm identifiers:

- RSA PKCS#1 v1.5 with SHA-256/384/512, accepting NULL or absent signature
  algorithm parameters. Public keys use rsaEncryption with NULL parameters.
- RSA-PSS with SHA-256/384/512, MGF1 using the same digest and salt length equal
  to the digest length, with rsaEncryption public keys.
- ECDSA P-256 and P-384, each with SHA-256 or SHA-384.
- Ed25519 (pure EdDSA), using Dalek's strict verification.

Verifiers take the public-key BIT STRING contents, the original message, and
signature bytes. RSA keys are DER PKCS#1 public keys, 2048–8192 bits, with an
exponent encoding of at most five bytes; signatures must have modulus length.
EC keys must be uncompressed SEC1 points (65/97 bytes), and ECDSA signatures
must be ASN.1 DER. Ed25519 keys/signatures must be 32/64 bytes. Invalid input
returns `InvalidSignature`; unsupported algorithms are absent from the list.
There is no automatic fallback to another provider. The ordering of entries
is not an API guarantee; select by both algorithm identifiers if needed.

## Provenance and limitations

Extracted from oxidize-pdf's MIT-licensed issue #627 adapter, originally by
Santiago Fernández Muñoz and contributors. See LICENSE. Cryptographic operations
are delegated to maintained RustCrypto crates: rsa, p256, p384, sha2 and
ed25519-dalek. This crate supplies decoding, policy bounds and dispatch; it
introduces no custom cryptographic primitives. It is independent of the
RustCrypto and rustls projects and does not imply their endorsement.

The crate forbids unsafe Rust in its own source. Dependencies may contain unsafe
code or architecture-specific intrinsics; pure Rust does not prove security.
Only public-key verification is exposed. No signing, private key operations,
FIPS certification, constant-time guarantee, or independent security audit is
claimed. Ed25519 strict verification intentionally rejects small-order inputs.
Certificate validation and application resource limits remain caller duties.

OpenSSL-generated public vectors and their provenance are included in
`tests/fixtures`; private keys were discarded. Tests exercise all 11 primitive
combinations, the three absent-parameter identifiers, wrong keys, malformed
inputs, tampering, key-size boundaries, PSS salt policy and weak Ed25519 keys.
No OpenSSL executable is needed to run tests.

```sh
cargo test -p oxidize-webpki
cargo +1.88 test -p oxidize-webpki
cargo package -p oxidize-webpki --allow-dirty
```

## Publishing

Maintainers publish from GitHub Actions using **Publish to crates.io** on
`main`, specifying the exact version from `Cargo.toml`. Publication waits for
Linux, Windows, macOS, Rust 1.88, formatting, Clippy, and packaging checks at
the same commit. The repository secret `CARGO_REGISTRY_TOKEN` authenticates
the publishing job; it is not provided to pull-request validation jobs.
