import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_DIR = path.resolve(__dirname, '../data');
const SNAPSHOT_FILE = path.join(DATA_DIR, 'snapshot.json');

const INITIAL_SNAPSHOT = {
  version: 1,
  last_modified_utc: new Date().toISOString(),
  items: [
    {
      id: "bulletin-1",
      title: "Chào mừng đến với Seminar IE307",
      body: "Hệ thống đồng bộ dữ liệu Android (Periodic, Push, Hybrid).",
      version: 1
    }
  ]
};

export class SnapshotStore {
  constructor(filePath = SNAPSHOT_FILE) {
    this.filePath = filePath;
    this.ensureDataFile();
  }

  ensureDataFile() {
    const dir = path.dirname(this.filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    if (!fs.existsSync(this.filePath)) {
      this.writeSnapshot(INITIAL_SNAPSHOT);
    }
  }

  getSnapshot() {
    try {
      const data = fs.readFileSync(this.filePath, 'utf-8');
      return JSON.parse(data);
    } catch (err) {
      console.error('Error reading snapshot file, falling back to initial:', err);
      return INITIAL_SNAPSHOT;
    }
  }

  updateSnapshot({ title, body, runId }) {
    const current = this.getSnapshot();
    const nextVersion = Number(current.version || 0) + 1;
    const nowUtc = new Date().toISOString();

    const newItem = {
      id: `bulletin-${nextVersion}`,
      title: title || `Bản tin v${nextVersion}`,
      body: body || `Nội dung cập nhật lúc ${nowUtc}`,
      version: nextVersion,
    };

    const updated = {
      version: nextVersion,
      last_modified_utc: nowUtc,
      items: [newItem, ...current.items],
    };

    this.writeSnapshot(updated);
    return updated;
  }

  writeSnapshot(snapshot) {
    const tempPath = `${this.filePath}.tmp.${Date.now()}`;
    fs.writeFileSync(tempPath, JSON.stringify(snapshot, null, 2), 'utf-8');
    fs.renameSync(tempPath, this.filePath);
  }
}

export const defaultStore = new SnapshotStore();
