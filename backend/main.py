import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.database import init_db, get_papers, log_fetch
from backend.paper_fetcher import fetch_all_papers

# Keywords for daily paper fetching
DAILY_KEYWORDS = [
    "language", "teaching", "syntax", "corpus", "acquisition",
    "translation", "multilingual", "pragmatics", "phonetics",
    "semantics", "discourse", "bilingual", "literacy",
    "\u4e8c\u8bed\u4e60\u5f97", "\u8bed\u6599\u5e93", "\u7ffb\u8bd1",
    "\u53e5\u6cd5", "\u8bed\u4e49", "\u8bed\u7528", "\u8ba4\u77e5",
]

scheduler = AsyncIOScheduler()


async def scheduled_fetch():
    """Auto-fetch papers daily."""
    print(f"[Scheduler] Starting daily paper fetch...")
    result = await fetch_all_papers(keywords=DAILY_KEYWORDS, max_per_journal=5)
    print(f"[Scheduler] Fetched {result['found']} papers, {result['new']} new.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Schedule daily fetch at 08:00 UTC
    scheduler.add_job(scheduled_fetch, "cron", hour=8, minute=0, id="daily_fetch")
    scheduler.start()
    # Also run once on startup (with slight delay to let server settle)
    asyncio.create_task(delayed_startup_fetch())
    yield
    scheduler.shutdown()


async def delayed_startup_fetch():
    await asyncio.sleep(5)
    await scheduled_fetch()


app = FastAPI(title="语言学论文速递 API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/journals")
async def list_journals():
    """Return the list of monitored CSSCI + SSCI journals (212 total)."""
    return {"journals": CSSCI_JOURNALS + SSCI_JOURNALS}


@app.get("/api/papers")
async def list_papers(
    keywords: str = Query(None, description="Comma-separated keywords"),
    search: str = Query(None, description="Full-text search query"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    journal_type: str = Query(None, description="CSSCI or SSCI"),
):
    """List papers with optional keyword/search filtering."""
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None
    papers = await get_papers(
        keywords=kw_list,
        search=search,
        limit=limit,
        offset=offset,
        journal_type=journal_type,
    )
    return {"papers": papers, "total": len(papers)}


@app.post("/api/papers/fetch")
async def trigger_fetch(
    keywords: str = Query(None, description="Comma-separated keywords"),
):
    """Trigger a fresh paper fetch from academic APIs."""
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None
    result = await fetch_all_papers(keywords=kw_list, max_per_journal=5)
    return result


@app.get("/api/stats")
async def get_stats():
    """Get paper statistics."""
    papers = await get_papers(limit=200)
    csci_count = sum(1 for p in papers if p.get("journal_type") == "CSSCI")
    ssci_count = sum(1 for p in papers if p.get("journal_type") == "SSCI")
    q1_count = sum(1 for p in papers if p.get("jif_quartile") == "Q1")
    return {
        "total": len(papers),
        "cssci": csci_count,
        "ssci": ssci_count,
        "q1": q1_count,
        "journals": 212,
    }


# ============================================================
# Journal Lists
# ============================================================

CSSCI_JOURNALS = [
    {"name": "外语教学与研究", "type": "CSSCI"},
    {"name": "外国语", "type": "CSSCI"},
    {"name": "外语界", "type": "CSSCI"},
    {"name": "现代外语", "type": "CSSCI"},
    {"name": "外语与外语教学", "type": "CSSCI"},
    {"name": "外语教学", "type": "CSSCI"},
    {"name": "外语研究", "type": "CSSCI"},
    {"name": "外语学刊", "type": "CSSCI"},
    {"name": "中国外语", "type": "CSSCI"},
    {"name": "外语电化教学", "type": "CSSCI"},
    {"name": "外语教学理论与实践", "type": "CSSCI"},
    {"name": "中国翻译", "type": "CSSCI"},
    {"name": "上海翻译", "type": "CSSCI"},
    {"name": "外国语文", "type": "CSSCI"},
    {"name": "解放军外国语学院学报", "type": "CSSCI"},
    {"name": "西安外国语大学学报", "type": "CSSCI"},
    {"name": "山东外语教学", "type": "CSSCI"},
]

SSCI_JOURNALS = [
    {"name": "Computational Linguistics", "type": "SSCI", "quartile": "Q1", "jif": 13.4},
    {"name": "Transactions of The Association For Computational Linguistics", "type": "SSCI", "quartile": "Q1", "jif": 11.7},
    {"name": "Annual Review of Applied Linguistics", "type": "SSCI", "quartile": "Q1", "jif": 10.8},
    {"name": "Computer Assisted Language Learning", "type": "SSCI", "quartile": "Q1", "jif": 8.7},
    {"name": "System", "type": "SSCI", "quartile": "Q1", "jif": 8.0},
    {"name": "Language Teaching", "type": "SSCI", "quartile": "Q1", "jif": 8.0},
    {"name": "ReCall", "type": "SSCI", "quartile": "Q1", "jif": 7.7},
    {"name": "Journal of Second Language Writing", "type": "SSCI", "quartile": "Q1", "jif": 7.7},
    {"name": "Assessing Writing", "type": "SSCI", "quartile": "Q1", "jif": 7.6},
    {"name": "RELC Journal", "type": "SSCI", "quartile": "Q1", "jif": 7.2},
    {"name": "Innovation in Language Learning and Teaching", "type": "SSCI", "quartile": "Q1", "jif": 5.5},
    {"name": "Studies in Second Language Acquisition", "type": "SSCI", "quartile": "Q1", "jif": 5.2},
    {"name": "Annual Review of Linguistics", "type": "SSCI", "quartile": "Q1", "jif": 5.2},
    {"name": "Studies in Second Language Learning and Teaching", "type": "SSCI", "quartile": "Q1", "jif": 5.1},
    {"name": "Tesol Quarterly", "type": "SSCI", "quartile": "Q1", "jif": 5.1},
    {"name": "Language Teaching Research", "type": "SSCI", "quartile": "Q1", "jif": 4.7},
    {"name": "Modern Language Journal", "type": "SSCI", "quartile": "Q1", "jif": 4.5},
    {"name": "Language Learning & Technology", "type": "SSCI", "quartile": "Q1", "jif": 4.5},
    {"name": "Applied Linguistics Review", "type": "SSCI", "quartile": "Q1", "jif": 4.4},
    {"name": "Language Assessment Quarterly", "type": "SSCI", "quartile": "Q1", "jif": 4.4},
    {"name": "ELT Journal", "type": "SSCI", "quartile": "Q1", "jif": 4.0},
    {"name": "Journal of Sociolinguistics", "type": "SSCI", "quartile": "Q1", "jif": 4.0},
    {"name": "Applied Linguistics", "type": "SSCI", "quartile": "Q1", "jif": 3.9},
    {"name": "International Journal of Applied Linguistics", "type": "SSCI", "quartile": "Q1", "jif": 3.8},
    {"name": "Journal of Multilingual and Multicultural Development", "type": "SSCI", "quartile": "Q1", "jif": 3.7},
    {"name": "Journal of English for Academic Purposes", "type": "SSCI", "quartile": "Q1", "jif": 3.7},
    {"name": "Language Policy", "type": "SSCI", "quartile": "Q1", "jif": 3.7},
    {"name": "Language Learning", "type": "SSCI", "quartile": "Q1", "jif": 3.5},
    {"name": "Journal of Memory and Language", "type": "SSCI", "quartile": "Q1", "jif": 3.5},
    {"name": "International Journal of Corpus Linguistics", "type": "SSCI", "quartile": "Q1", "jif": 3.3},
    {"name": "Language and Education", "type": "SSCI", "quartile": "Q1", "jif": 3.1},
    {"name": "Language Awareness", "type": "SSCI", "quartile": "Q1", "jif": 3.0},
    {"name": "English for Specific Purposes", "type": "SSCI", "quartile": "Q1", "jif": 3.0},
    {"name": "Linguistics and Education", "type": "SSCI", "quartile": "Q1", "jif": 3.0},
    {"name": "International Multilingual Research Journal", "type": "SSCI", "quartile": "Q1", "jif": 3.0},
    {"name": "Language Speech and Hearing Services in Schools", "type": "SSCI", "quartile": "Q1", "jif": 3.0},
    {"name": "Metaphor and Symbol", "type": "SSCI", "quartile": "Q1", "jif": 2.9},
    {"name": "Language Testing", "type": "SSCI", "quartile": "Q1", "jif": 2.8},
    {"name": "Language Culture and Curriculum", "type": "SSCI", "quartile": "Q1", "jif": 2.8},
    {"name": "Journal of Fluency Disorders", "type": "SSCI", "quartile": "Q1", "jif": 2.8},
    {"name": "Research on Language and Social Interaction", "type": "SSCI", "quartile": "Q1", "jif": 2.8},
    {"name": "Linguistic Approaches to Bilingualism", "type": "SSCI", "quartile": "Q1", "jif": 2.7},
    {"name": "IRAL - International Review of Applied Linguistics in Language Teaching", "type": "SSCI", "quartile": "Q1", "jif": 2.7},
    {"name": "American Journal of Speech-Language Pathology", "type": "SSCI", "quartile": "Q1", "jif": 2.5},
    {"name": "Natural Language Engineering", "type": "SSCI", "quartile": "Q1", "jif": 2.5},
    {"name": "Journal of Speech Language and Hearing Research", "type": "SSCI", "quartile": "Q1", "jif": 2.5},
    {"name": "Journal of Language and Social Psychology", "type": "SSCI", "quartile": "Q1", "jif": 2.5},
    {"name": "International Journal of Language & Communication Disorders", "type": "SSCI", "quartile": "Q1", "jif": 2.5},
    {"name": "Social Semiotics", "type": "SSCI", "quartile": "Q1", "jif": 2.4},
    {"name": "Applied Psycholinguistics", "type": "SSCI", "quartile": "Q1", "jif": 2.4},
    {"name": "Bilingualism-Language and Cognition", "type": "SSCI", "quartile": "Q1", "jif": 2.4},
    {"name": "Brain and Language", "type": "SSCI", "quartile": "Q1", "jif": 2.4},
    {"name": "Mind & Language", "type": "SSCI", "quartile": "Q1", "jif": 2.4},
    {"name": "Journal of Phonetics", "type": "SSCI", "quartile": "Q1", "jif": 2.3},
    {"name": "Linguistic Inquiry", "type": "SSCI", "quartile": "Q1", "jif": 2.3},
    {"name": "Argumentation", "type": "SSCI", "quartile": "Q1", "jif": 2.2},
    {"name": "Porta Linguarum", "type": "SSCI", "quartile": "Q1", "jif": 2.2},
    {"name": "Journal of Pragmatics", "type": "SSCI", "quartile": "Q1", "jif": 2.2},
    {"name": "Corpus Linguistics and Linguistic Theory", "type": "SSCI", "quartile": "Q1", "jif": 2.2},
    {"name": "First Language", "type": "SSCI", "quartile": "Q1", "jif": 2.2},
    {"name": "International Journal of Multilingualism", "type": "SSCI", "quartile": "Q1", "jif": 2.2},
    {"name": "Language Sciences", "type": "SSCI", "quartile": "Q1", "jif": 2.2},
    {"name": "Journal of Communication Disorders", "type": "SSCI", "quartile": "Q1", "jif": 2.2},
    {"name": "Aphasiology", "type": "SSCI", "quartile": "Q1", "jif": 2.2},
    {"name": "Language Cognition and Neuroscience", "type": "SSCI", "quartile": "Q1", "jif": 2.2},
    {"name": "Interpreter and Translator Trainer", "type": "SSCI", "quartile": "Q1", "jif": 2.1},
    {"name": "Language in Society", "type": "SSCI", "quartile": "Q1", "jif": 2.1},
    {"name": "Journal of Child Language", "type": "SSCI", "quartile": "Q1", "jif": 2.1},
    {"name": "International Journal of Bilingual Education and Bilingualism", "type": "SSCI", "quartile": "Q2", "jif": 2.0},
    {"name": "Interpreting", "type": "SSCI", "quartile": "Q2", "jif": 2.0},
    {"name": "Signs and Society", "type": "SSCI", "quartile": "Q2", "jif": 2.0},
    {"name": "Language", "type": "SSCI", "quartile": "Q2", "jif": 2.0},
    {"name": "Journal of Politeness Research-Language Behaviour Culture", "type": "SSCI", "quartile": "Q2", "jif": 2.0},
    {"name": "Literacy", "type": "SSCI", "quartile": "Q2", "jif": 2.0},
    {"name": "Foreign Language Annals", "type": "SSCI", "quartile": "Q2", "jif": 2.0},
    {"name": "Journal of Psycholinguistic Research", "type": "SSCI", "quartile": "Q2", "jif": 2.0},
    {"name": "Journal of Language Identity and Education", "type": "SSCI", "quartile": "Q2", "jif": 1.9},
    {"name": "Vial-Vigo International Journal of Applied Linguistics", "type": "SSCI", "quartile": "Q2", "jif": 1.9},
    {"name": "Current Issues in Language Planning", "type": "SSCI", "quartile": "Q2", "jif": 1.9},
    {"name": "Journal of Specialised Translation", "type": "SSCI", "quartile": "Q2", "jif": 1.9},
    {"name": "Language and Intercultural Communication", "type": "SSCI", "quartile": "Q2", "jif": 1.8},
    {"name": "Journal of Language and Politics", "type": "SSCI", "quartile": "Q2", "jif": 1.8},
    {"name": "Cognitive Linguistics", "type": "SSCI", "quartile": "Q2", "jif": 1.8},
    {"name": "International Journal of Lexicography", "type": "SSCI", "quartile": "Q2", "jif": 1.8},
    {"name": "Language & Communication", "type": "SSCI", "quartile": "Q2", "jif": 1.8},
    {"name": "Child Language Teaching & Therapy", "type": "SSCI", "quartile": "Q2", "jif": 1.7},
    {"name": "Language Acquisition", "type": "SSCI", "quartile": "Q2", "jif": 1.7},
    {"name": "Translation Studies", "type": "SSCI", "quartile": "Q2", "jif": 1.7},
    {"name": "Second Language Research", "type": "SSCI", "quartile": "Q2", "jif": 1.7},
    {"name": "Language Variation and Change", "type": "SSCI", "quartile": "Q2", "jif": 1.6},
    {"name": "English Teaching-Practice and Critique", "type": "SSCI", "quartile": "Q2", "jif": 1.6},
    {"name": "Journal of English Linguistics", "type": "SSCI", "quartile": "Q2", "jif": 1.6},
    {"name": "Language and Cognition", "type": "SSCI", "quartile": "Q2", "jif": 1.6},
    {"name": "Lingua", "type": "SSCI", "quartile": "Q2", "jif": 1.6},
    {"name": "International Journal of Speech-Language Pathology", "type": "SSCI", "quartile": "Q2", "jif": 1.6},
    {"name": "Natural Language Processing", "type": "SSCI", "quartile": "Q2", "jif": 1.6},
    {"name": "International Journal of Bilingualism", "type": "SSCI", "quartile": "Q2", "jif": 1.5},
    {"name": "Journal of Linguistic Anthropology", "type": "SSCI", "quartile": "Q2", "jif": 1.5},
    {"name": "Linguistics and Philosophy", "type": "SSCI", "quartile": "Q2", "jif": 1.5},
    {"name": "Target-International Journal of Translation Studies", "type": "SSCI", "quartile": "Q2", "jif": 1.5},
    {"name": "Linguistica Antverpiensia New Series-Themes in Translation Studies", "type": "SSCI", "quartile": "Q2", "jif": 1.5},
    {"name": "Journal of Neurolinguistics", "type": "SSCI", "quartile": "Q2", "jif": 1.5},
    {"name": "Intercultural Pragmatics", "type": "SSCI", "quartile": "Q2", "jif": 1.4},
    {"name": "Laboratory Phonology", "type": "SSCI", "quartile": "Q2", "jif": 1.4},
    {"name": "Iberica", "type": "SSCI", "quartile": "Q2", "jif": 1.4},
    {"name": "Australian Journal of Linguistics", "type": "SSCI", "quartile": "Q2", "jif": 1.4},
    {"name": "English World-Wide", "type": "SSCI", "quartile": "Q2", "jif": 1.3},
    {"name": "Gender and Language", "type": "SSCI", "quartile": "Q2", "jif": 1.3},
    {"name": "Diachronica", "type": "SSCI", "quartile": "Q2", "jif": 1.3},
    {"name": "Linguistics", "type": "SSCI", "quartile": "Q2", "jif": 1.3},
    {"name": "Syntax-A Journal of Theoretical Experimental and Interdisciplinary Research", "type": "SSCI", "quartile": "Q2", "jif": 1.3},
    {"name": "Linguistic Typology", "type": "SSCI", "quartile": "Q2", "jif": 1.2},
    {"name": "Multilingua-Journal of Cross-Cultural and Interlanguage Communication", "type": "SSCI", "quartile": "Q2", "jif": 1.2},
    {"name": "World Englishes", "type": "SSCI", "quartile": "Q2", "jif": 1.2},
    {"name": "Lexikos", "type": "SSCI", "quartile": "Q2", "jif": 1.2},
    {"name": "Perspectives-Studies in Translation Theory and Practice", "type": "SSCI", "quartile": "Q2", "jif": 1.2},
    {"name": "Language Matters", "type": "SSCI", "quartile": "Q2", "jif": 1.2},
    {"name": "Journal of East Asian Linguistics", "type": "SSCI", "quartile": "Q2", "jif": 1.2},
    {"name": "Translator", "type": "SSCI", "quartile": "Q2", "jif": 1.2},
    {"name": "Journal of Linguistics", "type": "SSCI", "quartile": "Q2", "jif": 1.1},
    {"name": "Linguistic Review", "type": "SSCI", "quartile": "Q2", "jif": 1.1},
    {"name": "Language Learning and Development", "type": "SSCI", "quartile": "Q2", "jif": 1.1},
    {"name": "Narrative Inquiry", "type": "SSCI", "quartile": "Q2", "jif": 1.1},
    {"name": "Clinical Linguistics & Phonetics", "type": "SSCI", "quartile": "Q2", "jif": 1.1},
    {"name": "Language and Speech", "type": "SSCI", "quartile": "Q2", "jif": 1.1},
    {"name": "Translation and Interpreting Studies", "type": "SSCI", "quartile": "Q2", "jif": 1.1},
    {"name": "Language Problems & Language Planning", "type": "SSCI", "quartile": "Q2", "jif": 1.1},
    {"name": "Digital Scholarship in The Humanities", "type": "SSCI", "quartile": "Q3", "jif": 1.0},
    {"name": "Journal of Quantitative Linguistics", "type": "SSCI", "quartile": "Q3", "jif": 1.0},
    {"name": "Gesture", "type": "SSCI", "quartile": "Q3", "jif": 1.0},
    {"name": "Probus", "type": "SSCI", "quartile": "Q3", "jif": 1.0},
    {"name": "Pragmatics & Cognition", "type": "SSCI", "quartile": "Q3", "jif": 1.0},
    {"name": "Terminology", "type": "SSCI", "quartile": "Q3", "jif": 1.0},
    {"name": "Journal of Semantics", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "Across Languages and Cultures", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "English Today", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "English Language & Linguistics", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "Topics in Language Disorders", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "Journal of French Language Studies", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "Phonetica", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "Glossa-A Journal of General Linguistics", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "Text & Talk", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "Canadian Modern Language Review", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "Interaction Studies", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "Revista Espanola De Linguistica Aplicada", "type": "SSCI", "quartile": "Q3", "jif": 0.9},
    {"name": "Hispania", "type": "SSCI", "quartile": "Q3", "jif": 0.8},
    {"name": "Natural Language & Linguistic Theory", "type": "SSCI", "quartile": "Q3", "jif": 0.8},
    {"name": "Linguistics Vanguard", "type": "SSCI", "quartile": "Q3", "jif": 0.8},
    {"name": "Journal of Historical Pragmatics", "type": "SSCI", "quartile": "Q3", "jif": 0.8},
    {"name": "Journal of The International Phonetic Association", "type": "SSCI", "quartile": "Q3", "jif": 0.8},
    {"name": "Theoretical Linguistics", "type": "SSCI", "quartile": "Q3", "jif": 0.8},
    {"name": "Functions of Language", "type": "SSCI", "quartile": "Q3", "jif": 0.8},
    {"name": "Natural Language Semantics", "type": "SSCI", "quartile": "Q3", "jif": 0.7},
    {"name": "Language and Literature", "type": "SSCI", "quartile": "Q3", "jif": 0.7},
    {"name": "Journal of African Languages and Linguistics", "type": "SSCI", "quartile": "Q3", "jif": 0.7},
    {"name": "Studies in Language", "type": "SSCI", "quartile": "Q3", "jif": 0.6},
    {"name": "Review of Cognitive Linguistics", "type": "SSCI", "quartile": "Q3", "jif": 0.6},
    {"name": "Folia Linguistica", "type": "SSCI", "quartile": "Q3", "jif": 0.6},
    {"name": "Names-A Journal of Onomastics", "type": "SSCI", "quartile": "Q3", "jif": 0.6},
    {"name": "Phonology", "type": "SSCI", "quartile": "Q3", "jif": 0.6},
    {"name": "Babel-Revue Internationale De La Traduction", "type": "SSCI", "quartile": "Q3", "jif": 0.6},
    {"name": "Spanish in Context", "type": "SSCI", "quartile": "Q3", "jif": 0.6},
    {"name": "Circulo De Linguistica Aplicada A La Comunicacion", "type": "SSCI", "quartile": "Q3", "jif": 0.6},
    {"name": "Revista Signos", "type": "SSCI", "quartile": "Q3", "jif": 0.6},
    {"name": "European Journal of English Studies", "type": "SSCI", "quartile": "Q3", "jif": 0.5},
    {"name": "Rilce-Revista De Filologia Hispanica", "type": "SSCI", "quartile": "Q3", "jif": 0.5},
    {"name": "American Speech", "type": "SSCI", "quartile": "Q3", "jif": 0.5},
    {"name": "Pragmatics", "type": "SSCI", "quartile": "Q3", "jif": 0.5},
    {"name": "Pragmatics and Society", "type": "SSCI", "quartile": "Q3", "jif": 0.5},
    {"name": "Nordic Journal of Linguistics", "type": "SSCI", "quartile": "Q3", "jif": 0.5},
    {"name": "Southern African Linguistics and Applied Language Studies", "type": "SSCI", "quartile": "Q3", "jif": 0.5},
    {"name": "Indogermanische Forschungen", "type": "SSCI", "quartile": "Q3", "jif": 0.5},
    {"name": "RLA-Revista De Linguistica Teorica Y Aplicada", "type": "SSCI", "quartile": "Q3", "jif": 0.5},
    {"name": "International Journal of American Linguistics", "type": "SSCI", "quartile": "Q3", "jif": 0.5},
    {"name": "Journal of Germanic Linguistics", "type": "SSCI", "quartile": "Q4", "jif": 0.4},
    {"name": "Poznan Studies in Contemporary Linguistics", "type": "SSCI", "quartile": "Q4", "jif": 0.4},
    {"name": "Journal of Pidgin and Creole Languages", "type": "SSCI", "quartile": "Q4", "jif": 0.4},
    {"name": "Dialectologia Et Geolinguistica", "type": "SSCI", "quartile": "Q4", "jif": 0.4},
    {"name": "Zeitschrift Fur Sprachwissenschaft", "type": "SSCI", "quartile": "Q4", "jif": 0.3},
    {"name": "Acta Linguistica Academica", "type": "SSCI", "quartile": "Q4", "jif": 0.3},
    {"name": "Slovo A Slovesnost", "type": "SSCI", "quartile": "Q4", "jif": 0.3},
    {"name": "Language and Linguistics", "type": "SSCI", "quartile": "Q4", "jif": 0.3},
    {"name": "Sintagma", "type": "SSCI", "quartile": "Q4", "jif": 0.3},
    {"name": "Onomazein", "type": "SSCI", "quartile": "Q4", "jif": 0.3},
    {"name": "Journal of Comparative Germanic Linguistics", "type": "SSCI", "quartile": "Q4", "jif": 0.2},
    {"name": "Language & History", "type": "SSCI", "quartile": "Q4", "jif": 0.2},
    {"name": "Atlantis-Journal of The Spanish Association of Anglo-American Studies", "type": "SSCI", "quartile": "Q4", "jif": 0.2},
    {"name": "Journal of Chinese Linguistics", "type": "SSCI", "quartile": "Q4", "jif": 0.2},
    {"name": "International Journal of Speech Language and The Law", "type": "SSCI", "quartile": "Q4", "jif": 0.2},
    {"name": "Estudios Filologicos", "type": "SSCI", "quartile": "Q4", "jif": 0.1},
    {"name": "Historiographia Linguistica", "type": "SSCI", "quartile": "Q4", "jif": 0.1},
    {"name": "Zeitschrift Fur Dialektologie Und Linguistik", "type": "SSCI", "quartile": "Q4", "jif": 0.1},
    {"name": "Revue Roumaine De Linguistique", "type": "SSCI", "quartile": "Q4", "jif": 0.1},
    {"name": "Langages", "type": "SSCI", "quartile": "Q4", "jif": 0.1},
    {"name": "Africana Linguistica", "type": "SSCI", "quartile": "Q4", "jif": 0.1},
]
