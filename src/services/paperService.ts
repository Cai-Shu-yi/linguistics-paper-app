import type { Paper, AIAnalysis } from '../types';
import { getApiKey } from './settingsService';

// API base URL - configurable for deployment
// When deployed, replace with your Railway/Render backend URL
const API_BASE = (typeof window !== 'undefined' && window.location.hostname === 'localhost')
  ? 'http://localhost:8000/api'
  : 'https://YOUR_BACKEND_URL/api';

const DEEPSEEK_API = 'https://api.deepseek.com/v1/chat/completions';

// Mock papers as fallback when API is unavailable
const MOCK_PAPERS: Paper[] = [
  {
    id: 'mock-1', title: 'The Role of Input Enhancement in L2 Vocabulary Acquisition: A Meta-Analysis',
    titleZh: '输入强化在二语词汇习得中的作用：一项元分析',
    authors: ['Wei Zhang', 'Xiaoming Li', 'Yu Chen'],
    journal: 'Studies in Second Language Acquisition', journalType: 'SSCI',
    jifQuartile: 'Q1', jif: 5.2, publishDate: '2026-07-02',
    doi: '10.1017/S0272263126000123',
    keywords: ['二语习得', '词汇习得', '输入强化', '元分析'],
    abstract: 'This meta-analysis synthesizes findings from 48 studies on the effectiveness of input enhancement techniques.',
    abstractZh: '本研究对48项关于输入强化技术在二语词汇习得中有效性的研究进行了元分析。',
    aiAnalysis: { summary: '该研究通过元分析方法系统回顾了48项关于输入强化在二语词汇习得中作用的研究...', methodology: '元分析法，纳入48项实证研究...', innovation: '首次系统性元分析', literatureReview: '梳理输入假说、注意假说相关理论', futureDirections: '关注交互效应和长期保持效果', generatedAt: '2026-07-03T10:00:00Z' },
  },
  {
    id: 'mock-2', title: 'Neural Correlates of Syntactic Processing in L1 and L2: An fMRI Study',
    titleZh: '一语和二语句法加工的神经关联：一项fMRI研究',
    authors: ['Jing Wang', 'Michael Johnson'],
    journal: 'Bilingualism-Language and Cognition', journalType: 'SSCI',
    jifQuartile: 'Q1', jif: 2.4, publishDate: '2026-07-01',
    doi: '10.1017/S1366728926000456',
    keywords: ['句法加工', '双语', 'fMRI', '神经语言学'],
    abstract: 'This fMRI study investigates the neural correlates of syntactic processing in both L1 and L2.',
    abstractZh: '本研究通过fMRI技术考察了晚期双语者一语和二语句法加工的神经关联。',
    aiAnalysis: { summary: '比较了晚期汉英双语者一语和二语句法加工脑激活模式...', methodology: '事件相关fMRI设计，30名被试...', innovation: '首次直接比较汉英双语者神经基础', literatureReview: '基于双语加工神经认知模型', futureDirections: '考察不同复杂度条件下的差异', generatedAt: '2026-07-03T10:00:00Z' },
  },
  {
    id: 'mock-3', title: '语料库驱动的汉语学术语篇立场标记语研究',
    titleZh: '语料库驱动的汉语学术语篇立场标记语研究',
    authors: ['李明', '张华', '王芳'],
    journal: '外语教学与研究', journalType: 'CSSCI',
    publishDate: '2026-06-28',
    keywords: ['学术语篇', '立场标记语', '语料库', '汉语学术写作'],
    abstract: '本研究基于自建的汉语学术论文语料库，考察了立场标记语在不同学科中的分布特征。',
    aiAnalysis: { summary: '基于百万词级汉语学术论文语料库分析立场标记语分布差异...', methodology: '语料库驱动方法，200篇CSSCI论文...', innovation: '构建汉语学术立场标记分类框架', literatureReview: 'Hyland(2005)、Biber(2006)理论框架', futureDirections: '扩大语料规模、历时研究', generatedAt: '2026-07-03T10:00:00Z' },
  },
  {
    id: 'mock-4', title: 'Translanguaging Practices in Multilingual Classrooms',
    titleZh: '多语课堂中的超语实践：教师视角与教学启示',
    authors: ['Elena Garcia', 'Robert Smith', 'Mei Liu'],
    journal: 'Applied Linguistics', journalType: 'SSCI',
    jifQuartile: 'Q1', jif: 3.9, publishDate: '2026-06-27',
    doi: '10.1093/applin/amac045',
    keywords: ['超语实践', '多语课堂', '教师认知', '教学策略'],
    abstract: 'Drawing on classroom observations and teacher interviews from 12 multilingual schools.',
    abstractZh: '基于三个国家12所多语学校的课堂观察和教师访谈。',
    aiAnalysis: { summary: '跨国比较的超语教学实践研究...', methodology: '多案例比较研究设计', innovation: '提出教师态度连续体模型', literatureReview: '超语理论发展脉络', futureDirections: '纵向研究追踪发展变化', generatedAt: '2026-07-03T10:00:00Z' },
  },
  {
    id: 'mock-5', title: '基于Transformer的汉英翻译质量自动评估模型研究',
    titleZh: '基于Transformer的汉英翻译质量自动评估模型研究',
    authors: ['刘洋', '陈思', '赵敏'],
    journal: '中国翻译', journalType: 'CSSCI',
    publishDate: '2026-06-25',
    keywords: ['翻译质量评估', 'Transformer', '汉英翻译', '自然语言处理'],
    abstract: '本文提出了一种基于改进Transformer架构的汉英翻译质量自动评估模型。',
    aiAnalysis: { summary: '基于改进Transformer的翻译质量评估模型...', methodology: 'TQA-Transformer架构', innovation: '句法依存信息融入评估', literatureReview: '翻译质量评估三个发展阶段', futureDirections: '扩展到更多语言对', generatedAt: '2026-07-03T10:00:00Z' },
  },
];

async function apiGet(path: string, params?: Record<string, string>): Promise<any> {
  try {
    const url = new URL(`${API_BASE}${path}`);
    if (params) {
      Object.entries(params).forEach(([k, v]) => { if (v) url.searchParams.set(k, v); });
    }
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch {
    return null;
  }
}

function mapPaper(raw: any): Paper {
  return {
    id: raw.id,
    title: raw.title || '',
    titleZh: raw.title_zh || undefined,
    authors: Array.isArray(raw.authors) ? raw.authors : (raw.authors || '').split(',').filter(Boolean),
    journal: raw.journal || '',
    journalType: raw.journal_type || 'SSCI',
    jifQuartile: raw.jif_quartile || undefined,
    jif: raw.jif || undefined,
    publishDate: raw.publish_date || '',
    doi: raw.doi || undefined,
    url: raw.url || undefined,
    keywords: Array.isArray(raw.keywords) ? raw.keywords : (raw.keywords || '').split(',').filter(Boolean),
    abstract: raw.abstract || undefined,
    abstractZh: raw.abstract_zh || undefined,
    aiAnalysis: raw.aiAnalysis || undefined,
  };
}

export async function fetchPapers(keywords?: string[]): Promise<Paper[]> {
  const params: Record<string, string> = {};
  if (keywords && keywords.length > 0) {
    params.keywords = keywords.join(',');
  }
  const data = await apiGet('/papers', params);
  if (data && data.papers && data.papers.length > 0) {
    return data.papers.map(mapPaper);
  }
  // Fallback to mock
  if (!keywords || keywords.length === 0) return MOCK_PAPERS;
  return MOCK_PAPERS.filter(p =>
    keywords.some(kw =>
      p.keywords.some(pk => pk.includes(kw)) ||
      p.title.toLowerCase().includes(kw.toLowerCase()) ||
      (p.titleZh && p.titleZh.includes(kw)) ||
      (p.abstract && p.abstract.toLowerCase().includes(kw.toLowerCase()))
    )
  );
}

export async function searchPapers(query: string): Promise<Paper[]> {
  if (!query.trim()) {
    const data = await apiGet('/papers');
    if (data && data.papers && data.papers.length > 0) return data.papers.map(mapPaper);
    return MOCK_PAPERS;
  }
  const data = await apiGet('/papers', { search: query });
  if (data && data.papers && data.papers.length > 0) return data.papers.map(mapPaper);
  // Fallback
  const q = query.toLowerCase();
  return MOCK_PAPERS.filter(p =>
    p.title.toLowerCase().includes(q) ||
    (p.titleZh && p.titleZh.includes(q)) ||
    p.authors.some(a => a.toLowerCase().includes(q)) ||
    p.journal.toLowerCase().includes(q) ||
    p.keywords.some(k => k.includes(q)) ||
    (p.abstract && p.abstract.toLowerCase().includes(q))
  );
}

export async function triggerFetch(keywords?: string[]): Promise<{ found: number; new: number }> {
  const params: Record<string, string> = {};
  if (keywords && keywords.length > 0) params.keywords = keywords.join(',');
  const data = await apiGet('/papers/fetch', params);
  return data || { found: 0, new: 0 };
}

export async function fetchStats(): Promise<any> {
  return await apiGet('/stats') || { total: 0, cssci: 0, ssci: 0, q1: 0, journals: 212 };
}

// =========== DeepSeek AI Integration ===========

const AI_PROMPT_TEMPLATE = `你是一位资深语言学研究者，请对以下论文进行专业、深入的分析。用中文回复，结构清晰。

论文标题：{title}
英文摘要：{abstract}
作者：{authors}
期刊：{journal}
关键词：{keywords}

请按以下五个维度进行分析，每个维度200-400字：

## 研究摘要
用简洁的中文概括这篇论文的研究问题、方法和主要发现。

## 方法论
分析研究采用的方法论，包括研究设计、数据来源、分析方法等。

## 创新点
指出该研究的核心创新之处和学术贡献。

## 文献综述要点
梳理研究引用的主要理论框架和文献脉络。

## 后续研究方向
基于本文发现，推测未来可延伸的研究方向。

请严格按照以下JSON格式回复（不要包含代码块标记）：
{
  "summary": "...",
  "methodology": "...",
  "innovation": "...",
  "literatureReview": "...",
  "futureDirections": "..."
}`;

export async function analyzeWithAI(paper: Paper): Promise<AIAnalysis | null> {
  const apiKey = getApiKey();
  if (!apiKey) return null;

  const prompt = AI_PROMPT_TEMPLATE
    .replace('{title}', paper.title || '')
    .replace('{abstract}', paper.abstract || '无')
    .replace('{authors}', paper.authors.join(', '))
    .replace('{journal}', `${paper.journal} (${paper.journalType}${paper.jifQuartile ? ` ${paper.jifQuartile}` : ''})`)
    .replace('{keywords}', paper.keywords.join('、'));

  try {
    const res = await fetch(DEEPSEEK_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: '你是一位资深语言学研究者，擅长分析学术论文。请严格按照JSON格式回复。' },
          { role: 'user', content: prompt },
        ],
        temperature: 0.7,
        max_tokens: 4096,
        response_format: { type: 'json_object' },
      }),
    });

    if (!res.ok) throw new Error(`DeepSeek API error: ${res.status}`);

    const data = await res.json();
    const content = data.choices?.[0]?.message?.content;
    if (!content) return null;

    const parsed = JSON.parse(content);
    return {
      summary: parsed.summary || '',
      methodology: parsed.methodology || '',
      innovation: parsed.innovation || '',
      literatureReview: parsed.literatureReview || '',
      futureDirections: parsed.futureDirections || '',
      generatedAt: new Date().toISOString(),
    };
  } catch (err) {
    console.error('DeepSeek AI analysis failed:', err);
    return null;
  }
}
