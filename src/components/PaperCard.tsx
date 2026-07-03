import { useState } from 'react';
import type { Paper, AIAnalysis } from '../types';
import { analyzeWithAI } from '../services/paperService';
import { getApiKey } from '../services/settingsService';
import { downloadPDF, downloadWord } from '../services/exportService';

interface PaperCardProps {
  paper: Paper;
  expanded: boolean;
  onToggle: () => void;
  onAnalysisReady?: (paperId: string, analysis: AIAnalysis) => void;
}

export default function PaperCard({ paper, expanded, onToggle, onAnalysisReady }: PaperCardProps) {
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(paper.aiAnalysis || null);
  const [error, setError] = useState('');

  const hasApiKey = !!getApiKey();

  const handleAnalyze = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (analyzing) return;
    setAnalyzing(true);
    setError('');

    const result = await analyzeWithAI(paper);
    if (result) {
      setAnalysis(result);
      onAnalysisReady?.(paper.id, result);
    } else {
      setError('AI 分析失败，请检查 API Key 或网络连接');
    }
    setAnalyzing(false);
  };

  const displayAnalysis = analysis || paper.aiAnalysis;

  const handleDownloadPDF = (e: React.MouseEvent) => {
    e.stopPropagation();
    downloadPDF({ ...paper, aiAnalysis: displayAnalysis || undefined });
  };

  const handleDownloadWord = (e: React.MouseEvent) => {
    e.stopPropagation();
    downloadWord({ ...paper, aiAnalysis: displayAnalysis || undefined });
  };

  return (
    <div className="bg-[var(--color-warm-card)] rounded-xl border border-[var(--color-warm-accent-light)] overflow-hidden transition-all duration-300 hover:border-[var(--color-warm-accent)]">
      {/* Header */}
      <div className="p-4 sm:p-5 cursor-pointer" onClick={onToggle}>
        <div className="flex flex-wrap items-center gap-2 mb-2">
          <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
            paper.journalType === 'CSSCI'
              ? 'bg-[var(--color-warm-primary-light)] text-[var(--color-warm-brown)]'
              : 'bg-[var(--color-warm-accent-light)] text-[var(--color-warm-brown-dark)]'
          }`}>
            {paper.journalType}
          </span>
          {paper.jifQuartile && (
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-white border border-[var(--color-warm-accent-light)] text-[var(--color-warm-text-muted)]">
              {paper.jifQuartile}
            </span>
          )}
          {paper.jif && (
            <span className="text-xs text-[var(--color-warm-text-muted)]">JIF {paper.jif}</span>
          )}
          <span className="text-xs text-[var(--color-warm-text-muted)] ml-auto">{paper.publishDate}</span>
        </div>

        <h3 className="text-[15px] font-medium text-[var(--color-warm-text)] leading-relaxed mb-1.5 font-[var(--font-serif)]">
          {paper.titleZh || paper.title}
        </h3>
        {paper.journalType === 'SSCI' && paper.titleZh && (
          <p className="text-[13px] text-[var(--color-warm-text-muted)] mb-1.5 leading-relaxed">{paper.title}</p>
        )}
        <div className="flex flex-wrap items-center gap-1.5 mb-2">
          {paper.authors.map((author, i) => (
            <span key={i} className="text-[13px] text-[var(--color-warm-text-muted)]">
              {author}{i < paper.authors.length - 1 ? '、' : ''}
            </span>
          ))}
        </div>
        <p className="text-[13px] text-[var(--color-warm-accent)] italic">{paper.journal}</p>

        <div className="flex flex-wrap gap-1.5 mt-2.5">
          {paper.keywords.slice(0, 5).map((kw) => (
            <span key={kw} className="text-xs px-2 py-0.5 rounded-full bg-[var(--color-warm-tag-bg)] text-[var(--color-warm-tag-text)]">#{kw}</span>
          ))}
        </div>
      </div>

      {/* Expanded Analysis */}
      {expanded && (
        <div className="border-t border-[var(--color-warm-accent-light)] bg-[var(--color-warm-surface)]">
          <div className="p-4 sm:p-5">
            {displayAnalysis ? (
              <div className="space-y-4">
                <AnalysisSection title="研究摘要" content={displayAnalysis.summary} />
                <AnalysisSection title="方法论" content={displayAnalysis.methodology} />
                <AnalysisSection title="创新点" content={displayAnalysis.innovation} />
                <AnalysisSection title="文献综述要点" content={displayAnalysis.literatureReview} />
                <AnalysisSection title="后续研究方向" content={displayAnalysis.futureDirections} />
              </div>
            ) : (
              <div className="text-center py-6">
                {hasApiKey ? (
                  <div>
                    <p className="text-[13px] text-[var(--color-warm-text-muted)] mb-3">
                      该论文尚未进行 AI 分析
                    </p>
                    {analyzing ? (
                      <div className="flex items-center justify-center gap-2 text-[var(--color-warm-primary)]">
                        <div className="w-4 h-4 border-2 border-[var(--color-warm-accent-light)] border-t-[var(--color-warm-primary)] rounded-full animate-spin" />
                        <span className="text-[13px]">AI 正在分析中...</span>
                      </div>
                    ) : (
                      <button
                        onClick={handleAnalyze}
                        disabled={analyzing}
                        className="px-4 py-2 rounded-lg bg-[var(--color-warm-primary)] text-white text-[13px] hover:bg-[var(--color-warm-primary-hover)] transition-colors"
                      >
                        AI 分析此论文
                      </button>
                    )}
                    {error && <p className="text-[12px] text-red-500 mt-2">{error}</p>}
                  </div>
                ) : (
                  <div className="text-[13px] text-[var(--color-warm-text-muted)]">
                    <p>需要配置 DeepSeek API Key 才能使用 AI 分析</p>
                    <a href="/settings" onClick={(e) => e.stopPropagation()} className="text-[var(--color-warm-primary)] hover:underline mt-1 inline-block">
                      前往设置
                    </a>
                  </div>
                )}
              </div>
            )}

            {/* Links and download */}
            <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-[var(--color-warm-accent-light)] mt-4">
              {paper.doi && (
                <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="text-[12px] text-[var(--color-warm-primary)] hover:text-[var(--color-warm-primary-hover)] underline underline-offset-2 flex items-center gap-1">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                  DOI
                </a>
              )}

              {displayAnalysis && (
                <>
                  <div className="w-px h-4 bg-[var(--color-warm-accent-light)]" />
                  <button onClick={handleDownloadPDF}
                    className="text-[12px] text-[var(--color-warm-text-muted)] hover:text-[var(--color-warm-primary)] transition-colors flex items-center gap-1">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="14" x2="12" y2="18"/><polyline points="9 16 12 14 15 16"/></svg>
                    下载 PDF
                  </button>
                  <button onClick={handleDownloadWord}
                    className="text-[12px] text-[var(--color-warm-text-muted)] hover:text-[var(--color-warm-primary)] transition-colors flex items-center gap-1">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    下载 Word
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Expand indicator */}
      <div className="flex justify-center pb-1 cursor-pointer" onClick={onToggle}>
        <svg className={`w-5 h-5 text-[var(--color-warm-text-muted)] transition-transform duration-300 ${expanded ? 'rotate-180' : ''}`}
          fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path d="M6 9l6 6 6-6"/>
        </svg>
      </div>
    </div>
  );
}

function AnalysisSection({ title, content }: { title: string; content: string }) {
  return (
    <div>
      <h4 className="text-[13px] font-medium text-[var(--color-warm-brown)] mb-1.5">{title}</h4>
      <p className="text-[13px] text-[var(--color-warm-text)] leading-relaxed">{content}</p>
    </div>
  );
}
