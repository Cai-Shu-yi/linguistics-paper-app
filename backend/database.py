import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "papers.db")


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    db = await get_db()
    await db.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            title_zh TEXT,
            authors TEXT NOT NULL,
            journal TEXT NOT NULL,
            journal_type TEXT NOT NULL,
            jif_quartile TEXT,
            jif REAL,
            publish_date TEXT NOT NULL,
            doi TEXT,
            url TEXT,
            keywords TEXT,
            abstract TEXT,
            abstract_zh TEXT,
            ai_summary TEXT,
            ai_methodology TEXT,
            ai_innovation TEXT,
            ai_literature_review TEXT,
            ai_future_directions TEXT,
            ai_generated_at TEXT,
            source TEXT DEFAULT 'mock',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS fetch_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            papers_found INTEGER DEFAULT 0,
            papers_new INTEGER DEFAULT 0,
            status TEXT DEFAULT 'success',
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await db.commit()
    await db.close()


async def paper_exists(doi: str) -> bool:
    db = await get_db()
    cursor = await db.execute("SELECT id FROM papers WHERE doi = ?", (doi,))
    row = await cursor.fetchone()
    await db.close()
    return row is not None


async def update_paper_abstract(doi: str, abstract: str) -> bool:
    """Update an existing paper's abstract. Returns True if updated."""
    if not doi or not abstract:
        return False
    db = await get_db()
    cursor = await db.execute(
        "UPDATE papers SET abstract = ? WHERE doi = ? AND (abstract IS NULL OR abstract = '')",
        (abstract, doi)
    )
    updated = cursor.rowcount > 0
    await db.commit()
    await db.close()
    return updated


async def save_paper(paper: dict) -> bool:
    """Save a paper to DB. Returns True if new, False if duplicate."""
    doi = paper.get("doi", "")
    if doi and await paper_exists(doi):
        return False

    import uuid
    paper_id = paper.get("id") or str(uuid.uuid4())

    db = await get_db()
    await db.execute("""
        INSERT OR REPLACE INTO papers (
            id, title, title_zh, authors, journal, journal_type,
            jif_quartile, jif, publish_date, doi, url, keywords,
            abstract, abstract_zh, ai_summary, ai_methodology,
            ai_innovation, ai_literature_review, ai_future_directions,
            ai_generated_at, source
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        paper_id,
        paper.get("title", ""),
        paper.get("title_zh"),
        ",".join(paper.get("authors", [])) if isinstance(paper.get("authors"), list) else paper.get("authors", ""),
        paper.get("journal", ""),
        paper.get("journal_type", ""),
        paper.get("jif_quartile"),
        paper.get("jif"),
        paper.get("publish_date", ""),
        doi,
        paper.get("url", ""),
        ",".join(paper.get("keywords", [])) if isinstance(paper.get("keywords"), list) else paper.get("keywords", ""),
        paper.get("abstract", ""),
        paper.get("abstract_zh"),
        paper.get("ai_summary"),
        paper.get("ai_methodology"),
        paper.get("ai_innovation"),
        paper.get("ai_literature_review"),
        paper.get("ai_future_directions"),
        paper.get("ai_generated_at"),
        paper.get("source", "api"),
    ))
    await db.commit()
    await db.close()
    return True


async def get_papers(
    keywords: list[str] | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
    journal_type: str | None = None,
) -> list[dict]:
    db = await get_db()
    query = "SELECT * FROM papers WHERE 1=1"
    params: list = []

    if search:
        query += " AND (title LIKE ? OR title_zh LIKE ? OR authors LIKE ? OR journal LIKE ? OR keywords LIKE ? OR abstract LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s, s, s, s])

    if journal_type:
        query += " AND journal_type = ?"
        params.append(journal_type)

    if keywords:
        kw_clauses = []
        for kw in keywords:
            kw_clauses.append("(keywords LIKE ? OR title LIKE ? OR title_zh LIKE ? OR abstract LIKE ?)")
            k = f"%{kw}%"
            params.extend([k, k, k, k])
        query += f" AND ({' OR '.join(kw_clauses)})"

    query += " ORDER BY publish_date DESC, created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    await db.close()

    papers = []
    for row in rows:
        d = dict(row)
        d["authors"] = d["authors"].split(",") if d["authors"] else []
        d["keywords"] = d["keywords"].split(",") if d["keywords"] else []
        d["aiAnalysis"] = None
        if d.get("ai_summary"):
            d["aiAnalysis"] = {
                "summary": d.pop("ai_summary"),
                "methodology": d.pop("ai_methodology"),
                "innovation": d.pop("ai_innovation"),
                "literatureReview": d.pop("ai_literature_review"),
                "futureDirections": d.pop("ai_future_directions"),
                "generatedAt": d.pop("ai_generated_at"),
            }
        papers.append(d)

    return papers


async def log_fetch(source: str, found: int, new: int, status: str = "success", error: str = None):
    db = await get_db()
    await db.execute(
        "INSERT INTO fetch_log (source, papers_found, papers_new, status, error) VALUES (?,?,?,?,?)",
        (source, found, new, status, error),
    )
    await db.commit()
    await db.close()
