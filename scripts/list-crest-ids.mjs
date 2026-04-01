import { readdirSync, mkdirSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const crestsDir = join(__dirname, '../crests');
const outPath = 'C:/export/football-vault/crest-ids.txt';

const ids = readdirSync(crestsDir)
  .filter(f => f.endsWith('.svg'))
  .map(f => parseInt(f.replace('.svg', ''), 10))
  .sort((a, b) => a - b);

mkdirSync('C:/export/football-vault', { recursive: true });
writeFileSync(outPath, ids.join('\n'), 'utf8');
console.log(`Written ${ids.length} IDs to ${outPath}`);
