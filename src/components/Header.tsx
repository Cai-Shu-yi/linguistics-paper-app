import { Link, useLocation } from 'react-router-dom';

export default function Header() {
  const location = useLocation();
  const isSettings = location.pathname === '/settings';

  return (
    <header className="sticky top-0 z-10 bg-[var(--color-warm-bg)]/95 backdrop-blur-sm border-b border-[var(--color-warm-accent-light)]">
      <div className="max-w-3xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 no-underline">
          <div className="w-8 h-8 rounded-lg bg-[var(--color-warm-primary)] flex items-center justify-center">
            <span className="text-white text-sm font-medium">语</span>
          </div>
          <div className="flex flex-col leading-none">
            <span className="text-[15px] font-medium text-[var(--color-warm-text)]">语言学论文速递</span>
            <span className="text-[11px] text-[var(--color-warm-text-muted)]">CSSCI · SSCI</span>
          </div>
        </Link>

        <Link
          to={isSettings ? '/' : '/settings'}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[13px] transition-colors ${
            isSettings
              ? 'bg-[var(--color-warm-primary)] text-white hover:bg-[var(--color-warm-primary-hover)]'
              : 'text-[var(--color-warm-text-muted)] hover:text-[var(--color-warm-text)] hover:bg-[var(--color-warm-surface)]'
          }`}
        >
          {isSettings ? (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
              返回首页
            </>
          ) : (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              设置
            </>
          )}
        </Link>
      </div>
    </header>
  );
}
