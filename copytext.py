"""Turn a producer's research note into one or two clean sentences of history for the page.

The note is a working log: facts about the farm interleaved with how they were found, checked and
ruled on. The page shows the facts and never the method. So: split the note into sentences and
clauses, drop every clause that speaks about the research, keep the leading run of clean clauses
of each sentence, and take sentences in order until the budget is spent — cutting only at a
sentence or clause boundary, never mid-phrase.
"""
import re

PROCESS_SRC = r"""
  (?<![\w-])(?:pass(?:es)?|brief(?:'s)?|hazards?|rosters?|harvest(?:er|ed|ing)?s?|scout|entity|entities|alias(?:es)?|namesakes?|
  confirm(?:ed|s|ation)?|corroborat\w*|resolv\w*|flag(?:ged|s)?|queue[ds]?|retriev\w*|fetch\w*|seed(?:ed|s)?|merge[ds]?|
  records?|recorded|files?|register|registry|registration|sources?|sourced|sourcing|unanimous|cit(?:ed|ation|ing)|json|robots|nav|
  triage|ruling|adopt\w*|geocod\w*|gps|lat|lng|null|stale|junk|director(?:y|ies)|aggregator|listings?|tiers?|hierarchy|tranche|
  audit\w*|auditor|verif\w*|re-sourced|phase|sweep|encoded|blurb|cards?|api|places|wikidata|osm|openstreetmap|withheld|url|www|
  count\ gap|lead|candidate|primary|secondary|trade-press|sa-venues|wine\.co\.za|platter\w*|homepage|website|web|site|pages?|
  domain|profile|search(?:es|ed)?|checked|check|contradiction|question|investigat\w*|blacklist\w*|guess\w*|rule|
  per\ (?:the|rule|hierarchy|brief)|this\ (?:pass|file|project)|the\ count|producer\ \#\d+|reciprocal|id|ids|status|pending|
  placeholder|scaffold|stub|todo|tbd|ask|owner's|the\ seed|nav\ list|member\ (?:page|cards?)|association(?:'s)?\ (?:own|member|page)|
  on\ file|not\ republished|data/|docs/|adr-\d+|ho-\d+|h\d|\d{4}-\d{2}-\d{2}|
  claims?|claimed|infer\w*|converted|set\ to|left\ (?:null|as|blank|unset)|written\ here|the\ reading|included|excluded|
  unchanged|footer|contact|address|phone|email|membership|self-description|description|says|states?|stated|mentions?|lists?|
  named\ body|treat(?:ed)?|kept|conflated|datum|load-bearing|tree|notes?|prior|evidence|plausibl\w*|likely|probably|apparent\w*|
  uncertain\w*|unclear|tension|disagreement|mismatch|contradict\w*|conflict\w*|ambigu\w*|one\ record|kept\ here|item|official|
  cluster|purposes|positioning|owed|surfaced|the\ producer's\ own|producers?'s?\ own|own\ (?:sites?|pages?|domains?)|article|section\ structure|headings?|pdf|holds\ the\ rest|modelling\ call|\S+-harvester\S*|single-source|multi-source|two-source|field|fields|
  populated|correct(?:ed|ion)?|typo|spelling|spelt|rendered|read\ as|reads|reading|footnote|caveat|nb|note\ for|
  atlas|filed|per|self-describ\w*|describ\w*|producer-site|producer-stated|venueat|venue/access|e\.g\.|see|case|cases\ like|
  inference|suggestive|genuinely|silence|closure|unknown|forcing|distinct\ from|so\ far|\w+=\S*|remain\w*\ unknown|
  hosted\ here|leads\ with|not\ (?:a|the)\ (?:second|separate|venue)|regardless|therefore|hence|thus|i\.e\.|viz\.|
  interpret\w*|assum\w*|presum\w*|reason\w*|justif\w*|deliberately\ (?:left|not)|on\ the\ (?:reading|basis)|basis|
  the\ same\ (?:page|site|source)|already\ in|elsewhere\ in|this\ region's|pattern|convention|criteri\w+|blocking|moved|
  the\ test|cross-link|renamed\ to|prints|place[sd]?\ it|industry\ profiles|the\ same\ group|unrelated|sharing\ a|element|
  \(producer\)|in\ because|is\ in|one\ is|winewiki|wineanorak|wosa|vinpro|news24|publish\w*|trade\ registry|wineinthecape|
  same-label|specifically|strictly|explicit\w*|literal\w*|verbatim|quoted?|quoting|wording|phrase[sd]?|phrasing|term|terms|
  varieties|cultivars|flagship\ wines:|caution|does\ not\ fit|consistent\ with|pre-dates|map\ only|from\ a\ \d{4}|po\ box|
  delivery|limited\ to|range\ only|hosted|venue:|relation|nothing\ more|recommends?|insideguide|inside\ guide|\(association\)|unverif\w*|operational\ currency|used\ here|not\ used
  )(?![\w-])
"""
HOURS_ONLY = r"""
  (?<![\w-])(?:bookings|\d{1,2}:\d{2}|(?:mon|tue|wed|thu|fri|sat|sun)(?:-|\b)|hours)(?![\w-])
"""
PROCESS_HISTORY = re.compile(PROCESS_SRC + "|" + HOURS_ONLY, re.I | re.X)
PROCESS_HOURS = re.compile(PROCESS_SRC, re.I | re.X)
PROCESS = PROCESS_HISTORY
DOMAIN = re.compile(r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:co\.za|com|org|net|wine|info|africa|za)\b(?:/\S*)?", re.I)
SMALL = {'IN','OF','AT','ON','TO','IS','AS','BY','OR','AN','SO','NO','UP','IT','BE','WE','DO','IF','NOT','AND','THE','FOR'}
ACRONYMS = {'VOC','KWV','SAWIS','IWSC','DWWA','WO','SA','GPS','N1','N2','N7','R44','R45','R62','R43','R46','R301','R304','R310','R43','R320','R27','PTY','LTD','CWG','MCC','WWF','WIETA','IPW','UK','USA','EU','SB','CS','DEIC','KLM','TTT','MW','OBE','II','III','IV','CEO','CWM','PJM','JC','MJ','JP','DBV','BWI','FNB','ABSA','AC','DC','CVC','VC','VD','JD','PC','JS','AG','WC','GG','AI','KM','HA','OZ','OVP','GM','JW','DGB','SIP','DWVA','R317','M3','M23'}

def _sentences(t):
    t = re.sub(r"\s+", " ", t).strip()
    # protect common abbreviations from the sentence splitter
    t = re.sub(r"\b(St|Mt|Dr|Mr|Mrs|Ms|Prof|Jr|Sr|Snr|Jnr|No|ca|approx|est|vs|Rev|Ave|Rd|Gov|Lt|Capt|Col|Gen|Hon|Cdr|Adm|Bros|Co|Ltd|Pty|Inc|cf|viz|fl|c)\.\s", lambda m: m.group(1) + "․ ", t)
    parts, start, depth, quote = [], 0, 0, 0
    for i, ch in enumerate(t):
        if ch == "(": depth += 1
        elif ch == ")": depth = max(0, depth - 1)
        elif ch == "'" and (i == 0 or t[i-1] in " (") and i + 1 < len(t) and t[i+1] != " ": quote += 1
        elif ch == "'" and i > 0 and t[i-1] not in " (" and (i + 1 == len(t) or t[i+1] in " .,;:)"): quote = max(0, quote - 1)
        elif ch in ".!?" and depth == 0 and quote == 0 and i + 2 < len(t) and t[i+1] == " " and (t[i+2].isupper() or t[i+2] in "0123456789'\"“("):
            parts.append(t[start:i+1]); start = i + 2
    parts.append(t[start:])
    return [p.replace("․", ".") for p in parts if p.strip()]

def _clean_clause(c):
    c = DOMAIN.sub("", c)
    c = re.sub(r"\(\s*\)", "", c)                                   # emptied parentheses
    c = re.sub(r"\[[^\]]*\]", "", c)                                 # [number withheld] and the like
    c = re.sub(r"`([^`]*)`", r"\1", c)
    c = re.sub(r"\s+([,;:.])", r"\1", c)
    c = re.sub(r"\s{2,}", " ", c).strip(" ,;:—-")
    return c

LABELS = re.compile(r"^(?:History|Scale|Founded|Varieties|Location|Wines?|Style|Range|Ownership(?: succession)?|Owners?|Blurb|Address|Contact|Hours|Venue|Access|Postal|Web|GPS|Winemaker|Cellarmaster|Origin|Background|Story|Identity|Note|Summary)\s*:\s*", re.I)
def _balance(t):
    """a dropped clause can leave a bracket or quotation open: close it by trimming the tail, else give the sentence up"""
    if t.count("(") > t.count(")"):
        k = t.rfind("(")
        if ")" in t[k:]: return ""
        t = t[:k].rstrip(" ,;:—-")
    if t.count("(") < t.count(")"): return ""
    opens = [m.start() for m in re.finditer(r"(?:(?<=[ (])|^)'(?=\S)", t)]
    closes = [m.start() for m in re.finditer(r"(?<=\S)'(?=[ .,;:)]|$)", t)]
    if len(opens) != len(closes):
        if opens and (not closes or opens[-1] > closes[-1]): t = t[:opens[-1]].rstrip(" ,;:—-")
        else: return ""
    return t

def _strip_label(s):
    s = LABELS.sub("", s)
    # "FOUNDED 1843 — ...", "ENTITY RESOLVED 2026-08-30: ...", "RULING: ..." — a shouted label before the content
    m = re.match(r"^([A-Z][A-Z0-9'’&/#().\- ]{2,60}?)(?::|\s—|\s-\s)\s*(.*)$", s)
    if m and len(m.group(1).split()) <= 6:
        label, rest = m.group(1), m.group(2)
        founded = re.search(r"\b(1[6-9]\d\d|20[0-2]\d)\b", label)
        if founded and label.upper().startswith("FOUNDED") and rest and not rest[:1].isupper():
            return f"Founded {founded.group(1)}: {rest}"
        if founded and label.upper().startswith("FOUNDED"):
            return f"Founded {founded.group(1)}. {rest}"
        return rest
    return s

def _decap(word, vocab):
    if "-" in word or "/" in word:
        return re.sub(r"[A-Za-z']+", lambda m: _decap(m.group(0), vocab), word)
    lower_vocab, proper_vocab = vocab
    core = re.sub(r"[^A-Za-z]", "", word)
    if len(core) < 2 or not core.isupper() or core in ACRONYMS: return word
    if len(core) == 2: return word.lower() if core in SMALL else word
    if core.capitalize() in proper_vocab and core.lower() not in lower_vocab:
        return re.sub(core, core.capitalize(), word, count=1)
    if core.lower() in lower_vocab:
        return word.lower()
    return word.lower()

def _unshout(s, lowercase_vocab):
    out = []
    for i, w in enumerate(s.split(" ")):
        nw = _decap(w, lowercase_vocab)
        out.append(nw)
    s = " ".join(out)
    return s[:1].upper() + s[1:] if s else s

def history(note, lowercase_vocab, budget=230, mode="history"):
    global PROCESS
    PROCESS = PROCESS_HOURS if mode == "hours" else PROCESS_HISTORY
    if not note: return ""
    t = note.replace("--", "—").replace(" – ", " — ")
    kept = []
    for s in _sentences(t):
        s = _strip_label(s.strip())
        if not s: continue
        clauses = re.split(r"(;\s+|\s—\s)", s)
        run, glue = [], []
        for i in range(0, len(clauses), 2):
            c = clauses[i]
            # a parenthetical that talks about method is dropped on its own; the clause survives
            c = re.sub(r"\s*\(([^()]*)\)", lambda m: "" if PROCESS.search(m.group(1)) or DOMAIN.search(m.group(1)) else m.group(0), c)
            if PROCESS.search(c) or DOMAIN.search(c) or re.search(r'\s[<>=]\s|\[\[|\*\*|\|', c): break
            cc = _clean_clause(c)
            if not cc: break
            if run: glue.append(clauses[i-1])
            run.append(cc)
        if not run: continue
        text = run[0]
        for g, c in zip(glue, run[1:]): text += g + c
        text = text.strip(" ,;:—-")
        text = _balance(text)
        if len(text) < 25: continue
        if re.match(r"^[\)'\"”’]|^[a-z]", text): continue          # a sentence that began inside a quote or bracket
        if text[0].islower(): text = text[0].upper() + text[1:]
        if not re.search(r"[.!?…”\"')]$", text): text += "."
        kept.append(text)
    if not kept: return ""
    out = ""
    for s in kept:
        if not out: out = s
        elif len(out) + 1 + len(s) <= budget: out += " " + s
        else: break
    if len(out) > budget:
        cut = out[:budget]
        k = max(cut.rfind("; "), cut.rfind(" — "), cut.rfind(", "))
        if k > 80:
            out = cut[:k].rstrip(" ,;—") + "."
        else:
            out = cut.rsplit(" ", 1)[0].rstrip(" ,;—") + "…"
    out = _unshout(out, lowercase_vocab)
    out = re.sub(r"\s+([,;:.])", r"\1", out)
    out = re.sub(r"([;,])\.$", ".", out)
    return out

def lowercase_vocabulary(notes):
    """(words seen in lower case, words seen Capitalised mid-sentence) across the whole corpus — how a
    shouted word is un-shouted: 'OLDEST' → 'oldest', 'CRYSTALLUM' → 'Crystallum', 'VOC' stays."""
    lower, proper = set(), set()
    for n in notes:
        for w in re.findall(r"\b[a-z]{3,}\b", n or ""): lower.add(w)
        for m in re.finditer(r"(?<=[a-z,;] )([A-Z][a-z]{2,})", n or ""): proper.add(m.group(1))
    return lower, proper
