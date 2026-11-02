"""Classic Halstead metrics for a Python file (token-based). Usage: python halstead.py <file> [out.json]
Operators : keywords (except True/False/None) + operator/punctuation tokens; each bracket pair counted once (by opener).
Operands  : identifiers, numbers, strings, True/False/None. Comments and docstrings are excluded."""
import ast, io, json, keyword, math, sys, tokenize

CLOSERS = {")", "]", "}"}
OPERAND_KW = {"True", "False", "None"}


def halstead(tokens):
    ops, opr = {}, {}
    for t, v in tokens:
        d = ops if t == "op" else opr
        d[v] = d.get(v, 0) + 1
    n1, n2, N1, N2 = len(ops), len(opr), sum(ops.values()), sum(opr.values())
    n, N = n1 + n2, N1 + N2
    vol = N * math.log2(n) if n > 1 else 0
    diff = (n1 / 2) * (N2 / n2) if n2 else 0
    eff = diff * vol
    return dict(n1=n1, n2=n2, N1=N1, N2=N2, vocabulary=n, length=N,
                est_length=round((n1 * math.log2(n1) if n1 else 0) + (n2 * math.log2(n2) if n2 else 0), 2),
                volume=round(vol, 2), difficulty=round(diff, 2), effort=round(eff, 2),
                time_s=round(eff / 18, 2), bugs=round(vol / 3000, 4),
                operators=sorted(ops), top_ops={k: ops[k] for k in sorted(ops, key=ops.get, reverse=True)[:8]})


def main(path, out=None):
    src = open(path).read()
    tree = ast.parse(src)
    skip = set()
    for node in [tree] + [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))]:
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(getattr(node.body[0], "value", None), ast.Constant) \
                and isinstance(node.body[0].value.value, str):
            skip.update(range(node.body[0].lineno, node.body[0].end_lineno + 1))
    toks = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        line = tok.start[0]
        if line in skip or tok.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                                        tokenize.DEDENT, tokenize.ENDMARKER):
            continue
        s = tok.string
        if tok.type == tokenize.NAME:
            kind = "opr" if (not keyword.iskeyword(s) or s in OPERAND_KW) else "op"
        elif tok.type in (tokenize.NUMBER, tokenize.STRING):
            kind = "opr"
        elif tok.type == tokenize.OP:
            if s in CLOSERS:
                continue
            kind = "op"
        else:
            continue
        toks.append((line, kind, s))
    res = {"module": halstead([(k, v) for _, k, v in toks]), "functions": {}}
    for f in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        res["functions"][f.name] = halstead([(k, v) for l, k, v in toks if f.lineno <= l <= f.end_lineno])
    if out:
        json.dump(res, open(out, "w"), indent=1)
    return res


if __name__ == "__main__":
    r = main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    for n, m in [("MODULE", r["module"])] + list(r["functions"].items()):
        print(f"{n:26} n1={m['n1']:3} n2={m['n2']:3} N1={m['N1']:3} N2={m['N2']:3} V={m['volume']:8} D={m['difficulty']:6} E={m['effort']:9} B={m['bugs']}")
