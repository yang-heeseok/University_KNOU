#!/usr/bin/env node

/**
 * 학습 아카이브 문서 빌드 스크립트
 * Markdown 파일들을 HTML로 변환하여 정적 사이트 생성
 */

const fs = require('fs-extra');
const path = require('path');
const glob = require('glob');
const MarkdownIt = require('markdown-it');
const anchor = require('markdown-it-anchor');
const toc = require('markdown-it-table-of-contents');
const hljs = require('highlight.js');
const matter = require('gray-matter');
const moment = require('moment');

// Markdown 파서 설정
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value;
      } catch (__) { }
    }
    return '';
  }
})
  .use(anchor, {
    permalink: anchor.permalink.headerLink()
  })
  .use(toc, {
    includeLevel: [1, 2, 3, 4],
    containerClass: 'table-of-contents'
  });

// 설정
const config = {
  sourceDir: '.',
  outputDir: 'dist',
  templateDir: 'templates',
  excludePatterns: [
    'node_modules/**',
    'dist/**',
    '.git/**',
    'automation/**',
    '.github/**'
  ]
};

// HTML 템플릿
const htmlTemplate = `
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} - 방송통신대학교 학습 아카이브</title>
    <meta name="description" content="{{description}}">
    <link rel="stylesheet" href="/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="nav-container">
                <a href="/" class="nav-logo">🎓 KNOU Archive</a>
                <ul class="nav-menu">
                    <li><a href="/subjects/">과목</a></li>
                    <li><a href="/research/">연구</a></li>
                    <li><a href="/code-examples/">코드</a></li>
                    <li><a href="/resources/">자료</a></li>
                </ul>
            </div>
        </nav>
    </header>
    
    <main class="main">
        <div class="container">
            {{breadcrumb}}
            <article class="content">
                {{content}}
            </article>
            {{sidebar}}
        </div>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 방송통신대학교 학습 아카이브. 
               <a href="https://github.com/your-username/University_KNOU">GitHub</a>에서 소스 보기</p>
            <p>마지막 업데이트: {{lastModified}}</p>
        </div>
    </footer>
    
    <script src="/script.js"></script>
</body>
</html>
`;

// CSS 스타일
const cssContent = `
:root {
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --background-color: #f8fafc;
  --text-color: #1e293b;
  --border-color: #e2e8f0;
  --code-bg: #f1f5f9;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
  color: var(--text-color);
  background-color: var(--background-color);
}

.header {
  background: white;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.nav-logo {
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  color: var(--primary-color);
}

.nav-menu {
  display: flex;
  list-style: none;
  gap: 2rem;
}

.nav-menu a {
  text-decoration: none;
  color: var(--text-color);
  font-weight: 500;
  transition: color 0.2s;
}

.nav-menu a:hover {
  color: var(--primary-color);
}

.main {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.container {
  display: grid;
  grid-template-columns: 1fr 250px;
  gap: 2rem;
}

.content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.content h1 {
  color: var(--primary-color);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--border-color);
}

.content h2, .content h3, .content h4 {
  margin: 1.5rem 0 1rem 0;
  color: var(--text-color);
}

.content p {
  margin-bottom: 1rem;
}

.content ul, .content ol {
  margin: 1rem 0;
  padding-left: 2rem;
}

.content li {
  margin-bottom: 0.5rem;
}

.content code {
  background: var(--code-bg);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
}

.content pre {
  background: var(--code-bg);
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1rem 0;
}

.content pre code {
  background: none;
  padding: 0;
}

.content blockquote {
  border-left: 4px solid var(--primary-color);
  padding-left: 1rem;
  margin: 1rem 0;
  font-style: italic;
  color: var(--secondary-color);
}

.content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.content th, .content td {
  border: 1px solid var(--border-color);
  padding: 0.5rem;
  text-align: left;
}

.content th {
  background: var(--code-bg);
  font-weight: 600;
}

.sidebar {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  height: fit-content;
  position: sticky;
  top: 80px;
}

.table-of-contents {
  margin-bottom: 2rem;
}

.table-of-contents ul {
  list-style: none;
  padding-left: 0;
}

.table-of-contents li {
  margin-bottom: 0.5rem;
}

.table-of-contents a {
  text-decoration: none;
  color: var(--secondary-color);
  font-size: 0.9rem;
}

.table-of-contents a:hover {
  color: var(--primary-color);
}

.breadcrumb {
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: var(--secondary-color);
}

.breadcrumb a {
  color: var(--primary-color);
  text-decoration: none;
}

.footer {
  background: white;
  border-top: 1px solid var(--border-color);
  padding: 2rem 0;
  margin-top: 4rem;
  text-align: center;
  color: var(--secondary-color);
  font-size: 0.9rem;
}

.footer a {
  color: var(--primary-color);
  text-decoration: none;
}

@media (max-width: 768px) {
  .container {
    grid-template-columns: 1fr;
  }
  
  .nav-menu {
    display: none;
  }
  
  .content {
    padding: 1rem;
  }
}
`;

// JavaScript 코드
const jsContent = `
// 목차 스크롤 하이라이트
document.addEventListener('DOMContentLoaded', function() {
  const tocLinks = document.querySelectorAll('.table-of-contents a');
  const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
  
  function highlightTocLink() {
    let current = '';
    headings.forEach(heading => {
      const rect = heading.getBoundingClientRect();
      if (rect.top <= 100) {
        current = heading.id;
      }
    });
    
    tocLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === '#' + current) {
        link.classList.add('active');
      }
    });
  }
  
  window.addEventListener('scroll', highlightTocLink);
  highlightTocLink();
});

// 코드 복사 기능
document.querySelectorAll('pre code').forEach(block => {
  const button = document.createElement('button');
  button.className = 'copy-button';
  button.textContent = '복사';
  button.onclick = () => {
    navigator.clipboard.writeText(block.textContent);
    button.textContent = '복사됨!';
    setTimeout(() => button.textContent = '복사', 2000);
  };
  block.parentNode.appendChild(button);
});
`;

async function buildDocs() {
  console.log('📚 학습 아카이브 빌드 시작...');

  try {
    // 출력 디렉토리 정리
    await fs.emptyDir(config.outputDir);

    // 정적 파일 복사
    await fs.writeFile(path.join(config.outputDir, 'style.css'), cssContent);
    await fs.writeFile(path.join(config.outputDir, 'script.js'), jsContent);

    // Markdown 파일 찾기
    const markdownFiles = glob.sync('**/*.md', {
      ignore: config.excludePatterns
    });

    console.log(`📄 ${markdownFiles.length}개의 Markdown 파일 발견`);

    // 각 파일 처리
    for (const file of markdownFiles) {
      await processMarkdownFile(file);
    }

    // 인덱스 페이지 생성
    await generateIndexPage();

    console.log('✅ 빌드 완료!');
    console.log(`📁 출력 디렉토리: ${config.outputDir}`);

  } catch (error) {
    console.error('❌ 빌드 실패:', error);
    process.exit(1);
  }
}

async function processMarkdownFile(filePath) {
  const content = await fs.readFile(filePath, 'utf8');
  const { data: frontMatter, content: markdownContent } = matter(content);

  // HTML 변환
  const htmlContent = md.render(markdownContent);

  // 메타데이터 추출
  const title = frontMatter.title || extractTitleFromContent(markdownContent) || path.basename(filePath, '.md');
  const description = frontMatter.description || extractDescriptionFromContent(markdownContent);

  // 브레드크럼 생성
  const breadcrumb = generateBreadcrumb(filePath);

  // 사이드바 생성 (목차)
  const sidebar = generateSidebar(htmlContent);

  // HTML 템플릿 적용
  const finalHtml = htmlTemplate
    .replace('{{title}}', title)
    .replace('{{description}}', description)
    .replace('{{content}}', htmlContent)
    .replace('{{breadcrumb}}', breadcrumb)
    .replace('{{sidebar}}', sidebar)
    .replace('{{lastModified}}', moment().format('YYYY-MM-DD HH:mm'));

  // 출력 파일 경로
  const outputPath = path.join(config.outputDir, filePath.replace('.md', '.html'));

  // 디렉토리 생성
  await fs.ensureDir(path.dirname(outputPath));

  // HTML 파일 저장
  await fs.writeFile(outputPath, finalHtml);

  console.log(`✓ ${filePath} → ${outputPath}`);
}

function extractTitleFromContent(content) {
  const match = content.match(/^#\s+(.+)$/m);
  return match ? match[1] : null;
}

function extractDescriptionFromContent(content) {
  const lines = content.split('\n');
  for (const line of lines) {
    if (line.trim() && !line.startsWith('#') && !line.startsWith('```')) {
      return line.trim().substring(0, 160) + '...';
    }
  }
  return '방송통신대학교 학습 아카이브';
}

function generateBreadcrumb(filePath) {
  const parts = filePath.split('/');
  let breadcrumb = '<nav class="breadcrumb">';
  let currentPath = '';

  breadcrumb += '<a href="/">🏠 홈</a>';

  for (let i = 0; i < parts.length - 1; i++) {
    currentPath += parts[i] + '/';
    breadcrumb += ` > <a href="/${currentPath}">${parts[i]}</a>`;
  }

  if (parts.length > 1) {
    breadcrumb += ` > ${parts[parts.length - 1].replace('.md', '')}`;
  }

  breadcrumb += '</nav>';
  return breadcrumb;
}

function generateSidebar(htmlContent) {
  // 목차 추출
  const tocMatch = htmlContent.match(/<div class="table-of-contents">[\s\S]*?<\/div>/);
  const toc = tocMatch ? tocMatch[0] : '';

  return `
    <aside class="sidebar">
      ${toc}
      <div class="sidebar-section">
        <h4>빠른 링크</h4>
        <ul>
          <li><a href="/subjects/">📚 과목별 정리</a></li>
          <li><a href="/research/">🔬 연구 자료</a></li>
          <li><a href="/code-examples/">💻 코드 예제</a></li>
          <li><a href="/resources/">🔗 참고 자료</a></li>
        </ul>
      </div>
    </aside>
  `;
}

async function generateIndexPage() {
  const indexContent = `
    <div class="hero">
      <h1>🎓 방송통신대학교 학습 아카이브</h1>
      <p>체계적인 학습 관리와 지식 공유를 위한 종합 문서화 프로젝트</p>
    </div>
    
    <div class="features">
      <div class="feature-card">
        <h3>📚 학습 컨텐츠</h3>
        <p>컴퓨터과학개론, 데이터구조, 알고리즘, 운영체제 등 교과목별 체계적인 정리</p>
        <a href="/subjects/">교과목 보기</a>
      </div>
      
      <div class="feature-card">
        <h3>📰 기술 블로그 크롤링</h3>
        <p>매일 수집되는 최신 기술 동향 - 영어/한국어 주요 블로그 6곳</p>
        <a href="/research/trends/">크롤링 보기</a>
      </div>
      
      <div class="feature-card">
        <h3>💻 코드 예제</h3>
        <p>알고리즘, 자료구조, 프로젝트 등 실습 코드 모음</p>
        <a href="/code-examples/">코드 보기</a>
      </div>
      
      <div class="feature-card">
        <h3>🤖 AI 활용</h3>
        <p>생성형 AI를 활용한 학습 최적화 및 자동화</p>
        <a href="/ai-assistant/">AI 도구</a>
      </div>
    </div>

    <div class="tech-blogs-section">
      <h2>📰 기술 블로그 크롤링</h2>
      <div class="blog-categories">
        <div class="blog-category">
          <h3>🌍 영어 블로그</h3>
          <ul>
            <li><a href="/research/trends/english/hacker-news/">Hacker News</a> - 개발자 커뮤니티 핫이슈</li>
            <li><a href="/research/trends/english/dev-to/">Dev.to</a> - 개발자 블로그 플랫폼</li>
            <li><a href="/research/trends/english/medium-engineering/">Medium Engineering</a> - 대기업 엔지니어링 블로그</li>
          </ul>
        </div>
        <div class="blog-category">
          <h3>🇰🇷 한국어 블로그</h3>
          <ul>
            <li><a href="/research/trends/korean/kakao/">카카오 기술블로그</a> - 대규모 서비스 운영 노하우</li>
            <li><a href="/research/trends/korean/woowahan/">우아한형제들</a> - 배달의민족 개발 경험</li>
            <li><a href="/research/trends/korean/naver-d2/">네이버 D2</a> - 기술 연구 및 오픈소스</li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="recent-updates">
      <h2>📈 최근 업데이트</h2>
      <ul>
        <li>🤖 일일 기술 블로그 크롤링 시스템 구축 (24시간 기준)</li>
        <li>📱 Slack/Telegram 봇 알림 시스템 추가</li>
        <li>🚀 GitHub Actions 자동 배포 설정</li>
        <li>📝 학습 템플릿 및 가이드라인 작성</li>
        <li>💾 DB 없이 GitHub 저장소 활용한 데이터 관리</li>
      </ul>
    </div>
  `;

  const indexHtml = htmlTemplate
    .replace('{{title}}', '방송통신대학교 학습 아카이브')
    .replace('{{description}}', '체계적인 학습 관리와 지식 공유를 위한 종합 문서화 프로젝트')
    .replace('{{content}}', indexContent)
    .replace('{{breadcrumb}}', '')
    .replace('{{sidebar}}', '')
    .replace('{{lastModified}}', moment().format('YYYY-MM-DD HH:mm'));

  await fs.writeFile(path.join(config.outputDir, 'index.html'), indexHtml);
  console.log('✓ 인덱스 페이지 생성 완료');
}

// 빌드 실행
if (require.main === module) {
  buildDocs();
}

module.exports = { buildDocs }; 