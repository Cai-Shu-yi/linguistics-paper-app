/**
 * PDF and Word export services for paper analysis reports.
 */
import type { Paper } from '../types';

function buildReportHTML(paper: Paper): string {
  const a = paper.aiAnalysis;
  const dateStr = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>论文分析报告 - ${paper.titleZh || paper.title}</title>
<style>
  body { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; color: #3E2A1A; line-height: 1.8; max-width: 800px; margin: 0 auto; padding: 40px 20px; background: #fff; }
  .header { border-bottom: 2px solid #E8843A; padding-bottom: 20px; margin-bottom: 24px; }
  .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; margin-right: 8px; background: #FDE8D4; color: #B5651D; }
  .title { font-size: 20px; font-weight: 600; margin: 12px 0 8px; color: #3E2A1A; }
  .meta { font-size: 13px; color: #8B7355; margin-bottom: 4px; }
  .section { margin: 24px 0; }
  .section h2 { font-size: 16px; color: #E8843A; border-left: 3px solid #E8843A; padding-left: 10px; margin-bottom: 8px; }
  .section p { font-size: 14px; color: #3E2A1A; text-indent: 2em; }
  .footer { margin-top: 40px; padding-top: 16px; border-top: 1px solid #E8D5C0; font-size: 12px; color: #8B7355; text-align: center; }
  @media print { body { padding: 20px; } }
</style>
</head>
<body>

<div class="header">
  <div>
    <span class="badge">${paper.journalType}</span>
    ${paper.jifQuartile ? `<span class="badge">${paper.jifQuartile}</span>` : ''}
    ${paper.jif ? `<span class="badge">JIF ${paper.jif}</span>` : ''}
  </div>
  <h1 class="title">${paper.titleZh || paper.title}</h1>
  ${paper.journalType === 'SSCI' && paper.titleZh ? `<p class="meta" style="font-size:14px; color:#8B7355;">${paper.title}</p>` : ''}
  <p class="meta">作者：${paper.authors.join('、')}</p>
  <p class="meta">期刊：${paper.journal} | 发表日期：${paper.publishDate}</p>
  ${paper.doi ? `<p class="meta">DOI: ${paper.doi}</p>` : ''}
  <p class="meta">关键词：${paper.keywords.join('、')}</p>
</div>

${a ? `
<div class="section">
  <h2>研究摘要</h2>
  <p>${a.summary}</p>
</div>
<div class="section">
  <h2>方法论</h2>
  <p>${a.methodology}</p>
</div>
<div class="section">
  <h2>创新点</h2>
  <p>${a.innovation}</p>
</div>
<div class="section">
  <h2>文献综述要点</h2>
  <p>${a.literatureReview}</p>
</div>
<div class="section">
  <h2>后续研究方向</h2>
  <p>${a.futureDirections}</p>
</div>
` : paper.abstract ? `
<div class="section">
  <h2>英文摘要</h2>
  <p>${paper.abstract}</p>
</div>
${paper.abstractZh ? `<div class="section"><h2>中文摘要</h2><p>${paper.abstractZh}</p></div>` : ''}
` : ''}

<div class="footer">
  由语言学论文速递生成 | ${dateStr}
</div>

</body>
</html>`;
}

export function downloadPDF(paper: Paper): void {
  const html = buildReportHTML(paper);
  const blob = new Blob([html], { type: 'text/html' });

  // Open in new window for print-to-PDF
  const w = window.open('', '_blank');
  if (!w) return;
  w.document.write(html);
  w.document.close();
  w.focus();
  // Auto-trigger print dialog
  setTimeout(() => w.print(), 500);
}

export function downloadWord(paper: Paper): void {
  const html = buildReportHTML(paper);
  // Word can open HTML files with .doc extension
  const blob = new Blob(['\ufeff' + html], { type: 'application/msword' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const filename = `论文分析_${(paper.titleZh || paper.title).slice(0, 30)}.doc`;
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
