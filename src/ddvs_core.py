"""DDVS core module: registration, hashing and verification logic (SRS FR-13..FR-36, FR-48)."""
import hashlib
import re
import uuid
from datetime import datetime

ALLOWED_TYPES = {"pdf"}
MAX_SIZE = 10 * 1024 * 1024
ID_PATTERN = re.compile(r"^DDVS-[0-9A-F]{12}$")


def compute_hash(data):
    """FR-15, FR-32: SHA-256 digest of file bytes."""
    return hashlib.sha256(data).hexdigest()


def generate_verification_id():
    """FR-16: unique verification ID."""
    return "DDVS-" + uuid.uuid4().hex[:12].upper()


def validate_upload(filename, data):
    """FR-20, FR-21: file type and size checks."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_TYPES:
        return False, "Unsupported file type"
    if len(data) > MAX_SIZE:
        return False, "File exceeds size limit"
    return True, "OK"


def register_document(store, org_id, doc_type, recipient, issue_date, filename, data):
    """FR-13..FR-16, FR-18: register a document and return its record."""
    missing = [k for k, v in (("doc_type", doc_type), ("recipient", recipient),
                              ("issue_date", issue_date)) if not v]
    if missing:
        return None, "Missing fields: " + ", ".join(missing)
    ok, msg = validate_upload(filename, data)
    if not ok:
        return None, msg
    vid = generate_verification_id()
    while vid in store:
        vid = generate_verification_id()
    store[vid] = {"org_id": org_id, "doc_type": doc_type, "recipient": recipient,
                  "issue_date": issue_date, "hash": compute_hash(data),
                  "status": "ACTIVE"}
    return vid, "Registered"


def verify_document(store, log, user_id, vid, method, data=None):
    """FR-22..FR-31, FR-33..FR-34, FR-37: return Verified/Invalid/Not Found/Tampered."""
    if not ID_PATTERN.match(vid or ""):
        return "Malformed ID"
    rec = store.get(vid)
    if rec is None:
        result = "Not Found"
    elif rec["status"] == "REVOKED":
        result = "Invalid"
    elif data is not None and compute_hash(data) != rec["hash"]:
        result = "Tampered"
    else:
        result = "Verified"
    log.append({"vid": vid, "user": user_id, "method": method,
                "result": result, "time": datetime.now().isoformat()})
    return result


def verify_by_file(store, log, user_id, data):
    """FR-24: file-only verification; look up registered record by file hash."""
    digest = compute_hash(data)
    for vid, rec in store.items():
        if rec["hash"] == digest:
            return verify_document(store, log, user_id, vid, "UPLOAD", data)
    log.append({"vid": None, "user": user_id, "method": "UPLOAD",
                "result": "Not Found", "time": datetime.now().isoformat()})
    return "Not Found"


def revoke_document(store, vid):
    """FR-48: mark a record as revoked (reversible status change, NFR-04)."""
    if vid in store:
        store[vid]["status"] = "REVOKED"
        return True
    return False
