import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

// Read-only by default. Optional diagram extraction stays inside this repository.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const args = process.argv.slice(2);
const options = new Map();
for (let i = 0; i < args.length; i += 2) {
  assert(['--mermaid-module', '--extract-dir'].includes(args[i]), `Unknown option: ${args[i]}`);
  assert(args[i + 1] && !args[i + 1].startsWith('--'), `Missing value: ${args[i]}`);
  options.set(args[i], args[i + 1]);
}
const files = [
  'docs/MECHANISMS.md', 'docs/QUESTIONS.md',
  'docs/evidence/SEM-19/INPUT_REVIEW.md', 'docs/evidence/SEM-19/CHECKS.md',
  'tasks/backlog/SEM-19.md',
];
const read = file => fs.readFileSync(path.resolve(root, file), 'utf8');
const text = Object.fromEntries(files.map(file => [file, read(file)]));
const slug = heading => heading.replace(/`/g, '').toLowerCase()
  .replace(/[^\p{L}\p{N}_ -]/gu, '').replace(/ /g, '-');
let links = 0, fragments = 0, tables = 0;
for (const [file, body] of Object.entries(text)) {
  assert(body.endsWith('\n'), `${file}: missing terminal newline`);
  assert(!body.includes('\uFFFD'), `${file}: invalid UTF-8 replacement`);
  assert(!/[\t ]+$/m.test(body), `${file}: trailing whitespace`);
  assert.equal((body.match(/^```/gm) || []).length % 2, 0, `${file}: unbalanced fences`);
  for (const m of body.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
    if (/^[a-z][a-z0-9+.-]*:\/\//i.test(m[1])) continue;
    const [relative, fragment] = m[1].split('#');
    const target = relative ? path.resolve(root, path.dirname(file), relative) : path.resolve(root, file);
    assert(fs.existsSync(target), `${file}: missing link ${m[1]}`);
    links++;
    if (fragment) {
      const headings = [...fs.readFileSync(target, 'utf8').matchAll(/^#{1,6}\s+(.+)$/gm)].map(h => slug(h[1]));
      assert(headings.includes(decodeURIComponent(fragment)), `${file}: missing fragment ${m[1]}`);
      fragments++;
    }
  }
  let width = null;
  for (const line of body.split('\n')) {
    if (!line.startsWith('|')) { width = null; continue; }
    const columns = line.split('|').length;
    if (width === null) tables++;
    else assert.equal(columns, width, `${file}: inconsistent Markdown table`);
    width = columns;
  }
}

const catalog = JSON.parse(read('tasks/catalog.json'));
const task = catalog.tasks.find(t => t.id === 'SEM-19');
assert(task, 'SEM-19 missing from catalog');
let inputs = 0;
for (const id of [...task.start_dependencies, ...task.finish_dependencies]) {
  const source = catalog.tasks.find(t => t.id === id);
  assert.equal(source?.status, 'Done', `${id}: dependency not Done in snapshot`);
  for (const file of [...source.outputs, `docs/evidence/${id}/CHECKS.md`]) {
    assert(fs.existsSync(path.resolve(root, file)), `${id}: missing artifact ${file}`);
    inputs++;
  }
}
const questions = text['docs/QUESTIONS.md'].split(/^## /m).slice(1).filter(s => /^\d+\./.test(s));
assert(questions.length >= 10, 'At least 10 questions required');
questions.forEach((section, i) => {
  assert(section.startsWith(`${i + 1}. `), 'Questions must be sequential');
  assert(section.includes('Nguồn:'), `Question ${i + 1}: source missing`);
});
for (const file of ['docs/MECHANISMS.md', 'docs/QUESTIONS.md']) {
  assert(!/chờ đối chiếu SEM-15|chờ SEM-15|Bản làm trước phần độc lập/i.test(text[file]), `${file}: unresolved intake label`);
}
const diagrams = [...text['docs/MECHANISMS.md'].matchAll(/```mermaid\r?\n([\s\S]*?)```/g)].map(m => m[1]);
assert.equal(diagrams.length, 2, 'Two trigger-to-cache diagrams required');
let parsed = null;
if (options.has('--mermaid-module')) {
  const mermaid = (await import(pathToFileURL(path.resolve(root, options.get('--mermaid-module'))).href)).default;
  mermaid.initialize({ startOnLoad: false });
  for (const diagram of diagrams) assert(await mermaid.parse(diagram));
  parsed = diagrams.length;
}
if (options.has('--extract-dir')) {
  const directory = path.resolve(root, options.get('--extract-dir'));
  assert(directory.startsWith(root + path.sep), 'Extraction must stay inside the repository');
  fs.mkdirSync(directory, { recursive: true });
  diagrams.forEach((diagram, i) => fs.writeFileSync(path.join(directory, `diagram-${i + 1}.mmd`), diagram));
}
const consumers = catalog.tasks.filter(t => [...t.start_dependencies, ...t.finish_dependencies].includes('SEM-19'));
console.log(JSON.stringify({
  files: files.length, internal_links: links, fragments, tables,
  input_artifacts: inputs, questions: questions.length, questions_with_sources: questions.length,
  diagram_blocks: diagrams.length, mermaid_parsed: parsed,
  consumers: consumers.map(t => t.id), runtime: 'NOT_RUN',
  head: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(),
}, null, 2));
