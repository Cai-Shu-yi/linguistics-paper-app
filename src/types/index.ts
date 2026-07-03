export interface Paper {
  id: string;
  title: string;
  titleZh?: string;
  authors: string[];
  journal: string;
  journalType: 'CSSCI' | 'SSCI';
  jifQuartile?: 'Q1' | 'Q2' | 'Q3' | 'Q4';
  jif?: number;
  publishDate: string;
  doi?: string;
  url?: string;
  keywords: string[];
  abstract?: string;
  abstractZh?: string;
  aiAnalysis?: AIAnalysis;
}

export interface AIAnalysis {
  summary: string;
  methodology: string;
  innovation: string;
  literatureReview: string;
  futureDirections: string;
  generatedAt: string;
}

export interface JournalInfo {
  name: string;
  type: 'CSSCI' | 'SSCI';
  quartile?: 'Q1' | 'Q2' | 'Q3' | 'Q4';
  jif?: number;
}

export interface AppSettings {
  deepseekApiKey: string;
  keywords: string[];
}
