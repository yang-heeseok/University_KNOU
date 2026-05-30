#!/usr/bin/env node

/**
 * Markdown → PDF 변환 스크립트
 *
 * 목표:
 *   VS Code 프리뷰(특히 Markdown Preview Enhanced) 및 일반적인 GitHub md 렌더링과
 *   "동일한 외형"으로 PDF 를 생성한다. 이를 위해 아래 3가지를 자동 적용한다.
 *     1) github-markdown-css 를 stylesheet 으로 적용 (색·표·blockquote·코드·폰트 = GitHub)
 *     2) marked breaks:true → 단일 개행을 줄바꿈으로 처리 (MPE breakOnSingleNewLine 기본값과 동일)
 *     3) <details> 에 open 자동 부여 → 접힌 본문이 PDF 에서 누락되지 않게 함
 *   부가: KaTeX($$…$$ / $…$) 사전 렌더링, Mermaid(```mermaid```) SVG 사전 렌더링.
 *
 * 사전 설치(전역):
 *   npm install -g md-to-pdf github-markdown-css
 *   npm install -g @mermaid-js/mermaid-cli   # (선택) mermaid 다이어그램용
 *   npm install -g katex                      # (선택) 수식용. 없으면 원문 그대로 출력
 *
 * 사용법:
 *   node scripts/md-to-pdf.js <파일 또는 glob 패턴> [옵션]
 *
 * 예시:
 *   node scripts/md-to-pdf.js subjects/4-2/.../integrated_report.md
 *   node scripts/md-to-pdf.js "subjects/**\/integrated_report.md"
 *   node scripts/md-to-pdf.js report.md --margin-top 10mm --margin-bottom 10mm
 *   node scripts/md-to-pdf.js report.md -o output/report.pdf
 *   # 폴더로 모아서(여러 파일은 -o 불가 → 파일별로 반복 실행):
 *   #   for n in 1 2 3; do node scripts/md-to-pdf.js "다강/${n}강.md" -o "out/${n}강.pdf"; done
 *
 * 여백 기본값: md-to-pdf 기본(30mm)의 1/5 적용
 *   top: 6mm / bottom: 6mm / left: 20mm / right: 40mm
 */

'use strict';

const path = require('path');
const fs   = require('fs');
const os   = require('os');
const { execSync } = require('child_process');

// md-to-pdf 전역 설치 경로 자동 탐색
function resolveMdToPdf() {
  const SUB = path.join('node_modules', 'md-to-pdf', 'dist', 'index.js');
  const candidates = [];

  // npm root -g 를 최우선으로 탐색
  try {
    const npmRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
    candidates.push(path.join(npmRoot, 'md-to-pdf', 'dist', 'index.js'));
  } catch (_) {}

  // nvm 설치 경로의 모든 노드 버전 디렉터리를 동적으로 스캔 (버전 하드코딩 제거)
  const nvmRoots = [
    process.env.NVM_HOME,
    process.env.APPDATA && path.join(process.env.APPDATA, 'Local', 'nvm'),
    process.env.NVM_DIR && path.join(process.env.NVM_DIR, 'versions', 'node'),
  ].filter(Boolean);
  for (const root of nvmRoots) {
    try {
      for (const ver of fs.readdirSync(root)) {
        candidates.push(path.join(root, ver, SUB));        // Windows nvm 배치
        candidates.push(path.join(root, ver, 'lib', SUB)); // *nix nvm 배치
      }
    } catch (_) {}
  }

  // npm 전역 / 유닉스 표준 경로
  candidates.push(
    path.join(process.env.APPDATA || '', 'npm', SUB),
    '/usr/local/lib/node_modules/md-to-pdf/dist/index.js',
    '/usr/lib/node_modules/md-to-pdf/dist/index.js',
  );

  for (const p of candidates) {
    if (p && fs.existsSync(p)) return p;
  }
  return null;
}

// ─── github-markdown-css 경로 탐색 ──────────────────────────────────────────
// VS Code(Markdown Preview Enhanced) 및 일반적인 md 렌더링과 동일한 외형을 위해
// GitHub 공식 스타일(github-markdown-css)을 적용한다.
// 라이트 테마(github-markdown-light.css)를 우선 선택 → 다크모드 환경에서도 흰 배경 유지.
function resolveGithubMarkdownCss() {
  const names = ['github-markdown-light.css', 'github-markdown.css'];
  const roots = [path.join(__dirname, '..', 'node_modules', 'github-markdown-css')];
  try {
    const npmRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
    roots.push(path.join(npmRoot, 'github-markdown-css'));
  } catch (_) {}
  for (const r of roots) {
    for (const n of names) {
      const p = path.join(r, n);
      if (fs.existsSync(p)) return p;
    }
  }
  return null;
}

// ─── 기본 여백 설정 ────────────────────────────────────────────────────────
// md-to-pdf 기본값: top 30mm / bottom 30mm / left 20mm / right 40mm
// 현재 설정: top/bottom을 1/5로 줄인 값 (30mm → 6mm)
const DEFAULT_MARGIN = {
  top:    '6mm',
  bottom: '6mm',
  left:   '20mm',
  right:  '40mm',
};

// ─── 인쇄(PDF) 보조 CSS ─────────────────────────────────────────────────────
// 색·테두리·여백 등 "시각 테마"는 github-markdown-css 가 담당한다(GitHub/프리뷰 외형 재현).
// 여기서는 PDF 에서만 필요한 페이지 나눔·줄바꿈 동작과, 화면용 GitHub CSS 가
// 인쇄 시 빠뜨리는 배경색 강제(.markdown-body 패딩/배경)만 보강한다.
// (css 옵션은 stylesheet 뒤에 "추가"되므로 GitHub CSS 를 덮어쓸 수 있음)
const BASE_PRINT_CSS = `
  /* GitHub CSS 의 .markdown-body 는 max-width/패딩이 화면 기준 → 인쇄 여백과 맞게 해제 */
  .markdown-body { box-sizing: border-box; min-width: 0 !important; max-width: none !important; margin: 0 !important; padding: 0 !important; }
  /* 표 헤더·줄무늬 배경이 인쇄되도록 색 보정 (printBackground 와 병행) */
  .markdown-body table tr, .markdown-body table th, .markdown-body table td,
  .markdown-body pre, .markdown-body code, .markdown-body blockquote {
    -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
  }
  /* GitHub 표는 display:block + overflow 라 PDF 에서 폭이 줄어듦 → 일반 표로 펼침 */
  .markdown-body table { display: table !important; width: 100% !important; overflow: visible !important; }
  thead { display: table-header-group; }                    /* 페이지 넘김 시 헤더 행 반복 */
  tr  { page-break-inside: avoid; break-inside: avoid; }     /* 행이 페이지 경계에서 잘리지 않게 */
  pre, blockquote, img, table, .katex-display { page-break-inside: avoid; break-inside: avoid; }
  .markdown-body pre, .markdown-body pre > code { white-space: pre-wrap; word-break: break-word; }  /* 긴 코드 가로 넘침 방지 */
  h1, h2, h3, h4 { page-break-after: avoid; break-after: avoid; }  /* 제목 직후 페이지 넘김 방지 */
  p, li { orphans: 2; widows: 2; }                          /* 문단 끝 한 줄 고립 방지 */
  /* <details>: 전처리에서 open 강제 → 본문이 PDF 에서 누락되지 않도록 안전망 */
  details { page-break-inside: avoid; break-inside: avoid; }
  details > *:not(summary) { display: block !important; }
`;

// ─── 인자 파싱 ─────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const args = argv.slice(2);
  const result = {
    files:       [],
    margin:      { ...DEFAULT_MARGIN },
    output:      null,
    imageScale:  null,
    format:      'a4',
    width:       null,
    height:      null,
    landscape:   false,
    help:        false,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--help': case '-h':   result.help = true; break;
      case '--margin-top':        result.margin.top    = args[++i]; break;
      case '--margin-bottom':     result.margin.bottom = args[++i]; break;
      case '--margin-left':       result.margin.left   = args[++i]; break;
      case '--margin-right':      result.margin.right  = args[++i]; break;
      case '--output': case '-o': result.output        = args[++i]; break;
      case '--image-scale':       result.imageScale    = args[++i]; break;
      case '--mermaid-scale':     result.mermaidScale  = args[++i]; break;
      case '--format':            result.format        = args[++i]; break;
      case '--width':             result.width         = args[++i]; break;
      case '--height':            result.height        = args[++i]; break;
      case '--landscape':         result.landscape     = true; break;
      default:
        if (!args[i].startsWith('--')) result.files.push(args[i]);
    }
  }
  if (!result.mermaidScale) result.mermaidScale = '100%';
  return result;
}

// ─── KaTeX 수식 사전 렌더링 ────────────────────────────────────────────────
// $$...$$ (display) 와 $...$ (inline) 을 KaTeX 로 HTML 변환하여 임베드.
// md-to-pdf 는 LaTeX 를 인식하지 못하므로 사전 렌더링이 필요함.
function loadKatex() {
  // 프로젝트 로컬 → 글로벌 npm root 순서로 katex 모듈 탐색
  const candidates = [
    path.join(__dirname, '..', 'node_modules', 'katex'),
  ];
  try {
    const npmRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
    candidates.push(path.join(npmRoot, 'katex'));
  } catch (_) {}
  for (const p of candidates) {
    if (fs.existsSync(path.join(p, 'package.json'))) {
      try { return require(p); } catch (_) {}
    }
  }
  return null;
}

function preprocessKatex(mdContent, katex) {
  if (!katex) return { content: mdContent, count: 0 };

  let count = 0;

  const renderDisplay = (_m, tex) => {
    try {
      const html = katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false, strict: 'ignore' });
      count++;
      return `\n\n<div style="text-align:center; margin:0.6em 0;">${html}</div>\n\n`;
    } catch (e) {
      console.error(`    [KaTeX 오류] ${e.message.split('\n')[0]}`);
      return _m;
    }
  };
  const renderInline = (_m, tex) => {
    try {
      const html = katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false, strict: 'ignore' });
      count++;
      return html;
    } catch (e) {
      return _m;
    }
  };

  // 코드블록을 먼저 분리해 보호한 뒤, 코드가 아닌 구간에서만
  // display($$…$$) → inline($…$) 순으로 변환한다.
  //  · 펜스(```…```) 패턴을 인라인(`…`)보다 앞에 두어야 ```블록``` 안의 $ 가 보호됨
  //  · display 치환도 분리 후에 수행하여 코드블록 내부의 $$ 가 렌더링되지 않도록 함
  const segments = mdContent.split(/(```[\s\S]*?```|`[^`]*`)/g);
  for (let i = 0; i < segments.length; i++) {
    if (segments[i].startsWith('`')) continue;            // 코드 구간은 건너뜀
    segments[i] = segments[i]
      .replace(/\$\$([\s\S]+?)\$\$/g, renderDisplay)          // 1) display math
      .replace(/(?<!\$)\$([^\$\n]+?)\$(?!\$)/g, renderInline); // 2) inline math
  }
  return { content: segments.join(''), count };
}

// ─── mermaid 블록 사전 렌더링 ──────────────────────────────────────────────
function findMmdc() {
  // 1) PATH 에 등록된 mmdc 우선
  try { execSync('mmdc --version', { stdio: 'pipe' }); return 'mmdc'; } catch (_) {}
  // 2) npm 전역 bin 경로 탐색 (Windows: <prefix>/mmdc.cmd, *nix: <prefix>/bin/mmdc)
  try {
    const npmRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
    const prefix  = path.dirname(npmRoot);
    const candidates = [
      path.join(prefix, 'mmdc.cmd'),
      path.join(prefix, 'mmdc'),
      path.join(prefix, 'bin', 'mmdc'),
    ];
    for (const c of candidates) if (fs.existsSync(c)) return `"${c}"`;
  } catch (_) {}
  return null;
}

function preprocessMermaid(mdContent, mermaidScale, tempDir, mmdcCmd) {
  const re = /```mermaid\r?\n([\s\S]*?)```/g;
  let processed = mdContent;
  const blocks = [];
  let m, idx = 0;
  while ((m = re.exec(mdContent)) !== null) {
    blocks.push({ original: m[0], code: m[1], idx: idx++ });
  }
  if (blocks.length === 0) return processed;

  console.log(`  Mermaid 블록 ${blocks.length}개 감지 → SVG 사전 렌더링`);

  for (const b of blocks) {
    const inputPath  = path.join(tempDir, `mermaid_${b.idx}.mmd`);
    const outputPath = path.join(tempDir, `mermaid_${b.idx}.svg`);
    fs.writeFileSync(inputPath, b.code);

    try {
      execSync(`${mmdcCmd} -i "${inputPath}" -o "${outputPath}" -b transparent`, { stdio: 'pipe' });
      let svg = fs.readFileSync(outputPath, 'utf8');
      // SVG 의 고정 width/height 속성 제거 → viewBox 기반으로 컨테이너에 맞춤
      svg = svg.replace(/<svg([^>]*?)\swidth="[^"]*"/, '<svg$1');
      svg = svg.replace(/<svg([^>]*?)\sheight="[^"]*"/, '<svg$1');
      svg = svg.replace(/<svg([^>]*?)>/, `<svg$1 style="width:100%; height:auto;">`);
      const wrapped = `\n\n<div style="width:${mermaidScale}; margin:0 auto; text-align:center;">\n\n${svg}\n\n</div>\n\n`;
      processed = processed.replace(b.original, wrapped);
      console.log(`    [${b.idx + 1}/${blocks.length}] OK (scale=${mermaidScale})`);
    } catch (err) {
      console.error(`    [${b.idx + 1}/${blocks.length}] 실패: ${err.message.split('\n')[0]}`);
    }
  }
  return processed;
}

// ─── <details> 강제 펼침 ───────────────────────────────────────────────────
// <details> 는 open 속성이 없으면 Chromium 렌더링 시 본문이 접혀(display:none)
// PDF 에 본문이 출력되지 않는다. 변환 전에 open 을 강제로 부여한다.
// (이미 open 이 있는 경우는 건드리지 않음)
function forceOpenDetails(mdContent) {
  let count = 0;
  const out = mdContent.replace(/<details(?![^>]*\bopen\b)([^>]*)>/gi, (_m, attrs) => {
    count++;
    return `<details open${attrs}>`;
  });
  return { content: out, count };
}

// ─── 도움말 ────────────────────────────────────────────────────────────────
function printHelp() {
  console.log(`
Markdown → PDF 변환 스크립트
  (VS Code 프리뷰 / GitHub md 렌더링과 동일한 외형으로 변환)
  자동 적용: github-markdown-css 스타일 · 단일개행 줄바꿈(breaks) · <details> 자동 펼침

사용법:
  node scripts/md-to-pdf.js <파일 또는 glob> [옵션]

사전 설치(전역):
  npm install -g md-to-pdf github-markdown-css
  (선택) npm install -g @mermaid-js/mermaid-cli katex

예시:
  node scripts/md-to-pdf.js report.md
  node scripts/md-to-pdf.js "subjects/**/integrated_report.md"
  node scripts/md-to-pdf.js report.md --margin-top 10mm --margin-bottom 10mm
  node scripts/md-to-pdf.js report.md -o output/report.pdf

여백 옵션 (기본: md-to-pdf 기본 30mm의 1/5):
  --margin-top    <값>    위 여백     (기본: ${DEFAULT_MARGIN.top})
  --margin-bottom <값>    아래 여백   (기본: ${DEFAULT_MARGIN.bottom})
  --margin-left   <값>    왼쪽 여백   (기본: ${DEFAULT_MARGIN.left})
  --margin-right  <값>    오른쪽 여백 (기본: ${DEFAULT_MARGIN.right})

기타:
  --output, -o      <경로>  출력 파일 경로 (단일 파일 변환 시에만 사용 가능)
  --image-scale     <값>    일반 이미지 크기 (예: 80%)
  --mermaid-scale   <값>    Mermaid 다이어그램 크기 (기본: 100%)
  --help, -h                도움말 출력
`);
}

// ─── 단일 파일 변환 ────────────────────────────────────────────────────────
async function convertFile(mdToPdf, mdToPdfPath, inputPath, outputPath, margin, imageScale, mermaidScale, mmdcCmd, pageOpts) {
  const absInput  = path.resolve(inputPath);
  const absOutput = outputPath
    ? path.resolve(outputPath)
    : absInput.replace(/\.md$/i, '.pdf');

  if (!fs.existsSync(absInput)) {
    console.error(`[오류] 파일 없음: ${absInput}`);
    return false;
  }

  // 출력 디렉토리 생성
  const outDir = path.dirname(absOutput);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  console.log(`\n  변환: ${path.relative(process.cwd(), absInput)}`);
  console.log(`  여백: top=${margin.top}  bottom=${margin.bottom}  left=${margin.left}  right=${margin.right}`);
  if (imageScale)   console.log(`  이미지 크기: ${imageScale}`);
  if (mermaidScale) console.log(`  Mermaid 크기: ${mermaidScale}`);

  const cssExtra = BASE_PRINT_CSS + (imageScale
    ? `\nimg { max-width: ${imageScale} !important; width: ${imageScale} !important; display: block; }`
    : '');

  // 임시 디렉토리 (mermaid SVG 캐시용)
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'md-to-pdf-'));
  let tmpMd = null;  // 사전처리 임시 .md (예외 발생 시에도 finally 에서 정리)

  try {
    const rawContent = fs.readFileSync(absInput, 'utf8');
    const hasMermaid = /```mermaid/.test(rawContent);
    const hasMath    = /\$\$[\s\S]+?\$\$|(?<!\$)\$[^\$\n]+?\$(?!\$)/.test(rawContent);

    // KaTeX 모듈 로드 (수식이 있을 때만)
    let katex = null;
    if (hasMath) {
      katex = loadKatex();
      if (!katex) console.warn('  [경고] katex 미설치 → LaTeX 수식은 원문 그대로 출력됩니다. (npm install katex)');
    }

    // 마크다운 사전 처리 (Mermaid + KaTeX + details)
    let needTempFile = false;
    let processedContent = rawContent;

    // <details> 강제 펼침 (접힌 본문이 PDF 에서 누락되는 문제 방지)
    {
      const r = forceOpenDetails(processedContent);
      if (r.count > 0) {
        processedContent = r.content;
        console.log(`  <details> ${r.count}개 강제 펼침(open)`);
        needTempFile = true;
      }
    }

    if (hasMath && katex) {
      const r = preprocessKatex(processedContent, katex);
      processedContent = r.content;
      console.log(`  KaTeX 수식 ${r.count}개 렌더링`);
      needTempFile = true;
    }
    if (hasMermaid && mmdcCmd) {
      processedContent = preprocessMermaid(processedContent, mermaidScale, tempDir, mmdcCmd);
      needTempFile = true;
    } else if (hasMermaid) {
      console.warn('  [경고] mmdc 미설치 → Mermaid 블록은 코드로 출력됩니다.');
    }

    let inputArg;
    if (needTempFile) {
      // 사전 처리가 있는 경우: 원본 파일 옆에 임시 .md 작성 → path 로 전달
      // (같은 디렉터리에 두어야 상대경로 이미지 참조가 그대로 해석됨)
      tmpMd = path.join(path.dirname(absInput), `.md-to-pdf-${process.pid}.md`);
      fs.writeFileSync(tmpMd, processedContent);
      inputArg = { path: tmpMd };
    } else {
      // path 로 전달 → md-to-pdf 가 file:// 로 로드하여 상대경로 이미지가 정상 해석됨
      inputArg = { path: absInput };
    }

    // ── 스타일시트 구성 ──
    // stylesheet 옵션은 번들 markdown.css 를 "교체"한다.
    // → github-markdown-css 를 베이스로 깔아 GitHub/프리뷰와 동일한 외형을 만든다.
    //   (github-markdown-css 는 .markdown-body 셀렉터를 쓰므로 body_class 로 클래스 부여 필요)
    const stylesheets = [];
    const ghCss = resolveGithubMarkdownCss();
    if (ghCss) {
      stylesheets.push(ghCss);
    } else {
      console.warn('  [경고] github-markdown-css 미설치 → 기본(번들) 스타일로 출력됩니다. (npm install -g github-markdown-css)');
      if (hasMath && katex) {
        // GitHub CSS 가 없으면 수식 가독성을 위해 번들 markdown.css 라도 유지
        const defaultMarkdownCss = path.resolve(path.dirname(mdToPdfPath), '..', 'markdown.css');
        if (fs.existsSync(defaultMarkdownCss)) stylesheets.push(defaultMarkdownCss);
      }
    }
    // KaTeX CSS 를 stylesheet 으로 주입 (CDN, 문자열 URL)
    if (hasMath && katex) {
      stylesheets.push('https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css');
    }

    const result = await mdToPdf(
      { path: inputArg.path },
      {
        // breaks:true → 소스의 단일 개행(\n)을 <br> 로 변환.
        //   VS Code 의 Markdown Preview Enhanced 는 breakOnSingleNewLine 기본값이 true 라
        //   단일 개행을 줄바꿈으로 렌더링한다. 이를 그대로 재현하기 위함.
        //   (false 면 보기·선택지의 가/나/다/라·①②③④ 줄이 한 문단으로 합쳐짐)
        marked_options: { breaks: true, gfm: true },
        // github-markdown-css 적용을 위해 <body> 에 markdown-body 클래스 부여
        body_class: ghCss ? ['markdown-body'] : undefined,
        pdf_options: (() => {
          // width/height 가 지정되면 format 대신 사용 (Puppeteer 미지원 규격: B4 등)
          const po = { printBackground: true, margin, landscape: !!(pageOpts && pageOpts.landscape) };
          if (pageOpts && pageOpts.width && pageOpts.height) {
            po.width  = pageOpts.width;
            po.height = pageOpts.height;
            // md-to-pdf 가 기본 pdf_options(format:'a4')을 깊게 병합하고
            // Puppeteer 는 format 이 있으면 width/height 를 무시하므로 명시적으로 해제한다.
            po.format = undefined;
          } else {
            po.format = (pageOpts && pageOpts.format) || 'a4';
          }
          return po;
        })(),
        css: cssExtra,
        stylesheet: stylesheets.length > 0 ? stylesheets : undefined,
      }
    );

    if (!result || !result.content) {
      console.error('  [오류] 변환 결과 없음');
      return false;
    }

    fs.writeFileSync(absOutput, result.content);
    const sizeKB = (fs.statSync(absOutput).size / 1024).toFixed(0);
    console.log(`  출력: ${path.relative(process.cwd(), absOutput)} (${sizeKB} KB)`);
    return true;
  } catch (err) {
    console.error(`  [오류] 변환 실패: ${err.message}`);
    return false;
  } finally {
    // 임시 파일 정리 (예외 발생 시에도 원본 폴더의 임시 .md 까지 확실히 제거)
    if (tmpMd) { try { fs.unlinkSync(tmpMd); } catch (_) {} }
    try { fs.rmSync(tempDir, { recursive: true, force: true }); } catch (_) {}
  }
}

// ─── 진입점 ────────────────────────────────────────────────────────────────
async function main() {
  const opts = parseArgs(process.argv);

  if (opts.help || opts.files.length === 0) {
    printHelp();
    process.exit(opts.help ? 0 : 1);
  }

  // md-to-pdf 모듈 로드
  const mdToPdfPath = resolveMdToPdf();
  if (!mdToPdfPath) {
    console.error('[오류] md-to-pdf 전역 패키지를 찾을 수 없습니다.\n       npm install -g md-to-pdf 로 설치하세요.');
    process.exit(1);
  }
  const { mdToPdf } = require(mdToPdfPath);

  // mmdc (mermaid-cli) 탐색 — 없으면 mermaid 블록은 그대로 출력
  const mmdcCmd = findMmdc();
  if (!mmdcCmd) console.warn('[경고] mmdc 미발견 → mermaid 블록은 렌더링되지 않습니다. (npm install -g @mermaid-js/mermaid-cli)');

  // glob 패턴 확장
  let allFiles = [];
  for (const pattern of opts.files) {
    if (fs.existsSync(pattern)) {
      allFiles.push(pattern);
    } else {
      try {
        const { glob } = require('glob');
        const matched = await glob(pattern, { nodir: true });
        if (matched.length === 0) console.warn(`[경고] 매칭 파일 없음: ${pattern}`);
        allFiles = allFiles.concat(matched);
      } catch (_) {
        // glob 없으면 그대로 시도
        allFiles.push(pattern);
      }
    }
  }

  if (allFiles.length === 0) {
    console.error('[오류] 변환할 파일이 없습니다.');
    process.exit(1);
  }
  if (allFiles.length > 1 && opts.output) {
    console.error('[오류] --output 옵션은 단일 파일 변환 시에만 사용할 수 있습니다.');
    process.exit(1);
  }

  console.log(`\nMarkdown → PDF 변환 시작 (총 ${allFiles.length}개)`);
  console.log('─'.repeat(50));

  const pageOpts = { format: opts.format, width: opts.width, height: opts.height, landscape: opts.landscape };

  let success = 0;
  for (const file of allFiles) {
    const outPath = allFiles.length === 1 ? opts.output : null;
    if (await convertFile(mdToPdf, mdToPdfPath, file, outPath, opts.margin, opts.imageScale, opts.mermaidScale, mmdcCmd, pageOpts)) success++;
  }

  console.log('─'.repeat(50));
  console.log(`완료: ${success} / ${allFiles.length}개 성공\n`);
  if (success < allFiles.length) process.exit(1);
}

main().catch(err => {
  console.error('[치명적 오류]', err);
  process.exit(1);
});
