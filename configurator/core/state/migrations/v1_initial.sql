-- Initial database schema for state management
-- Version: 1.0
-- Created: 2026-01-16

-- Installations table
-- Tracks overall installation sessions
CREATE TABLE IF NOT EXISTS installations (
    installation_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    profile TEXT NOT NULL,
    overall_status TEXT NOT NULL DEFAULT 'in_progress',
    metadata TEXT,  -- JSON
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Modules table
-- Tracks individual module execution within installations
CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    installation_id TEXT NOT NULL,
    module_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TEXT,
    completed_at TEXT,
    duration_seconds REAL,
    progress_percent INTEGER DEFAULT 0,
    current_step TEXT,
    error_message TEXT,
    checkpoint TEXT,
    rollback_actions TEXT,  -- JSON array
    FOREIGN KEY (installation_id) REFERENCES installations (installation_id) ON DELETE CASCADE,
    UNIQUE (installation_id, module_name)
);

-- Checkpoints table
-- Stores state snapshots at specific points
CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    installation_id TEXT NOT NULL,
    module_name TEXT NOT NULL,
    checkpoint_name TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    state_snapshot TEXT,  -- JSON
    FOREIGN KEY (installation_id) REFERENCES installations (installation_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_modules_installation ON modules(installation_id);
CREATE INDEX IF NOT EXISTS idx_modules_status ON modules(status);
CREATE INDEX IF NOT EXISTS idx_checkpoints_installation ON checkpoints(installation_id);
CREATE INDEX IF NOT EXISTS idx_checkpoints_module ON checkpoints(installation_id, module_name);
CREATE INDEX IF NOT EXISTS idx_installations_status ON installations(overall_status);
CREATE INDEX IF NOT EXISTS idx_installations_started ON installations(started_at DESC);
