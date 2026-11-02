import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
actors = ["Verifier", "Web Client", "Application Server", "Database"]
X = [1.5, 5.0, 9.0, 13.0]
fig, ax = plt.subplots(figsize=(14, 10.5)); ax.set_xlim(0, 14.5); ax.set_ylim(0, 10.5); ax.axis("off")
ax.text(7.25, 10.25, "Sequence Diagram - Document Verification (ID / QR / File)", ha="center", fontsize=15, weight="bold")
for n, x in zip(actors, X):
    ax.add_patch(Rectangle((x - 1.0, 9.35), 2.0, 0.55, fc="#DEEBF7", ec="black"))
    ax.text(x, 9.62, n, ha="center", va="center", fontsize=11, weight="bold")
    ax.plot([x, x], [0.3, 9.35], color="gray", ls="--", lw=1)
def msg(y, a, b, text, ret=False, self_=False):
    xa, xb = X[a], X[b]
    if self_:
        ax.plot([xa, xa + 0.7, xa + 0.7, xa], [y, y, y - 0.35, y - 0.35], color="black", lw=1.2)
        ax.annotate("", xy=(xa, y - 0.35), xytext=(xa + 0.1, y - 0.35), arrowprops=dict(arrowstyle="-|>", color="black"))
        ax.text(xa + 0.85, y - 0.17, text, fontsize=9.5, va="center"); return
    ax.annotate("", xy=(xb, y), xytext=(xa, y), arrowprops=dict(arrowstyle="-|>", color="black", lw=1.2, ls="--" if ret else "-"))
    ax.text((xa + xb) / 2, y + 0.1, text, ha="center", fontsize=9.5)
steps = [
 (8.85, 0, 1, "1. enter ID / scan QR / upload file", False),
 (8.35, 1, 2, "2. POST /api/verify/{id|qr|upload}", False),
 (7.85, 2, 2, "3. validate input (ID format FR-25, file type/size)", "self"),
 (7.15, 2, 3, "4. SELECT document WHERE verification_id = ?", False),
 (6.65, 3, 2, "5. record (or none)", True),
]
for y, a, b, t, k in steps:
    msg(y, a, b, t, ret=(k is True), self_=(k == "self"))
# alt frames
def frame(y1, y2, label, x1=0.4, x2=14.2):
    ax.add_patch(Rectangle((x1, y2), x2 - x1, y1 - y2, fc="none", ec="#444444", lw=1.2))
    ax.add_patch(Rectangle((x1, y1 - 0.3), 1.6, 0.3, fc="#F2F2F2", ec="#444444"))
    ax.text(x1 + 0.1, y1 - 0.15, label, fontsize=9, va="center", weight="bold")
frame(6.35, 2.0, "alt")
ax.text(2.2, 6.1, "[no record]", fontsize=9.5, style="italic")
msg(5.75, 2, 1, "6a. result = NOT FOUND (no metadata, FR-26)", ret=True)
ax.plot([0.4, 14.2], [5.4, 5.4], color="#444444", ls="--", lw=1)
ax.text(2.2, 5.2, "[record revoked]", fontsize=9.5, style="italic")
msg(4.85, 2, 1, "6b. result = INVALID (FR-29)", ret=True)
ax.plot([0.4, 14.2], [4.5, 4.5], color="#444444", ls="--", lw=1)
ax.text(2.2, 4.3, "[record active]", fontsize=9.5, style="italic")
msg(3.75, 2, 2, "6c. if file submitted: SHA-256(file) == stored hash ? (FR-32/33)", self_=True)
msg(3.1, 2, 1, "6d. result = VERIFIED or TAMPERED (hash mismatch, FR-28)", ret=True)
# after alt
msg(1.65, 2, 3, "7. INSERT verification_logs (ID, time, method, result)", False)
msg(1.15, 3, 2, "8. ack", True)
msg(0.65, 2, 1, "9. JSON result", True)
msg(0.3, 1, 0, "10. display result page", True)
plt.savefig("diagrams/Sequence Diagram.pdf", bbox_inches="tight"); plt.savefig("diagrams/Sequence Diagram.png", dpi=170, bbox_inches="tight")
