import graphviz as G, os
OUT = "diagrams"
FONT = "Helvetica"

def new(name, **g):
    d = G.Digraph(name, format="pdf")
    d.attr(fontname=FONT, labelloc="t", fontsize="18", **g)
    d.attr("node", fontname=FONT, fontsize="11")
    d.attr("edge", fontname=FONT, fontsize="10")
    return d

def save(d, fname):
    d.render(os.path.join(OUT, fname), cleanup=True)
    d.format = "png"; d.graph_attr["dpi"] = "170"
    d.render(os.path.join(OUT, fname), cleanup=True)

# ---------- USE CASE ----------
d = new("uc", rankdir="LR", label="Use Case Diagram - Digital Document Verification System", nodesep="0.3", ranksep="1.0", newrank="true")
for a, l in [("V", "General User /\\nVerifier"), ("I", "Issuing\\nOrganization"), ("A", "System\\nAdministrator")]:
    d.node(a, f"«actor»\\n{l}", shape="box", style="filled", fillcolor="#FFF2CC", width="1.4")
d.node("U", "«abstract actor»\\nUser", shape="box", style="dashed,filled", fillcolor="#F2F2F2", width="1.4")
with d.subgraph(name="cluster_sys") as s:
    s.attr(label="DDVS (System Boundary)", style="rounded", color="#444444", fontsize="13")
    s.attr("node", shape="ellipse", style="filled", fillcolor="#DEEBF7")
    for k, l in [("reg", "Register Account"), ("login", "Log In"), ("logout", "Log Out /\\nChange Password"),
                 ("reqorg", "Request Issuing\\nOrg Account"), ("regdoc", "Register Document"), ("qr", "Generate QR Code"),
                 ("mydocs", "View Own Documents"), ("ver", "Verify Document"), ("byid", "Verify by ID"),
                 ("byqr", "Verify by QR"), ("byfile", "Verify by File Upload"), ("hash", "Check Integrity Hash"),
                 ("hist", "View Own Verification\\nHistory"), ("appr", "Approve / Reject\\nIssuing Org"),
                 ("users", "Manage Users"), ("docs", "Manage Documents"), ("revoke", "Revoke Document"),
                 ("allhist", "View System-wide\\nHistory (filter)")]:
        s.node(k, l)
for a in "VIA": d.edge(a, "U", arrowhead="empty", label="is a" if a == "I" else "")
for k in ["login", "logout", "ver", "hist"]: d.edge("U", k, arrowhead="none")
d.edge("V", "reg", arrowhead="none")
for k in ["reqorg", "regdoc", "mydocs", "revoke"]: d.edge("I", k, arrowhead="none")
for k in ["appr", "users", "docs", "allhist"]: d.edge("A", k, arrowhead="none")
d.edge("ver", "hash", label="«include»", style="dashed")
for a, b in [("byid", "ver"), ("byqr", "ver"), ("byfile", "ver"), ("qr", "regdoc"), ("revoke", "docs")]:
    d.edge(a, b, label="«extend»", style="dashed")
save(d, "use case diagram")

# ---------- CLASS ----------
d = new("cls", rankdir="BT", label="Class Diagram - DDVS", nodesep="0.5", ranksep="0.8")
d.attr("node", shape="record", style="filled", fillcolor="#FFFFFF")
def C(n, attrs, meths, fill="#FFFFFF"):
    d.node(n, "{" + n + "|" + "\\l".join(attrs) + "\\l|" + "\\l".join(meths) + "\\l}", fillcolor=fill)
C("User", ["- userId: int", "- name: String", "- email: String", "- passwordHash: String", "- role: Role",
           "- status: AccountStatus", "- failedAttempts: int"],
  ["+ register()", "+ login()", "+ logout()", "+ changePassword()", "+ verifyDocument()", "+ viewHistory()"], "#DEEBF7")
C("GeneralUser", [], ["(role = VERIFIER)"])
C("IssuingOrganization", ["- orgName: String", "- approvalStatus: ApprovalStatus"],
  ["+ requestApproval()", "+ registerDocument()", "+ viewOwnDocuments()", "+ revokeOwnDocument()"])
C("Administrator", [], ["+ approveOrg()", "+ rejectOrg()", "+ disableUser()", "+ enableUser()", "+ revokeDocument()",
                         "+ viewAllHistory()", "+ filterHistory()"])
C("Document", ["- docId: int", "- verificationId: String", "- docType: String", "- recipientName: String",
                "- issueDate: Date", "- fileHash: String", "- filePath: String", "- status: DocStatus"],
  ["+ computeHash()", "+ generateQR()", "+ revoke()", "+ isActive()"], "#E2EFDA")
C("VerificationRequest", ["- method: Method", "- inputValue: String", "- uploadedFile: File"],
  ["+ validateFormat()", "+ submit()"], "#FFF2CC")
C("VerificationService", [], ["+ verify(request): Result", "+ compareHash(file, doc): boolean", "+ lookup(id): Document"], "#FFF2CC")
C("VerificationLog", ["- logId: int", "- verificationId: String", "- method: Method", "- result: Result", "- timestamp: DateTime"],
  ["+ record()", "+ listByUser()", "+ listAll()"], "#FCE4D6")
C("AuditLog", ["- auditId: int", "- action: String", "- targetType: String", "- targetId: int", "- timestamp: DateTime"],
  ["+ record()"], "#FCE4D6")
for sub in ["GeneralUser", "IssuingOrganization", "Administrator"]:
    d.edge(sub, "User", arrowhead="empty")
d.edge("IssuingOrganization", "Document", label="registers  1..*", arrowhead="none", headlabel="", taillabel="1")
d.edge("VerificationRequest", "VerificationService", label="processed by", arrowhead="vee")
d.edge("VerificationService", "Document", label="looks up / compares", arrowhead="vee")
d.edge("VerificationService", "VerificationLog", label="creates 1 per request", arrowhead="vee")
d.edge("VerificationLog", "Document", label="refers to 0..1", arrowhead="vee")
d.edge("User", "VerificationLog", label="performs 0..*", arrowhead="vee")
d.edge("Administrator", "AuditLog", label="generates 0..*", arrowhead="vee")
save(d, "class diagram")

# ---------- ACTIVITY ----------
d = new("act", label="Activity Diagram - Document Verification", nodesep="0.5", ranksep="0.45")
d.node("s", "", shape="circle", style="filled", fillcolor="black", width="0.25")
d.node("e", "", shape="doublecircle", style="filled", fillcolor="black", width="0.2")
A = lambda k, l: d.node(k, l, shape="box", style="rounded,filled", fillcolor="#DEEBF7")
D = lambda k, l: d.node(k, l, shape="diamond", style="filled", fillcolor="#FFF2CC")
R = lambda k, l, c: d.node(k, l, shape="box", style="rounded,filled", fillcolor=c)
A("in", "User submits Verification ID,\\nQR value or document file")
D("fmt", "ID format valid?\\n(FR-25)")
R("mal", "Display format error", "#F8CBAD")
A("look", "Look up record by\\nverification ID / file hash")
D("fnd", "Record found?")
R("nf", "Result = NOT FOUND\\n(no metadata shown, FR-26)", "#F8CBAD")
D("rev", "Record revoked?\\n(FR-29)")
R("inv", "Result = INVALID", "#F8CBAD")
D("fl", "File submitted?")
A("h", "Compute SHA-256 of file;\\ncompare with stored hash")
D("m", "Hashes match?")
R("tam", "Result = TAMPERED", "#F8CBAD")
R("ok", "Result = VERIFIED\\n(show non-sensitive metadata)", "#C6E0B4")
A("log", "Write verification-log entry\\n(ID, time, method, result)")
A("disp", "Display result to user")
d.edge("s", "in"); d.edge("in", "fmt"); d.edge("fmt", "mal", label="no"); d.edge("mal", "e")
d.edge("fmt", "look", label="yes"); d.edge("look", "fnd")
d.edge("fnd", "nf", label="no"); d.edge("fnd", "rev", label="yes")
d.edge("rev", "inv", label="yes"); d.edge("rev", "fl", label="no")
d.edge("fl", "ok", label="no"); d.edge("fl", "h", label="yes"); d.edge("h", "m")
d.edge("m", "tam", label="no"); d.edge("m", "ok", label="yes")
for r in ["nf", "inv", "tam", "ok"]: d.edge(r, "log")
d.edge("log", "disp"); d.edge("disp", "e")
save(d, "Activity Diagram")

# ---------- DFD ----------
def ent(d, k, l): d.node(k, l, shape="box", style="filled", fillcolor="#FFF2CC")
def store(d, k, l): d.node(k, l, shape="underline", fontsize="11")
d = new("dfd0", rankdir="LR", label="Data Flow Diagram - Level 0 (Context)", nodesep="1.0", ranksep="2.0")
d.node("P", "0\\nDigital Document\\nVerification System", shape="circle", style="filled", fillcolor="#DEEBF7", width="2.2")
for k, l in [("V", "Verifier"), ("I", "Issuing Organization"), ("A", "Administrator")]: ent(d, k, l)
d.edge("V", "P", label="registration / login data\\nverification request (ID, QR, file)")
d.edge("P", "V", label="auth response\\nverification result, history")
d.edge("I", "P", label="login / org request\\ndocument metadata + file, revoke request")
d.edge("P", "I", label="approval status\\nverification ID + QR, own document list")
d.edge("A", "P", label="approve/reject, disable/enable,\\nrevoke, history filters")
d.edge("P", "A", label="pending requests, user/document records,\\nsystem-wide verification history")
save(d, "Dataflow Diagram L0")

d = new("dfd1", rankdir="TB", label="Data Flow Diagram - Level 1", nodesep="0.7", ranksep="1.1")
for k, l in [("V", "Verifier"), ("I", "Issuing Organization"), ("A", "Administrator")]: ent(d, k, l)
for k, l in [("P1", "1.0\\nManage\\nAccounts"), ("P2", "2.0\\nRegister\\nDocument"), ("P3", "3.0\\nVerify\\nDocument"),
             ("P4", "4.0\\nMaintain\\nVerification Log"), ("P5", "5.0\\nAdminister\\nSystem")]:
    d.node(k, l, shape="circle", style="filled", fillcolor="#DEEBF7", width="1.4")
for k, l in [("D1", "D1 User Store"), ("D2", "D2 Document Store"), ("D3", "D3 Verification Log Store"), ("D4", "D4 Admin Audit Log Store")]:
    store(d, k, l)
d.edge("V", "P1", label="register / login"); d.edge("I", "P1", label="login, org request"); d.edge("P1", "V", label="auth result")
d.edge("P1", "D1", label="account records"); d.edge("D1", "P1", label="credentials, status")
d.edge("I", "P2", label="metadata + file"); d.edge("P2", "I", label="verification ID, QR")
d.edge("P2", "D2", label="record + SHA-256 hash"); d.edge("D1", "P2", label="issuer role check")
d.edge("V", "P3", label="ID / QR / file"); d.edge("P3", "V", label="result")
d.edge("D2", "P3", label="stored record + hash"); d.edge("P3", "P4", label="attempt details")
d.edge("P4", "D3", label="log entry"); d.edge("D3", "P4", label="entries")
d.edge("P4", "V", label="own history"); d.edge("P4", "A", label="all history (filtered)")
d.edge("A", "P5", label="approve/reject, disable, revoke, search")
d.edge("P5", "A", label="requests, records"); d.edge("P5", "D1", label="status updates"); d.edge("D1", "P5", label="user data")
d.edge("P5", "D2", label="revoke status"); d.edge("D2", "P5", label="document data"); d.edge("P5", "D4", label="admin actions")
save(d, "Dataflow Diagram")

# ---------- STATE TRANSITION ----------
from PIL import Image
specs = [("doc", "Document Record", ["ACTIVE", "REVOKED", "DELETED"],
          [("ACTIVE", "REVOKED", "revoke (Issuer own / Admin)"), ("REVOKED", "ACTIVE", "reinstate (Admin)"),
           ("REVOKED", "DELETED", "permanent delete (Admin)"), ("ACTIVE", "DELETED", "permanent delete (Admin)")], "ACTIVE"),
         ("acc", "Account (User / Issuing Organization)", ["PENDING", "ACTIVE", "REJECTED", "DISABLED", "LOCKED"],
          [("PENDING", "ACTIVE", "admin approves"), ("PENDING", "REJECTED", "admin rejects"), ("ACTIVE", "DISABLED", "admin disables"),
           ("DISABLED", "ACTIVE", "admin re-enables"), ("ACTIVE", "LOCKED", "5 failed logins / 15 min"),
           ("LOCKED", "ACTIVE", "window expires")], "PENDING"),
         ("ses", "Session", ["ANONYMOUS", "AUTHENTICATED", "TERMINATED"],
          [("ANONYMOUS", "AUTHENTICATED", "valid login"), ("AUTHENTICATED", "TERMINATED", "logout / 30 min inactivity"),
           ("TERMINATED", "ANONYMOUS", "redirect to login")], "ANONYMOUS"),
         ("vr", "Verification Request", ["SUBMITTED", "VALIDATED", "LOOKED_UP", "VERIFIED", "INVALID", "NOT_FOUND", "TAMPERED", "LOGGED"],
          [("SUBMITTED", "VALIDATED", "format ok"), ("VALIDATED", "LOOKED_UP", "db query"),
           ("LOOKED_UP", "NOT_FOUND", "no record"), ("LOOKED_UP", "INVALID", "record revoked"),
           ("LOOKED_UP", "TAMPERED", "hash mismatch"), ("LOOKED_UP", "VERIFIED", "active + hash ok"),
           ("NOT_FOUND", "LOGGED", ""), ("INVALID", "LOGGED", ""), ("TAMPERED", "LOGGED", ""), ("VERIFIED", "LOGGED", "")], "SUBMITTED")]
parts = []
for pfx, title, states, trans, start in specs:
    g = new("st_" + pfx, label=title, nodesep="0.5", ranksep="0.55", rankdir="TB")
    g.node("s", "", shape="circle", style="filled", fillcolor="black", width="0.2")
    for st in states: g.node(st, st, shape="box", style="rounded,filled", fillcolor="#DEEBF7")
    g.edge("s", start)
    for a, b, l in trans: g.edge(a, b, label=l)
    g.format = "png"; g.graph_attr["dpi"] = "200"
    g.render(os.path.join(OUT, "_st_" + pfx), cleanup=True)
    parts.append(Image.open(os.path.join(OUT, "_st_" + pfx + ".png")).convert("RGB"))
cw = max(p_.width for p_ in parts); ch = max(p_.height for p_ in parts)
sheet = Image.new("RGB", (cw * 2 + 60, ch * 2 + 160), "white")
from PIL import ImageDraw
from PIL import ImageFont
ImageDraw.Draw(sheet).text((30, 15), "State Transition Diagram - DDVS", fill="black", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44))
for k, im in enumerate(parts):
    sheet.paste(im, (20 + (k % 2) * (cw + 20), 80 + (k // 2) * (ch + 20)))
sheet.save(os.path.join(OUT, "State Transition Diagram.pdf"), resolution=200)
sheet.save(os.path.join(OUT, "State Transition Diagram.png"))
for pfx, *_ in specs: os.remove(os.path.join(OUT, "_st_" + pfx + ".png"))

# ---------- COMPONENT ----------
d = new("cmp", rankdir="TB", label="Component Diagram - DDVS (three-tier)", nodesep="0.35", ranksep="0.8", compound="true")
d.attr("node", shape="component", style="filled", fillcolor="#DEEBF7")
with d.subgraph(name="cluster_c") as c:
    c.attr(label="Client Tier - Web Browser", style="rounded"); 
    for k, l in [("ui_auth", "Login / Register UI"), ("ui_dash", "User Dashboard"), ("ui_reg", "Document Registration UI"),
                 ("ui_ver", "Verification UI\\n(ID / QR scan / upload)"), ("ui_res", "Result Page"), ("ui_adm", "Admin Dashboard")]: c.node(k, l)
with d.subgraph(name="cluster_s") as c:
    c.attr(label="Application Tier - Application Server (REST / JSON over HTTPS)", style="rounded")
    c.node("gw", "REST API Gateway\\n+ Session & RBAC Middleware\\n+ Input Validation", fillcolor="#FFF2CC")
    for k, l in [("m_auth", "Authentication Module"), ("m_reg", "Document Registration Module"), ("m_ver", "Verification Module"),
                 ("m_int", "Integrity Service\\n(SHA-256)"), ("m_qr", "QR Code Service"), ("m_adm", "Administration Module"),
                 ("m_log", "Logging / Audit Module")]: c.node(k, l)
with d.subgraph(name="cluster_d") as c:
    c.attr(label="Data Tier", style="rounded")
    c.node("db", "Relational Database\\n(users, documents,\\nverification_logs, admin_audit_logs)", shape="cylinder", fillcolor="#E2EFDA")
    c.node("fs", "Private File Storage\\n(no public URL, NFR-10)", shape="folder", fillcolor="#E2EFDA")
for k in ["ui_auth", "ui_dash", "ui_reg", "ui_ver", "ui_res", "ui_adm"]: d.edge(k, "gw", label="HTTPS" if k == "ui_auth" else "", arrowhead="vee")
for k in ["m_auth", "m_reg", "m_ver", "m_adm"]: d.edge("gw", k, arrowhead="vee")
d.edge("m_reg", "m_int", label="«uses»", style="dashed"); d.edge("m_ver", "m_int", label="«uses»", style="dashed")
d.edge("m_reg", "m_qr", label="«uses»", style="dashed")
for k in ["m_ver", "m_adm", "m_reg"]: d.edge(k, "m_log", style="dashed", label="«uses»" if k == "m_ver" else "")
for k in ["m_auth", "m_reg", "m_ver", "m_adm", "m_log"]: d.edge(k, "db", arrowhead="vee")
d.edge("m_reg", "fs", arrowhead="vee")
save(d, "Component Diagram")

# ---------- ER ----------
d = new("er", rankdir="LR", label="ER Diagram - DDVS", nodesep="0.8", ranksep="1.6")
def T(n, rows, fill):
    h = f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3"><TR><TD BGCOLOR="{fill}"><B>{n}</B></TD></TR>'
    for r in rows: h += f'<TR><TD ALIGN="LEFT">{r}</TD></TR>'
    d.node(n, h + "</TABLE>>", shape="plaintext")
T("users", ["<B>PK</B> user_id", "name", "email (UNIQUE)", "password_hash", "role (VERIFIER|ISSUER|ADMIN)",
            "status (PENDING|ACTIVE|REJECTED|DISABLED)", "org_name (issuers)", "failed_attempts", "last_failed_at", "created_at"], "#DEEBF7")
T("documents", ["<B>PK</B> doc_id", "verification_id (UNIQUE)", "<I>FK</I> org_id &#8594; users", "doc_type", "recipient_name", "issue_date",
                "file_hash (INDEX)", "file_path", "status (ACTIVE|REVOKED)", "created_at"], "#E2EFDA")
T("verification_logs", ["<B>PK</B> log_id", "<I>FK</I> doc_id &#8594; documents (nullable)", "<I>FK</I> user_id &#8594; users (nullable)",
                        "input_ref (ID or file hash)", "method (ID|QR|UPLOAD)", "result (VERIFIED|INVALID|NOT_FOUND|TAMPERED)", "timestamp"], "#FCE4D6")
T("admin_audit_logs", ["<B>PK</B> audit_id", "<I>FK</I> admin_id &#8594; users", "action", "target_type (USER|DOCUMENT)", "target_id", "timestamp"], "#FFF2CC")
d.edge("users", "documents", label="registers\\n1 : N", arrowhead="crow", arrowtail="tee", dir="both")
d.edge("documents", "verification_logs", label="is checked in\\n1 : N (0..1 per log)", arrowhead="crow", arrowtail="tee", dir="both")
d.edge("users", "verification_logs", label="performs\\n1 : N (optional)", arrowhead="crow", arrowtail="tee", dir="both")
d.edge("users", "admin_audit_logs", label="admin performs\\n1 : N", arrowhead="crow", arrowtail="tee", dir="both")
save(d, "ER Diagram")
print(sorted(os.listdir(OUT)))
