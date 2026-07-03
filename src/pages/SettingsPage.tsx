import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { getSettings, saveSettings } from '../services/settingsService';
import type { AppSettings } from '../types';

export default function SettingsPage() {
  const navigate = useNavigate();
  const [apiKey, setApiKey] = useState('');
  const [keywordsInput, setKeywordsInput] = useState('');
  const [saved, setSaved] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'fail' | null>(null);

  useEffect(() => {
    const s = getSettings();
    setApiKey(s.deepseekApiKey);
    setKeywordsInput(s.keywords.join('、'));
  }, []);

  const handleSave = () => {
    const keywords = keywordsInput
      .split(/[、，,\s]+/)
      .map(k => k.trim())
      .filter(k => k.length > 0);

    const settings: AppSettings = { deepseekApiKey: apiKey.trim(), keywords };
    saveSettings(settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleTestKey = async () => {
    if (!apiKey.trim()) return;
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch('https://api.deepseek.com/v1/models', {
        headers: { Authorization: `Bearer ${apiKey.trim()}` },
      });
      setTestResult(res.ok ? 'success' : 'fail');
    } catch {
      setTestResult('fail');
    }
    setTesting(false);
  };

  return (
    <div className="min-h-screen bg-[var(--color-warm-bg)]">
      <Header />

      <main className="max-w-xl mx-auto px-4 pt-6 pb-16">
        <h2 className="text-[15px] font-medium text-[var(--color-warm-text)] mb-5">设置</h2>

        {/* API Key Section */}
        <div className="bg-white rounded-xl border border-[var(--color-warm-accent-light)] p-5 mb-4">
          <h3 className="text-[14px] font-medium text-[var(--color-warm-text)] mb-1.5">
            DeepSeek API Key
          </h3>
          <p className="text-[12px] text-[var(--color-warm-text-muted)] mb-3 leading-relaxed">
            用于 AI 论文解读。你的 Key 仅存储在浏览器本地，不会上传到任何服务器。
            <a
              href="https://platform.deepseek.com/api_keys"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--color-warm-primary)] hover:underline ml-1"
            >
              获取 API Key
            </a>
          </p>
          <div className="flex gap-2">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => { setApiKey(e.target.value); setTestResult(null); }}
              placeholder="sk-..."
              className="flex-1 px-3 py-2 rounded-lg bg-[var(--color-warm-surface)] border border-[var(--color-warm-accent-light)] text-[13px] text-[var(--color-warm-text)] placeholder:text-[var(--color-warm-text-muted)] focus:outline-none focus:border-[var(--color-warm-primary)] transition-colors"
            />
            <button
              onClick={handleTestKey}
              disabled={!apiKey.trim() || testing}
              className="px-3 py-2 rounded-lg border border-[var(--color-warm-accent-light)] text-[13px] text-[var(--color-warm-text-muted)] hover:bg-[var(--color-warm-surface)] disabled:opacity-40 transition-colors whitespace-nowrap"
            >
              {testing ? '检测中...' : '测试'}
            </button>
          </div>
          {testResult === 'success' && (
            <p className="text-[12px] text-green-600 mt-2">密钥有效，连接成功</p>
          )}
          {testResult === 'fail' && (
            <p className="text-[12px] text-red-500 mt-2">密钥无效或网络异常</p>
          )}
        </div>

        {/* Keywords Section */}
        <div className="bg-white rounded-xl border border-[var(--color-warm-accent-light)] p-5 mb-6">
          <h3 className="text-[14px] font-medium text-[var(--color-warm-text)] mb-1.5">
            关注关键词
          </h3>
          <p className="text-[12px] text-[var(--color-warm-text-muted)] mb-3 leading-relaxed">
            用顿号或逗号分隔，系统将从目标期刊中筛选匹配的论文
          </p>
          <textarea
            value={keywordsInput}
            onChange={(e) => setKeywordsInput(e.target.value)}
            rows={3}
            placeholder="例如：二语习得、语料库语言学、翻译研究、句法学..."
            className="w-full px-3 py-2 rounded-lg bg-[var(--color-warm-surface)] border border-[var(--color-warm-accent-light)] text-[13px] text-[var(--color-warm-text)] placeholder:text-[var(--color-warm-text-muted)] focus:outline-none focus:border-[var(--color-warm-primary)] transition-colors resize-none"
          />
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          className="w-full py-2.5 rounded-xl bg-[var(--color-warm-primary)] text-white text-[14px] font-medium hover:bg-[var(--color-warm-primary-hover)] transition-colors"
        >
          {saved ? '已保存' : '保存设置'}
        </button>

        {/* Security Notice */}
        <p className="text-[12px] text-[var(--color-warm-text-muted)] text-center mt-4 leading-relaxed">
          你的 API Key 和关键词仅存储在浏览器本地（localStorage），
          不会上传到任何服务器。
        </p>
      </main>
    </div>
  );
}
