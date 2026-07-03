import type { AppSettings } from '../types';

const SETTINGS_KEY = 'linguistics-paper-settings';

const defaultSettings: AppSettings = {
  deepseekApiKey: '',
  keywords: ['二语习得', '语料库', '翻译', '句法', '语义', '语用', '认知语言学'],
};

export function getSettings(): AppSettings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (raw) {
      return { ...defaultSettings, ...JSON.parse(raw) };
    }
  } catch {}
  return defaultSettings;
}

export function saveSettings(settings: AppSettings): void {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

export function getApiKey(): string {
  return getSettings().deepseekApiKey;
}

export function getKeywords(): string[] {
  return getSettings().keywords;
}
