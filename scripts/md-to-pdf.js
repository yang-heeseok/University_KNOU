#!/usr/bin/env node

/**
 * Markdown → PDF 변환 스크립트
 *
 * 사용법:
 *   node scripts/md-to-pdf.js <파일 또는 glob 패턴> [옵션]
 *
 * 예시:
 *   node scripts/md-to-pdf.js subjects/4-2/.../integrated_report.md
 *   node scripts/md-to-pdf.js "subjects/**\/integrated_report.md"
 *   node scripts/md-to-pdf.js report.md --margin-top 10mm --margin-bottom 10mm
 *   node scripts/md-to-pdf.js report.md -o output/report.pdf
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
  const candidates = [
    // nvm 경로 (Windows)
    path.join(process.env.NVM_HOME || '', 'v22.21.0', 'node_modules', 'md-to-pdf', 'dist', 'index.js'),
    path.join(process.env.APPDATA  || '', 'Local', 'nvm', 'v22.21.0', 'node_modules', 'md-to-pdf', 'dist', 'index.js'),
    // npm 전역 경로
    path.join(process.env.APPDATA  || '', 'npm', 'node_modules', 'md-to-pdf', 'dist', 'index.js'),
    '/usr/local/lib/node_modules/md-to-pdf/dist/index.js',
    '/usr/lib/node_modules/md-to-pdf/dist/index.js',
  ];

  // npm root -g 로도 탐색
  try {
    const { execSync } = require('child_process');
    const npmRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
    candidates.unshift(path.join(npmRoot, 'md-to-pdf', 'dist', 'index.js'));
  } catch (_) {}

  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
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

// ─── 인자 파싱 ─────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const args = argv.slice(2);
  const result = {
    files:       [],
    margin:      { ...DEFAULT_MARGIN },
    output:      null,
    imageScale:  null,
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
      default:
        if (!args[i].startsWith('--')) result.files.push(args[i]);
    }
  }
  if (!result.mermaidScale) result.mermaidScale = '100%';
  return result;
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

// ─── 도움말 ────────────────────────────────────────────────────────────────
function printHelp() {
  console.log(`
Markdown → PDF 변환 스크립트

사용법:
  node scripts/md-to-pdf.js <파일 또는 glob> [옵션]

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
async function convertFile(mdToPdf, inputPath, outputPath, margin, imageScale, mermaidScale, mmdcCmd) {
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

  const cssExtra = imageScale
    ? `img { max-width: ${imageScale} !important; width: ${imageScale} !important; display: block; }`
    : '';

  // 임시 디렉토리 (mermaid SVG 캐시용)
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'md-to-pdf-'));

  try {
    const rawContent = fs.readFileSync(absInput, 'utf8');
    const hasMermaid = /```mermaid/.test(rawContent);

    let inputArg;
    if (hasMermaid && mmdcCmd) {
      // Mermaid 전처리가 필요한 경우: 원본 파일 옆에 임시 .md 작성 → path 로 전달
      // (같은 디렉터리에 두어야 상대경로 이미지 참조가 그대로 해석됨)
      const processed = preprocessMermaid(rawContent, mermaidScale, tempDir, mmdcCmd);
      const tmpMd = path.join(path.dirname(absInput), `.md-to-pdf-${process.pid}.md`);
      fs.writeFileSync(tmpMd, processed);
      inputArg = { path: tmpMd, _cleanup: tmpMd };
    } else {
      if (hasMermaid) console.warn('  [경고] mmdc 미설치 → Mermaid 블록은 코드로 출력됩니다.');
      // path 로 전달 → md-to-pdf 가 file:// 로 로드하여 상대경로 이미지가 정상 해석됨
      inputArg = { path: absInput };
    }

    const result = await mdToPdf(
      { path: inputArg.path },
      { pdf_options: { format: 'a4', printBackground: true, margin }, css: cssExtra }
    );

    if (inputArg._cleanup) {
      try { fs.unlinkSync(inputArg._cleanup); } catch (_) {}
    }

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
    // 임시 파일 정리
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

  let success = 0;
  for (const file of allFiles) {
    const outPath = allFiles.length === 1 ? opts.output : null;
    if (await convertFile(mdToPdf, file, outPath, opts.margin, opts.imageScale, opts.mermaidScale, mmdcCmd)) success++;
  }

  console.log('─'.repeat(50));
  console.log(`완료: ${success} / ${allFiles.length}개 성공\n`);
  if (success < allFiles.length) process.exit(1);
}

main().catch(err => {
  console.error('[치명적 오류]', err);
  process.exit(1);
});
