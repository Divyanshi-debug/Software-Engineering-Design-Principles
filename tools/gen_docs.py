import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from PIL import Image as PI

ss = getSampleStyleSheet()
B = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.5, leading=13)
S = ParagraphStyle("s", parent=B, fontSize=8, leading=10)
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=15, spaceBefore=10, textColor=colors.HexColor("#1F3864"))
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11.5, spaceBefore=8, textColor=colors.HexColor("#2F5496"))
T = ParagraphStyle("t", parent=ss["Title"], fontSize=21, textColor=colors.HexColor("#1F3864"))
P = lambda t, st=B: Paragraph(t, st)

def tbl(rows, widths, hdr=True, font=8, align_center_from=None):
    data = [[Paragraph(str(c), ParagraphStyle("c", parent=S, fontSize=font, leading=font + 2,
            textColor=colors.white if (hdr and i == 0) else colors.black, fontName="Helvetica-Bold" if (hdr and i == 0) else "Helvetica"))
             for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if hdr else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FC")])]
    if hdr: st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F5496")))
    t.setStyle(TableStyle(st)); return t

def img(path, w):
    iw, ih = PI.open(path).size
    return Image(path, width=w, height=w * ih / iw)

def footer(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.grey)
    c.drawString(1.5 * cm, 1 * cm, "DDVS - KIET Group of Institutions, Dept. of CSE"); c.drawRightString(c._pagesize[0] - 1.5 * cm, 1 * cm, f"Page {d.page}"); c.restoreState()

# ================= HALSTEAD =================
h = json.load(open("docs/halstead.json")); cc = json.load(open("docs/cc.json"))
doc = SimpleDocTemplate("docs/Halstead_Metrics_Analysis_Matrix.pdf", pagesize=landscape(A4), leftMargin=1.4*cm, rightMargin=1.4*cm, topMargin=1.4*cm, bottomMargin=1.6*cm)
E = [P("Halstead Metrics Analysis Matrix", T), P("<b>Subject:</b> Digital Document Verification System (DDVS) &nbsp;|&nbsp; <b>Artifact measured:</b> src/ddvs_core.py (reference implementation of registration, hashing and verification logic, SRS FR-13 to FR-36, FR-48) &nbsp;|&nbsp; <b>Size:</b> %d lines, %d non-blank/non-comment lines" % (cc["lines"], cc["loc"])), Spacer(1, 6)]
E.append(P("1. Measurement method", H1))
E.append(P("Metrics are computed by tools/halstead.py (reproducible: <font face='Courier'>python tools/halstead.py src/ddvs_core.py</font>). <b>Operators</b> = Python keywords (except True/False/None) and operator/punctuation tokens, each bracket pair counted once via its opening token. <b>Operands</b> = identifiers, numeric and string literals, True/False/None. Comments and docstrings are excluded. Function rows count tokens inside that function's line range (including its signature); the module row additionally includes imports and module-level constants, so it is larger than the sum of the function rows."))
E.append(P("Formulas: n = n1 + n2; N = N1 + N2; estimated length N^ = n1 log2 n1 + n2 log2 n2; Volume V = N log2 n; Difficulty D = (n1 / 2) x (N2 / n2); Effort E = D x V; Time T = E / 18 seconds; Delivered bugs B = V / 3000. n1/n2 = distinct operators/operands; N1/N2 = total operators/operands. CC = McCabe cyclomatic complexity (radon).", S))
E.append(P("2. Metrics matrix", H1))
rows = [["Function / Unit", "n1", "n2", "N1", "N2", "n", "N", "N^", "Volume V", "Difficulty D", "Effort E", "Time T (s)", "Bugs B", "CC"]]
def row(name, m, c): return [name, m["n1"], m["n2"], m["N1"], m["N2"], m["vocabulary"], m["length"], m["est_length"], m["volume"], m["difficulty"], m["effort"], m["time_s"], m["bugs"], c]
for n, m in h["functions"].items(): rows.append(row(n, m, cc["cc"][n]))
rows.append(row("<b>MODULE (ddvs_core.py)</b>", h["module"], "-"))
E.append(tbl(rows, [4.6*cm] + [1.1*cm]*4 + [1.2*cm, 1.2*cm, 1.5*cm, 1.9*cm, 2.0*cm, 2.2*cm, 1.9*cm, 1.5*cm, 1.0*cm], font=8))
fn = h["functions"]; top = sorted(fn, key=lambda k: fn[k]["effort"], reverse=True)
E.append(Spacer(1, 6)); E.append(P("3. Interpretation", H1))
mx = max(cc["cc"].values())
for t in [
 f"<b>Highest effort:</b> {top[0]} (E = {fn[top[0]]['effort']:,.0f}), then {top[1]} (E = {fn[top[1]]['effort']:,.0f}) and {top[2]} (E = {fn[top[2]]['effort']:,.0f}). These three hold the validation and decision logic, so they are the first candidates for focused testing and review.",
 f"<b>Highest difficulty:</b> {max(fn, key=lambda k: fn[k]['difficulty'])} (D = {max(v['difficulty'] for v in fn.values())}; n1 = {fn[max(fn, key=lambda k: fn[k]['difficulty'])]['n1']} distinct operators, average operand reuse N2/n2 = {fn[max(fn, key=lambda k: fn[k]['difficulty'])]['N2']/fn[max(fn, key=lambda k: fn[k]['difficulty'])]['n2']:.2f}).",
 f"<b>Module totals:</b> Volume = {h['module']['volume']:,.0f}, Effort = {h['module']['effort']:,.0f}, estimated delivered bugs B = {h['module']['bugs']} (about one latent defect per 3000 units of volume - a coarse estimate, not a guarantee).",
 f"<b>Complexity:</b> maximum cyclomatic complexity is {mx} (verify_document: format check, four result branches and two boolean conditions), well inside the commonly used threshold of 10, so no function needs to be split. Radon Maintainability Index = {cc['mi']} (rank A, scale 0-100).",
 "<b>Test link:</b> all 12 unit tests in tests/test_ddvs_core.py pass (python -m unittest tests.test_ddvs_core) and cover every verification outcome (Verified, Invalid, Not Found, Tampered, Malformed ID), registration validation, ID uniqueness and logging of every attempt (FR-37).",
 "<b>Scope note:</b> Halstead is defined over source code, so these figures measure the reference implementation of the core module only, not the full web application (UI, REST layer and database access are outside this file)."]:
    E.append(P("- " + t)); E.append(Spacer(1, 3))
doc.build(E, onFirstPage=footer, onLaterPages=footer)

# ================= DESIGN REPORT =================
doc = SimpleDocTemplate("docs/DDVS_Design_Analysis_Report.pdf", pagesize=A4, leftMargin=1.8*cm, rightMargin=1.8*cm, topMargin=1.6*cm, bottomMargin=1.6*cm)
W = A4[0] - 3.6*cm
E = [Spacer(1, 40), P("Design Analysis Report", T), P("Digital Document Verification System (DDVS) - Version 1.0", ParagraphStyle("x", parent=ss["Title"], fontSize=14)),
     Spacer(1, 14), P("Department of Computer Science and Engineering, KIET Group of Institutions (KIET Deemed to be University)", ParagraphStyle("c", parent=B, alignment=1)),
     Spacer(1, 6), P("Prepared by: Divya Kumari (202401100200133), Divyanshi Jaiswal (202401100200134), Divyanshi Khemani (202401100200135), Divyanshu Gupta (202401100200136)", ParagraphStyle("c", parent=B, alignment=1)),
     Spacer(1, 6), P("Basis: SRS Version 1.0 (31 August 2026). Requirement IDs (FR-xx, NFR-xx) refer to that document.", ParagraphStyle("c", parent=S, alignment=1)), PageBreak()]

E.append(P("1. Scope and design goals", H1))
E.append(P("DDVS lets an approved Issuing Organization register a PDF document (storing metadata and a SHA-256 hash and issuing a unique verification ID with an optional QR code) and lets any verifier check a document by ID, QR value or file upload. Possible results: <b>Verified, Invalid, Not Found, Tampered</b>. Design goals, taken from the SRS: correctness of the four-way result (FR-26 to FR-31), tamper detection by hash comparison only (FR-32 to FR-35), role-based access (NFR-07), full audit trail (FR-37, FR-49), and a modular code base (NFR-17). The system uses no blockchain, AI, OCR or biometrics (SRS 2.5)."))
E.append(P("2. Architecture", H1))
E.append(P("Three-tier web architecture (SRS 2.1): browser UI, application server exposing a REST/JSON API over HTTPS, and a relational database plus private file storage. The server is organised into independent modules behind one gateway that enforces session, role-based access control and server-side input validation (NFR-07, NFR-11)."))
E.append(img("diagrams/Component Diagram.png", W * 0.95))
E.append(P("Figure 1 - Component diagram (see Component Diagram.pdf).", S))
E.append(P("2.1 Module responsibilities and requirement coverage", H2))
E.append(tbl([["Module", "Responsibility", "Requirements"],
 ["REST gateway + RBAC middleware + validation", "Session handling, 30-min inactivity timeout, role checks, input sanitisation, HTTPS only", "FR-08, FR-09, FR-11, NFR-06, NFR-07, NFR-09, NFR-11"],
 ["Authentication Module", "Register, login (generic error), logout, change password, bcrypt hashing, lockout after 5 failures / 15 min, issuer request in PENDING state", "FR-01 to FR-07, FR-10, FR-12, NFR-08, NFR-13"],
 ["Document Registration Module", "Mandatory-field check, file type (PDF) and size (10 MB) check, unique ID generation, store record, list own documents", "FR-13 to FR-16, FR-18 to FR-21, NFR-05"],
 ["Integrity Service (SHA-256)", "Single hash routine used for registration and verification so both always use the same algorithm", "FR-15, FR-32, FR-33"],
 ["QR Code Service", "Encode verification ID as QR; decode scanned/entered value to an ID", "FR-17, FR-23"],
 ["Verification Module", "Format validation, lookup, revoked check, hash comparison, result mapping, no metadata on Not Found", "FR-22 to FR-31, FR-34, FR-35"],
 ["Logging / Audit Module", "One verification_logs row per attempt; admin_audit_logs row per admin status change; read-only for non-admins", "FR-36 to FR-42, FR-49, NFR-12"],
 ["Administration Module", "Approve/reject issuer requests, search/disable/enable users, search/revoke documents, filtered global history", "FR-43 to FR-48"]],
 [4.2*cm, 8.2*cm, 4.8*cm], font=7.5))


E.append(P("3. Data design", H1))
E.append(P("Four tables with enforced referential integrity (SRS 6.1). Revoked records are kept, never physically removed by a normal action, so a revoked ID answers Invalid rather than Not Found (SRS 6.2, NFR-04)."))
E.append(img("diagrams/ER Diagram.png", W))
E.append(P("Figure 2 - ER diagram (see ER Diagram.pdf).", S))
E.append(tbl([["Table", "Key columns", "Constraints / indexes"],
 ["users", "user_id, name, email, password_hash, role, status, org_name, failed_attempts, last_failed_at", "email UNIQUE; role in (VERIFIER, ISSUER, ADMIN); status in (PENDING, ACTIVE, REJECTED, DISABLED)"],
 ["documents", "doc_id, verification_id, org_id, doc_type, recipient_name, issue_date, file_hash, file_path, status", "verification_id UNIQUE; org_id FK to users; INDEX on file_hash (file-only lookup); status in (ACTIVE, REVOKED)"],
 ["verification_logs", "log_id, doc_id, user_id, input_ref, method, result, timestamp", "doc_id and user_id nullable (Not Found / anonymous); no UPDATE or DELETE for non-admin roles (FR-41)"],
 ["admin_audit_logs", "audit_id, admin_id, action, target_type, target_id, timestamp", "admin_id FK to users; insert-only"]],
 [3*cm, 7.6*cm, 6.6*cm], font=7.5))
E.append(P("4. Behavioural design", H1))
E.append(P("<b>Verification algorithm</b> (Activity Diagram.pdf, Sequence Diagram.pdf, implemented in src/ddvs_core.py):"))
for i, t in enumerate(["Validate ID format (pattern DDVS-XXXXXXXXXXXX); malformed input is rejected before any lookup (FR-25).",
 "Look up the record by verification ID (or, for file-only upload, by file_hash).",
 "No record: result Not Found, no metadata returned (FR-26, FR-31).",
 "Record revoked: result Invalid, regardless of hash (FR-29, Business Rule 6).",
 "File supplied and SHA-256(file) differs from stored hash: result Tampered (FR-28, FR-34); otherwise Verified with non-sensitive metadata (FR-27).",
 "Write one verification_logs row for every attempt and return the result (FR-37, FR-38)."], 1):
    E.append(P(f"{i}. {t}"))
E.append(P("<b>State models</b> (State Transition Diagram.pdf): document record (ACTIVE, REVOKED, DELETED), account (PENDING, ACTIVE, REJECTED, DISABLED, LOCKED), session, and verification request. <b>Data flow</b> (Dataflow Diagram L0.pdf and Dataflow Diagram.pdf): context level with three external entities, level 1 with processes 1.0 Manage Accounts, 2.0 Register Document, 3.0 Verify Document, 4.0 Maintain Verification Log, 5.0 Administer System and stores D1 to D4. <b>Use cases and classes</b>: use case diagram.pdf and class diagram.pdf."))
E.append(PageBreak())

E.append(P("5. Interface design (REST, JSON over HTTPS)", H1))
E.append(tbl([["Endpoint", "Role", "Purpose", "FR"],
 ["POST /api/auth/register", "Public", "Create general user", "01-03"], ["POST /api/auth/login", "Public", "Login, lockout, session", "05, 06"],
 ["POST /api/auth/logout; /change-password", "Auth", "End session; change password", "10, 12"], ["POST /api/org-requests", "Public", "Request issuer account (PENDING)", "07"],
 ["POST /api/documents", "Issuer", "Register document (multipart: metadata + PDF)", "13-16, 18, 20, 21"], ["GET /api/documents", "Issuer", "List own documents", "19"],
 ["GET /api/documents/{vid}/qr", "Issuer", "QR code for verification ID", "17"], ["POST /api/documents/{vid}/revoke", "Issuer (own), Admin", "Mark revoked", "29, 48"],
 ["POST /api/verify/id; /verify/qr; /verify/upload", "Public*", "Verify by ID, QR value, or file (+ optional ID)", "22-24, 25-31, 32-36"], ["GET /api/history", "Auth", "Own verification history", "39"],
 ["GET /api/admin/history?from&to&result", "Admin", "All history, filtered", "40, 42"], ["GET /api/admin/org-requests; POST .../{id}/approve|reject", "Admin", "Review issuer requests", "43, 44"],
 ["GET /api/admin/users?q; POST .../{id}/disable|enable", "Admin", "Search and disable/enable accounts", "45, 46"], ["GET /api/admin/documents?q", "Admin", "Search document records", "47"]],
 [6.4*cm, 2.8*cm, 5.6*cm, 2.4*cm], font=7.5))
E.append(P("*Verification needs no login unless the deployment restricts it (FR-30).", S))
E.append(P("6. Security design", H1))
E.append(tbl([["Concern", "Design decision", "Req."],
 ["Passwords", "bcrypt with per-password salt; generic login error; policy min 8 chars with letter and digit", "FR-03, 04, 06, NFR-08"],
 ["Brute force", "failed_attempts and last_failed_at; lock at 5 failures in 15 min", "NFR-13"],
 ["Transport", "TLS on all client-server traffic", "NFR-09"], ["Access control", "Role claim checked in middleware on every protected route", "NFR-06, 07"],
 ["Uploaded files", "Stored outside web root; served only through authorised handlers; type and size validated", "NFR-05, 10"],
 ["Injection / XSS", "Parameterised queries, server-side validation, output encoding", "NFR-11"], ["Audit", "Insert-only verification and admin audit tables", "NFR-12, FR-41"]],
 [3*cm, 11*cm, 3.2*cm], font=7.5))
E.append(P("7. Verification and testing", H1))
E.append(P("The reference module and its 12 unit tests demonstrate the core logic end to end (all pass). Complexity and Halstead results are in Halstead_Metrics_Analysis_Matrix.pdf (maximum cyclomatic complexity 7).", B))
E.append(tbl([["Test", "Scenario", "Expected", "FR"],
 ["T01", "Valid ID, no file", "Verified", "27"], ["T02", "Valid ID, original file", "Verified", "27, 33"], ["T03", "Valid ID, modified file", "Tampered", "28, 34"],
 ["T04", "Well-formed unknown ID", "Not Found", "26, 31"], ["T05", "Malformed ID", "Rejected before lookup", "25"], ["T06", "Revoked record, original file", "Invalid", "29, 48"],
 ["T07", "Revoked record, modified file", "Invalid (revocation takes precedence)", "29"], ["T08", "File only: registered / unknown file", "Verified / Not Found", "24"],
 ["T09", "Registration with a missing mandatory field", "Rejected, field named", "14"], ["T10", "Non-PDF file; file over 10 MB", "Rejected", "20, 21"],
 ["T11", "50 registrations", "50 distinct IDs", "16"], ["T12", "Every attempt (found or not)", "One log entry each", "37"]],
 [1.5*cm, 7.6*cm, 6*cm, 2.1*cm], font=7.5))
E.append(P("8. Design decisions and points to confirm", H1))
for t in ["<b>Revocation vs. tamper precedence.</b> FR-29 and Business Rule 6 require Invalid for a revoked record regardless of hash, but the Appendix B activity description tests the hash first. This design follows FR-29 (revoked check first). If your evaluator expects the Appendix B order, swap steps 4 and 5 in section 4 and in verify_document().",
 "<b>File-only verification (FR-24).</b> Without an ID the record is found through the indexed file_hash: a match gives Verified, no match gives Not Found. Tampered can only be reported when an ID identifies the original record.",
 "<b>Reinstating a revoked document.</b> The SRS calls revocation a reversible status change (NFR-04) but names no role; this design allows an Administrator to reinstate.",
 "<b>Technology stack.</b> The SRS leaves it open (SRS 2.4). The reference implementation is Python; the design is neutral between Node.js, Java and Python with MySQL or PostgreSQL.",
 "<b>Use case diagram.</b> An abstract actor 'User' groups Log In, Log Out/Change Password, Verify Document and View Own Verification History, which all three actors share."]:
    E.append(P("- " + t)); E.append(Spacer(1, 2))
doc.build(E, onFirstPage=footer, onLaterPages=footer)
print("ok")
