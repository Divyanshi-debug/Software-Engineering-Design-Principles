# Digital Document Verification System (DDVS)

A web-based system that lets authorized organizations register digital documents (SHA-256 hash + unique verification ID + QR code) and lets anyone verify a document by **ID, QR code, or file upload**. Every check returns one of four results: **Verified, Invalid, Not Found, Tampered**. No blockchain, AI, OCR or biometrics - integrity is checked with standard cryptographic hashing and record comparison in a relational database.

Software Engineering project - Department of CSE, KIET Group of Institutions (KIET Deemed to be University).

## Team
| Name | Roll No. |
|---|---|
| Divya Kumari | 202401100200133 |
| Divyanshi Jaiswal | 202401100200134 |
| Divyanshi Khemani | 202401100200135 |
| Divyanshu Gupta | 202401100200136 |

## Key features
- Role-based access: General User / Verifier, Issuing Organization, System Administrator
- Document registration with unique verification ID, SHA-256 hash and QR code
- Verification by ID, QR value or file upload; tamper detection by hash comparison
- Revocation (reversible status change), verification history, admin audit log

## Repository contents
| File | Description |
|---|---|
| `DDVS_SRS.docx` | Software Requirements Specification v1.0 (add your SRS file here) |
| `DDVS_Presentation.pptx` | Project presentation (add your file here) |
| `use case diagram.pdf` | Actors and use cases (include/extend) |
| `class diagram.pdf` | Domain and service classes |
| `Activity Diagram.pdf` | Document verification flow |
| `Dataflow Diagram L0.pdf`, `Dataflow Diagram.pdf` | DFD level 0 (context) and level 1 |
| `State Transition Diagram.pdf` | Document record, account, session, verification request |
| `Component Diagram.pdf` | Three-tier component view |
| `ER Diagram.pdf` | Database design |
| `Sequence Diagram.pdf` | Verifier - Web Client - Server - Database interaction |
| `DDVS_Design_Analysis_Report.pdf` | Architecture, data, API, security design and FR traceability |
| `Halstead_Metrics_Analysis_Matrix.pdf` | Halstead and cyclomatic complexity of the core module |
| `src/ddvs_core.py` | Reference implementation of registration and verification logic |
| `tests/test_ddvs_core.py` | 12 unit tests covering all verification outcomes |
| `tools/` | Halstead calculator and diagram/report generators |

## Run the tests and metrics
```bash
python -m unittest tests.test_ddvs_core        # 12 tests
python tools/halstead.py src/ddvs_core.py      # Halstead metrics
```

## Verification rules (summary)
1. Malformed ID is rejected before lookup.
2. No matching record -> **Not Found** (no metadata shown).
3. Revoked record -> **Invalid** (regardless of hash).
4. Uploaded file whose SHA-256 differs from the stored hash -> **Tampered**.
5. Otherwise -> **Verified**.
Every attempt is written to the verification history.
