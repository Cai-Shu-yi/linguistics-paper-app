import { useState, useEffect, useCallback } from 'react';
import Header from '../components/Header';
import PaperCard from '../components/PaperCard';
import { fetchPapers, searchPapers } from '../services/paperService';
import { getSettings } from '../services/settingsService';
import type { Paper, AIAnalysis } from '../types';

export default function HomePage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showKeywords, setShowKeywords] = useState(false);

  const settings = getSettings();

  const loadPapers = useCallback(async () => {
    setLoading(true);
    const data = await fetchPapers(settings.keywords);
    setPapers(data);
    setLoading(false);
  }, [settings.keywords]);

  useEffect(() => {
    loadPapers();
  }, [loadPapers]);

  const handleSearch = useCallback(async (query: string) => {
    setSearchQuery(query);
    setLoading(true);
    const data = await searchPapers(query);
    setPapers(data);
    setLoading(false);
  }, []);

  const handleClearSearch = () => {
    setSearchQuery('');
    loadPapers();
  };

  const handleAnalysisReady = (paperId: string, analysis: AIAnalysis) => {
    setPapers(prev => prev.map(p =>
      p.id === paperId ? { ...p, aiAnalysis: analysis } : p
    ));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      handleClearSearch();
    }
  };

  return (
    <div className="min-h-screen bg-[var(--color-warm-bg)]">
      <Header />

      <main className="max-w-3xl mx-auto px-4 pb-16">
        {/* Search Section */}
        <div className="pt-6 pb-4">
          <div className="relative">
            <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--color-warm-text-muted)]">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
              </svg>
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="搜索语言学论文关键词、作者、期刊..."
              className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-white border border-[var(--color-warm-accent-light)] text-[14px] text-[var(--color-warm-text)] placeholder:text-[var(--color-warm-text-muted)] placeholder:text-[13px] focus:outline-none focus:border-[var(--color-warm-primary)] focus:ring-2 focus:ring-[var(--color-warm-primary-light)] transition-all"
            />
            {searchQuery && (
              <button
                onClick={handleClearSearch}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[var(--color-warm-text-muted)] hover:text-[var(--color-warm-text)] transition-colors"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            )}
          </div>

          {/* Active keywords */}
          <div className="mt-3">
            <button
              onClick={() => setShowKeywords(!showKeywords)}
              className="text-[12px] text-[var(--color-warm-text-muted)] hover:text-[var(--color-warm-text)] transition-colors flex items-center gap-1"
            >
              <svg className={`w-3 h-3 transition-transform ${showKeywords ? 'rotate-90' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6"/></svg>
              关注关键词 ({settings.keywords.length})
            </button>
            {showKeywords && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {settings.keywords.map((kw) => (
                  <button
                    key={kw}
                    onClick={() => handleSearch(kw)}
                    className="text-xs px-2.5 py-1 rounded-full bg-[var(--color-warm-tag-bg)] text-[var(--color-warm-tag-text)] hover:bg-[var(--color-warm-primary-light)] transition-colors"
                  >
                    #{kw}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Results */}
        <div className="space-y-3">
          {!loading && (
            <p className="text-[13px] text-[var(--color-warm-text-muted)] px-1">
              {searchQuery
                ? `找到 ${papers.length} 篇相关论文`
                : `今日更新 · ${new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' })}`}
            </p>
          )}

          {loading ? (
            <div className="flex flex-col items-center py-16 text-[var(--color-warm-text-muted)]">
              <div className="w-8 h-8 border-2 border-[var(--color-warm-accent-light)] border-t-[var(--color-warm-primary)] rounded-full animate-spin mb-3" />
              <p className="text-[13px]">正在加载论文...</p>
            </div>
          ) : papers.length === 0 ? (
            <div className="flex flex-col items-center py-16 text-[var(--color-warm-text-muted)]">
              <svg className="w-12 h-12 mb-3 text-[var(--color-warm-accent-light)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
              </svg>
              <p className="text-[14px]">没有找到相关论文</p>
              <p className="text-[13px] mt-1">试试其他关键词？</p>
            </div>
          ) : (
            papers.map((paper) => (
              <PaperCard
                key={paper.id}
                paper={paper}
                expanded={expandedId === paper.id}
                onToggle={() => setExpandedId(expandedId === paper.id ? null : paper.id)}
                onAnalysisReady={handleAnalysisReady}
              />
            ))
          )}
        </div>
      </main>
    </div>
  );
}
