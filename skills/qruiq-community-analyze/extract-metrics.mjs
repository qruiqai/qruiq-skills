#!/usr/bin/env node
/**
 * Helper for the qruiq-community-analyze skill.
 *
 * Given a subreddit name and a workflow kind ("timing" | "critic"), finds the
 * latest log directory in cowork and extracts structured metrics for
 * synthesis into the final report.
 *
 * Usage:
 *   node extract-metrics.mjs timing r/singaporefi
 *   node extract-metrics.mjs critic r/singaporefi
 *   node extract-metrics.mjs critic-multi r/singaporefi
 *
 * Prints JSON to stdout with the extracted fields. Exits non-zero if no
 * matching log directory can be found.
 */

import fs from "node:fs";
import path from "node:path";

const LOGS_ROOT = "/Users/timmysun/Desktop/cowork/logs/workflow";

const kind = process.argv[2];
const subredditRaw = process.argv[3];
if (!kind || !subredditRaw) {
  console.error("usage: extract-metrics.mjs <timing|critic|critic-multi> <subreddit>");
  process.exit(1);
}
const normalized = subredditRaw.replace(/^r\//i, "").toLowerCase();

const WORKFLOW_PREFIX = {
  timing: "analysis-comment-timing_",
  critic: "community-critic-prompt-train_",
  "critic-multi": "community-critic-prompt-train_",
}[kind];
if (!WORKFLOW_PREFIX) {
  console.error(`unknown kind: ${kind}`);
  process.exit(1);
}

function listRuns() {
  if (!fs.existsSync(LOGS_ROOT)) return [];
  return fs
    .readdirSync(LOGS_ROOT)
    .filter((n) => n.startsWith(WORKFLOW_PREFIX))
    .map((n) => {
      const full = path.join(LOGS_ROOT, n);
      return { name: n, path: full, mtime: fs.statSync(full).mtimeMs };
    })
    .sort((a, b) => b.mtime - a.mtime);
}

function matchSubreddit(run, want) {
  const outJson = path.join(run.path, "output.json");
  if (!fs.existsSync(outJson)) return false;
  try {
    const parsed = JSON.parse(fs.readFileSync(outJson, "utf-8"));
    if (!parsed.subreddit) return false;
    return parsed.subreddit === want;
  } catch {
    return false;
  }
}

const runs = listRuns();
const match = runs.find((r) => matchSubreddit(r, normalized));
if (!match) {
  console.error(`no ${kind} run found for r/${normalized}`);
  process.exit(2);
}

const out = JSON.parse(fs.readFileSync(path.join(match.path, "output.json"), "utf-8"));

function fmtDuration(sec) {
  if (sec == null) return "—";
  if (sec < 60) return `${sec.toFixed(0)}s`;
  if (sec < 3600) return `${(sec / 60).toFixed(1)}m`;
  if (sec < 86400) return `${(sec / 3600).toFixed(1)}h`;
  return `${(sec / 86400).toFixed(1)}d`;
}

if (kind === "timing") {
  const s = out.summary || {};
  const fetchInfo = out.fetch || {};
  const dropCounts = {};
  for (const d of fetchInfo.dropReasons || []) {
    dropCounts[d.reason] = (dropCounts[d.reason] || 0) + 1;
  }
  console.log(
    JSON.stringify(
      {
        kind: "timing",
        logDir: match.path,
        outputJson: path.join(match.path, "output.json"),
        outputMd: path.join(match.path, "output.md"),
        subreddit: out.subreddit,
        executionId: out.executionId,
        durationMs: out.durationMs,
        totalPosts: s.totalPosts,
        totalComments: s.totalComments,
        goldenWindowSec: s.goldenWindowSec,
        goldenWindowPretty: fmtDuration(s.goldenWindowSec),
        medianTopAgeSec: s.medianTopBucketAgeSec,
        medianTopAgePretty: fmtDuration(s.medianTopBucketAgeSec),
        medianBottomAgeSec: s.medianBottomBucketAgeSec,
        medianBottomAgePretty: fmtDuration(s.medianBottomBucketAgeSec),
        spearman: s.avgSpearmanAgeVsScore,
        cumTopShareAt: s.cumTopShareAt || {},
        bins: s.bins || [],
        fetch: {
          rawCount: fetchInfo.rawCount,
          keptCount: fetchInfo.keptCount,
          droppedCount: fetchInfo.droppedCount,
          dropCounts,
        },
      },
      null,
      2,
    ),
  );
} else if (kind === "critic") {
  const training = out.training || {};
  const validation = out.validation || {};
  const metrics = validation.metrics || {};
  const baseline = (validation.baseline && validation.baseline.metrics) || {};
  const delta = validation.delta || {};
  const fetchInfo = out.fetch || {};
  const dropCounts = {};
  for (const d of fetchInfo.dropReasons || []) {
    dropCounts[d.reason] = (dropCounts[d.reason] || 0) + 1;
  }
  console.log(
    JSON.stringify(
      {
        kind: "critic",
        logDir: match.path,
        outputJson: path.join(match.path, "output.json"),
        outputMd: path.join(match.path, "output.md"),
        subreddit: out.subreddit,
        executionId: out.executionId,
        durationMs: out.durationMs,
        finalPrompt: out.finalPrompt,
        initialPrompt: out.initialPrompt,
        training: {
          totalPosts: training.totalPosts,
          convergedCount: training.convergedCount,
          avgIterations: training.avgIterations,
          hardCasesCount: (training.hardCases || []).length,
          hardCases: (training.hardCases || []).map((h) => ({
            postId: h.postId,
            postTitle: h.postTitle,
            iterations: h.iterations,
            lastMisclassified: (h.lastMisclassified || []).map((m) => ({
              actualBucket: m.actualBucket,
              actualScore: m.actualScore,
              sonnetScore: m.sonnetScore,
              commentBodySnippet: (m.commentBody || "").slice(0, 120),
            })),
          })),
        },
        validation: {
          classificationAccuracy: metrics.classificationAccuracy,
          baselineAccuracy: baseline.classificationAccuracy,
          deltaAccuracy: delta.classificationAccuracy,
          positiveMeanScore: metrics.positiveMeanScore,
          baselinePositiveMeanScore: baseline.positiveMeanScore,
          negativeMeanScore: metrics.negativeMeanScore,
          baselineNegativeMeanScore: baseline.negativeMeanScore,
          scoreGap: metrics.scoreGap,
          baselineScoreGap: baseline.scoreGap,
          deltaScoreGap: delta.scoreGap,
          spearman: metrics.spearman,
          baselineSpearman: baseline.spearman,
          deltaSpearman: delta.spearman,
        },
        split: out.split || {},
        fetch: {
          rawCount: fetchInfo.rawCount,
          keptCount: fetchInfo.keptCount,
          droppedCount: fetchInfo.droppedCount,
          dropCounts,
        },
      },
      null,
      2,
    ),
  );
} else if (kind === "critic-multi") {
  const summaryPath = path.join(match.path, "multi-seed-summary.json");
  if (!fs.existsSync(summaryPath)) {
    console.error(`critic-multi: no multi-seed-summary.json in ${match.path}`);
    process.exit(3);
  }
  const summary = JSON.parse(fs.readFileSync(summaryPath, "utf-8"));
  console.log(
    JSON.stringify(
      {
        kind: "critic-multi",
        logDir: match.path,
        summaryPath,
        ...summary,
      },
      null,
      2,
    ),
  );
}
