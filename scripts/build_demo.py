"""Inject data/financials.json into demo/template.html -> demo/index.html"""
import json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
data = (root / "data/financials.json").read_text()
html = (root / "demo/template.html").read_text().replace("/*DATA*/null", data)
(root / "demo/index.html").write_text(html)
print("built demo/index.html", len(html))
