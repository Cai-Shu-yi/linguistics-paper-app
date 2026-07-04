"""
Paper fetcher: queries CrossRef API for recent papers from 212 target journals,
filters by keywords, and stores results in the database.
"""
import asyncio
import hashlib
import re
import httpx
from datetime import datetime, timedelta
from backend.database import save_paper, log_fetch, init_db

CROSSREF_URL = "https://api.crossref.org/works"
SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
USER_AGENT = "LinguisticsPaperApp/1.0 (mailto:dev@example.com)"

# ----- SSCI Journal names (for CrossRef ISSN matching, we use journal name as filter) -----
SSCI_JOURNAL_NAMES = [
    "Computational Linguistics", "Transactions of the Association for Computational Linguistics",
    "Annual Review of Applied Linguistics", "Computer Assisted Language Learning", "System",
    "Language Teaching", "ReCALL", "Journal of Second Language Writing", "Assessing Writing",
    "RELC Journal", "Innovation in Language Learning and Teaching",
    "Studies in Second Language Acquisition", "Annual Review of Linguistics",
    "Studies in Second Language Learning and Teaching", "TESOL Quarterly",
    "Language Teaching Research", "Modern Language Journal", "Language Learning & Technology",
    "Applied Linguistics Review", "Language Assessment Quarterly", "ELT Journal",
    "Journal of Sociolinguistics", "Applied Linguistics", "International Journal of Applied Linguistics",
    "Journal of Multilingual and Multicultural Development", "Journal of English for Academic Purposes",
    "Language Policy", "Language Learning", "Journal of Memory and Language",
    "International Journal of Corpus Linguistics", "Language and Education", "Language Awareness",
    "English for Specific Purposes", "Linguistics and Education",
    "International Multilingual Research Journal", "Language Speech and Hearing Services in Schools",
    "Metaphor and Symbol", "Language Testing", "Language Culture and Curriculum",
    "Journal of Fluency Disorders", "Research on Language and Social Interaction",
    "Linguistic Approaches to Bilingualism", "International Review of Applied Linguistics in Language Teaching",
    "American Journal of Speech-Language Pathology", "Natural Language Engineering",
    "Journal of Speech Language and Hearing Research", "Journal of Language and Social Psychology",
    "International Journal of Language & Communication Disorders", "Social Semiotics",
    "Applied Psycholinguistics", "Bilingualism-Language and Cognition", "Brain and Language",
    "Mind & Language", "Journal of Phonetics", "Linguistic Inquiry", "Argumentation",
    "Porta Linguarum", "Journal of Pragmatics", "Corpus Linguistics and Linguistic Theory",
    "First Language", "International Journal of Multilingualism", "Language Sciences",
    "Journal of Communication Disorders", "Aphasiology", "Language Cognition and Neuroscience",
    "Interpreter and Translator Trainer", "Language in Society", "Journal of Child Language",
    "International Journal of Bilingual Education and Bilingualism", "Interpreting",
    "Signs and Society", "Language", "Journal of Politeness Research",
    "Literacy", "Foreign Language Annals", "Journal of Psycholinguistic Research",
    "Journal of Language Identity and Education", "Current Issues in Language Planning",
    "Journal of Specialised Translation", "Language and Intercultural Communication",
    "Journal of Language and Politics", "Cognitive Linguistics",
    "International Journal of Lexicography", "Language & Communication",
    "Child Language Teaching & Therapy", "Language Acquisition", "Translation Studies",
    "Second Language Research", "Language Variation and Change",
    "English Teaching-Practice and Critique", "Journal of English Linguistics",
    "Language and Cognition", "Lingua", "International Journal of Speech-Language Pathology",
    "International Journal of Bilingualism", "Journal of Linguistic Anthropology",
    "Linguistics and Philosophy", "Target-International Journal of Translation Studies",
    "Journal of Neurolinguistics", "Intercultural Pragmatics",
    "Laboratory Phonology", "Australian Journal of Linguistics",
    "English World-Wide", "Gender and Language", "Diachronica", "Linguistics",
    "Linguistic Typology", "World Englishes", "Lexikos",
    "Perspectives-Studies in Translation Theory and Practice", "Language Matters",
    "Journal of East Asian Linguistics", "Translator", "Journal of Linguistics",
    "Linguistic Review", "Language Learning and Development", "Narrative Inquiry",
    "Clinical Linguistics & Phonetics", "Language and Speech",
    "Translation and Interpreting Studies", "Language Problems & Language Planning",
    "Digital Scholarship in The Humanities", "Journal of Quantitative Linguistics",
    "Gesture", "Probus", "Terminology", "Journal of Semantics",
    "Across Languages and Cultures", "English Today", "English Language & Linguistics",
    "Topics in Language Disorders", "Journal of French Language Studies", "Phonetica",
    "Glossa", "Text & Talk", "Canadian Modern Language Review",
    "Interaction Studies", "Natural Language & Linguistic Theory",
    "Linguistics Vanguard", "Journal of Historical Pragmatics",
    "Journal of the International Phonetic Association", "Theoretical Linguistics",
    "Functions of Language", "Natural Language Semantics", "Language and Literature",
    "Journal of African Languages and Linguistics", "Studies in Language",
    "Review of Cognitive Linguistics", "Folia Linguistica",
    "Phonology", "Spanish in Context", "Revista Signos",
    "European Journal of English Studies", "American Speech", "Pragmatics",
    "Pragmatics and Society", "Nordic Journal of Linguistics",
    "International Journal of American Linguistics", "Journal of Germanic Linguistics",
    "Poznan Studies in Contemporary Linguistics", "Journal of Pidgin and Creole Languages",
    "Zeitschrift Fur Sprachwissenschaft", "Acta Linguistica Academica",
    "Language and Linguistics", "Sintagma", "Onomazein",
    "Journal of Comparative Germanic Linguistics", "Language & History",
    "Journal of Chinese Linguistics", "International Journal of Speech Language and The Law",
    "Historiographia Linguistica", "Language Problems and Language Planning",
    "Langages", "Africana Linguistica",
]

def generate_paper_id(title: str, doi: str = "") -> str:
    raw = doi or title
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _clean_abstract(text: str) -> str:
    """Strip XML/HTML tags from CrossRef abstracts and normalize."""
    if not text:
        return ""
    # Remove XML tags like <jats:p>, <jats:italic>, etc.
    text = re.sub(r'<[^>]+>', '', text)
    # Replace common XML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#x27;', "'").replace('&apos;', "'")
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


async def _fetch_crossref_page(client: httpx.AsyncClient, journal_name: str, rows: int = 20) -> list[dict]:
    """Fetch recent papers from a specific journal via CrossRef."""
    params = {
        "filter": f"container-title:{journal_name},from-pub-date:2026-06-01",
        "rows": rows,
        "sort": "published",
        "order": "desc",
    }
    try:
        resp = await client.get(CROSSREF_URL, params=params, timeout=30.0)
        if resp.status_code != 200:
            return []
        data = resp.json()
        items = data.get("message", {}).get("items", [])
        return items
    except Exception:
        return []


def parse_crossref_item(item: dict, journal_name: str, journal_info: dict) -> dict | None:
    """Parse a CrossRef work item into our paper format."""
    title_raw = item.get("title", [])
    if not title_raw:
        return None

    title = title_raw[0]
    abstract = _clean_abstract(item.get("abstract", ""))
    author_list = item.get("author", [])
    if not author_list:
        return None

    authors = []
    for a in author_list:
        family = a.get("family", "")
        given = a.get("given", "")
        name = f"{family}, {given[0]}." if given else family
        if family and given:
            name = f"{given} {family}"
        if name.strip():
            authors.append(name.strip())

    doi = item.get("DOI", "")
    paper_id = generate_paper_id(title, doi)

    # Check for open-access PDF link
    pdf_url = None
    link_list = item.get("link", [])
    for link in link_list:
        if link.get("content-type") == "application/pdf":
            pdf_url = link.get("URL")
            break
    if not pdf_url and doi:
        # Try Unpaywall for open-access PDF
        pdf_url = f"https://api.unpaywall.org/v2/{doi}?email=dev@unpaywall.org"

    # Publish date
    pub_parts = item.get("published-print", {}) or item.get("published-online", {}) or {}
    pub_date = ""
    if pub_parts:
        date_parts = pub_parts.get("date-parts", [[None]])[0]
        pub_date = "-".join(str(p or 1).zfill(2) for p in date_parts[:3])

    return {
        "id": paper_id,
        "title": title,
        "title_zh": None,
        "authors": authors,
        "journal": journal_name,
        "journal_type": journal_info.get("type", "SSCI"),
        "jif_quartile": journal_info.get("quartile"),
        "jif": journal_info.get("jif"),
        "publish_date": pub_date or datetime.now().strftime("%Y-%m-%d"),
        "doi": doi,
        "url": f"https://doi.org/{doi}" if doi else None,
        "keywords": [],
        "abstract": abstract,
        "abstract_zh": None,
        "source": "crossref",
    }


async def _fetch_semantic_scholar(client: httpx.AsyncClient, query: str, limit: int = 20) -> list[dict]:
    """Search Semantic Scholar as supplementary source."""
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,journal,publicationDate,externalIds,abstract,year",
        "sort": "publicationDate:desc",
    }
    try:
        resp = await client.get(SEMANTIC_SCHOLAR_URL, params=params, timeout=30.0)
        if resp.status_code != 200:
            return []
        data = resp.json()
        return data.get("data", [])
    except Exception:
        return []


def parse_s2_item(item: dict, keyword: str) -> dict | None:
    """Parse a Semantic Scholar paper into our format."""
    title = item.get("title", "")
    if not title:
        return None

    authors = [a.get("name", "") for a in item.get("authors", [])]
    journal_info = item.get("journal") or {}
    journal = journal_info.get("name", "")

    doi = item.get("externalIds", {}).get("DOI", "")
    paper_id = generate_paper_id(title, doi)

    return {
        "id": paper_id,
        "title": title,
        "title_zh": None,
        "authors": authors,
        "journal": journal or "Unknown",
        "journal_type": "SSCI",
        "jif_quartile": None,
        "jif": None,
        "publish_date": item.get("publicationDate", ""),
        "doi": doi,
        "url": f"https://doi.org/{doi}" if doi else None,
        "keywords": [keyword],
        "abstract": item.get("abstract", ""),
        "abstract_zh": None,
        "source": "semantic_scholar",
    }


async def fetch_all_papers(
    keywords: list[str] | None = None,
    max_per_journal: int = 5,
    concurrent_journals: int = 5,
) -> dict:
    """
    Fetch papers from CrossRef for target SSCI journals.
    Uses keyword filtering on titles/abstracts.
    Returns {"found": int, "new": int}.
    """
    await init_db()

    # Build journal info lookup
    from backend.main import SSCI_JOURNALS
    journal_info_map = {j["name"].lower(): j for j in SSCI_JOURNALS}

    sem = asyncio.Semaphore(concurrent_journals)
    found_total = 0
    new_total = 0

    async def fetch_one_journal(client, journal_name):
        nonlocal found_total, new_total
        async with sem:
            items = await _fetch_crossref_page(client, journal_name, rows=max_per_journal)
            info = journal_info_map.get(journal_name.lower(), {"type": "SSCI"})
            count = 0
            for item in items:
                paper = parse_crossref_item(item, journal_name, info)
                if paper is None:
                    continue
                count += 1

                # Keyword filter
                if keywords:
                    match = False
                    search_text = (paper.get("title", "") + " " + paper.get("abstract", "")).lower()
                    for kw in keywords:
                        if kw.lower() in search_text:
                            match = True
                            break
                    if not match:
                        continue

                if await save_paper(paper):
                    new_total += 1
            return count

    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
    ) as client:
        tasks = [fetch_one_journal(client, name) for name in SSCI_JOURNAL_NAMES[:50]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, int):
                found_total += r
            elif isinstance(r, Exception):
                print(f"  Fetch error: {r}")

    # If not enough papers, also try Semantic Scholar with keywords
    if keywords and new_total < 10:
        async with httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=30.0,
        ) as client:
            for kw in keywords[:3]:
                items = await _fetch_semantic_scholar(client, f"{kw} linguistics", limit=10)
                for item in items:
                    paper = parse_s2_item(item, kw)
                    if paper and await save_paper(paper):
                        new_total += 1

    await log_fetch("crossref+semantic_scholar", found_total, new_total)
    return {"found": found_total, "new": new_total}
