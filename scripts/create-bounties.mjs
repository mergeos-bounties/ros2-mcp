import { execSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const REPO = 'mergeos-bounties/ros2-mcp';

function sh(cmd) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function ensureLabel(name, color, description) {
  try {
    sh(`gh label create ${JSON.stringify(name)} --repo ${REPO} --color ${color} --description ${JSON.stringify(description)}`);
  } catch {
    try {
      sh(`gh label edit ${JSON.stringify(name)} --repo ${REPO} --color ${color} --description ${JSON.stringify(description)}`);
    } catch { /* ignore */ }
  }
}

function createIssue(title, body, labels) {
  const dir = mkdtempSync(join(tmpdir(), 'ros2mcp-'));
  const file = join(dir, 'body.md');
  try {
    writeFileSync(file, body, 'utf8');
    const labelFlags = labels.map((l) => `--label ${JSON.stringify(l)}`).join(' ');
    console.log(sh(`gh issue create --repo ${REPO} --title ${JSON.stringify(title)} --body-file ${JSON.stringify(file)} ${labelFlags}`));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

for (const row of [
  ['bounty', '5319E7', 'Eligible for MergeOS MRG bounty'],
  ['bounty: feature', 'A2EEEF', 'Feature bounty'],
  ['mcp', '1D76DB', 'MCP protocol'],
  ['ros2', 'FBCA04', 'ROS2'],
  ['mock', 'C5DEF5', 'Mock backend'],
  ['live', '0E8A16', 'Live ROS2 bridge'],
  ['docs', '0075CA', 'Documentation'],
  ['reward:25-mrg', 'FEF2C0', '25 MRG'],
  ['reward:50-mrg', 'FEF2C0', '50 MRG'],
  ['reward:100-mrg', 'FEF2C0', '100 MRG'],
  ['reward:200-mrg', 'FEF2C0', '200 MRG'],
  ['good first issue', '7057FF', 'Good first issue'],
]) ensureLabel(...row);

const footer = `

## Claim

1. Follow https://github.com/mergeos-bounties  
2. Star https://github.com/mergeos-bounties/mergeos  
3. Star https://github.com/mergeos-bounties/mergeos-contracts
4. Comment: \`I claim this bounty\`  
5. MergeOS [Claim #1](https://github.com/mergeos-bounties/mergeos/issues/1)  
6. PR to **ros2-mcp** with \`Fixes #<n>\`

Policy: [docs/BOUNTY.md](../blob/master/docs/BOUNTY.md)
`;

const issues = [
  { title: '[25 MRG] Docs: Grok + Cursor + Claude MCP setup screenshots', labels: ['bounty', 'bounty: feature', 'docs', 'mcp', 'reward:25-mrg', 'good first issue'],
    body: `## 25 MRG\n\nExpand examples/ with OS-specific paths and screenshots.\n\n## Acceptance\n- [ ] docs/HOST_SETUP.md + README link\n${footer}` },
  { title: '[25 MRG] CLI: ros2-mcp call with JSON file input', labels: ['bounty', 'bounty: feature', 'mcp', 'reward:25-mrg', 'good first issue'],
    body: `## 25 MRG\n\nSupport \`--json-file\` for topic_pub / service_call.\n\n## Acceptance\n- [ ] Tests\n${footer}` },
  { title: '[50 MRG] Live: parse ros2 topic info -v into structured JSON', labels: ['bounty', 'bounty: feature', 'live', 'ros2', 'reward:50-mrg'],
    body: `## 50 MRG\n\nImprove LiveBackend.topic_info / node_info structured fields.\n\n## Acceptance\n- [ ] Mock fixtures of CLI output + tests\n${footer}` },
  { title: '[50 MRG] Mock: multi-robot fleet graph (3 diffs)', labels: ['bounty', 'bounty: feature', 'mock', 'reward:50-mrg'],
    body: `## 50 MRG\n\nSeed option for robot0/1/2 cmd_vel + odom namespaces.\n\n## Acceptance\n- [ ] seed_demo(profile=fleet) + tests\n${footer}` },
  { title: '[100 MRG] Optional rclpy backend (no CLI)', labels: ['bounty', 'bounty: feature', 'live', 'ros2', 'reward:100-mrg'],
    body: `## 100 MRG\n\nBackend using rclpy when importable; fallback to CLI/mock.\n\n## Acceptance\n- [ ] Optional extra [rclpy] docs; CI stays mock-only green\n${footer}` },
  { title: '[100 MRG] MCP resources: topic:// stream snapshot', labels: ['bounty', 'bounty: feature', 'mcp', 'reward:100-mrg'],
    body: `## 100 MRG\n\nExpose FastMCP resources for last message per topic.\n\n## Acceptance\n- [ ] Documented resource URIs + test\n${footer}` },
  { title: '[50 MRG] Safety: live publish allowlist', labels: ['bounty', 'bounty: feature', 'live', 'reward:50-mrg'],
    body: `## 50 MRG\n\nEnv ROS2_MCP_PUB_ALLOWLIST=/cmd_vel,/turtle1/cmd_vel — block others in live.\n\n## Acceptance\n- [ ] Tests for deny path\n${footer}` },
  { title: '[50 MRG] Lappa bridge: HTTP tools to local Lappa sim', labels: ['bounty', 'bounty: feature', 'mcp', 'reward:50-mrg'],
    body: `## 50 MRG\n\nOptional tools ros2_lappa_sim_start / cmd hitting localhost:8840.\n\n## Acceptance\n- [ ] Offline skip if Lappa down; mock tests\n${footer}` },
  { title: '[50 MRG] Actions: list and send_goal stubs', labels: ['bounty', 'bounty: feature', 'ros2', 'reward:50-mrg'],
    body: `## 50 MRG\n\nros2_list_actions + ros2_action_send_goal (mock full, live CLI if possible).\n\n## Acceptance\n- [ ] Tools + tests\n${footer}` },
  { title: '[25 MRG] TF: mock tf tree tool', labels: ['bounty', 'bounty: feature', 'mock', 'reward:25-mrg', 'good first issue'],
    body: `## 25 MRG\n\nros2_tf_tree returns map→odom→base_link.\n\n## Acceptance\n- [ ] Tool + test\n${footer}` },
  { title: '[100 MRG] Docker image ros2-mcp:humble', labels: ['bounty', 'bounty: feature', 'live', 'reward:100-mrg'],
    body: `## 100 MRG\n\nDockerfile with ROS2 Humble + ros2-mcp entrypoint.\n\n## Acceptance\n- [ ] README run instructions\n${footer}` },
  { title: '[50 MRG] Bag: ros2_bag_info mock + live CLI', labels: ['bounty', 'bounty: feature', 'ros2', 'reward:50-mrg'],
    body: `## 50 MRG\n\nTool for bag metadata.\n\n## Acceptance\n- [ ] Mock fixture bag meta JSON\n${footer}` },
  { title: '[25 MRG] Vietnamese README section', labels: ['bounty', 'bounty: feature', 'docs', 'reward:25-mrg', 'good first issue'],
    body: `## 25 MRG\n\n## Tiếng Việt quickstart in README.\n\n## Acceptance\n- [ ] Section present\n${footer}` },
  { title: '[200 MRG] E2E: agent uses MCP to drive mock turtle + evidence', labels: ['bounty', 'bounty: feature', 'mcp', 'mock', 'reward:200-mrg'],
    body: `## 200 MRG\n\nScripted tool sequence pub cmd_vel → pose moves; screenshots/logs.\n\n## Acceptance\n- [ ] Evidence in PR\n${footer}` },
  { title: '[50 MRG] Structured logging + --verbose serve', labels: ['bounty', 'bounty: feature', 'mcp', 'reward:50-mrg'],
    body: `## 50 MRG\n\nLog tool calls to stderr without breaking stdio MCP.\n\n## Acceptance\n- [ ] Docs + tests\n${footer}` },
];

for (const issue of issues) {
  createIssue(issue.title, issue.body, issue.labels);
}
console.log(`Created ${issues.length} issues on ${REPO}`);
