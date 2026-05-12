#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const repoRoot = path.resolve(__dirname, "..");
const skillName = "xiaohongshu-ai-publisher";
const npxPackage = "github:pengcong2020520/xhs-publisher-skill";
const sourceSkill = path.join(repoRoot, skillName);
const codexHome = process.env.CODEX_HOME || path.join(os.homedir(), ".codex");
const targetSkillsDir = path.join(codexHome, "skills");
const targetSkill = path.join(targetSkillsDir, skillName);

function main() {
  const [command = "help", ...args] = process.argv.slice(2);
  if (command === "install") return installSkill();
  if (command === "env") return installEnv();
  if (command === "login") return login(args);
  if (command === "check") return checkEnv();
  if (command === "doctor") return doctor();
  return help();
}

function installSkill() {
  assertDirectory(sourceSkill, `Missing bundled skill at ${sourceSkill}`);
  fs.mkdirSync(targetSkillsDir, { recursive: true });
  fs.rmSync(targetSkill, { recursive: true, force: true });
  fs.cpSync(sourceSkill, targetSkill, { recursive: true });
  console.log(`Installed ${skillName} to ${targetSkill}`);
  console.log("");
  console.log("Next:");
  console.log(`  npx ${npxPackage} env`);
  console.log(`  npx ${npxPackage} login`);
  console.log(`  npx ${npxPackage} check`);
}

function installEnv() {
  const installer = firstAvailable(["uv", "pipx"]);
  if (!installer) {
    fail(
      [
        "Neither uv nor pipx is available.",
        "Install one of them first:",
        "  curl -LsSf https://astral.sh/uv/install.sh | sh",
        "  or",
        "  python3 -m pip install --user pipx",
      ].join("\n")
    );
  }

  if (installer === "uv") {
    run("uv", ["tool", "install", "xiaohongshu-cli"], { allowFailure: true });
  } else {
    run("pipx", ["install", "xiaohongshu-cli"], { allowFailure: true });
  }

  if (hasCommand("npm")) {
    run("npm", ["exec", "--yes", "--package", "playwright", "--", "playwright", "install", "chromium"], { allowFailure: true });
  } else {
    console.warn("npm/npx is not available. Install Node.js before generating screenshots.");
  }

  console.log("");
  console.log("Environment bootstrap finished. Run:");
  console.log(`  npx ${npxPackage} login`);
}

function login(args) {
  const mode = args.includes("--browser") ? [] : ["--qrcode"];
  ensureCommand("xhs", "xiaohongshu-cli is missing. Run: npx xhs-publisher-skill env");
  run("xhs", ["login", ...mode], { allowFailure: false });
}

function checkEnv() {
  const skillPath = fs.existsSync(targetSkill) ? targetSkill : sourceSkill;
  const script = path.join(skillPath, "scripts", "check_env.py");
  assertFile(script, `Missing check script at ${script}`);
  run("python3", [script], { allowFailure: false });
}

function doctor() {
  console.log(`CODEX_HOME: ${codexHome}`);
  console.log(`Skill installed: ${fs.existsSync(targetSkill) ? "yes" : "no"}`);
  console.log(`xhs: ${commandPath("xhs") || "missing"}`);
  console.log(`npx: ${commandPath("npx") || "missing"}`);
  console.log(`python3: ${commandPath("python3") || "missing"}`);
}

function help() {
  console.log(`Usage:
  npx ${npxPackage} install   Install the Codex skill into ~/.codex/skills
  npx ${npxPackage} env       Install xiaohongshu-cli and Playwright Chromium
  npx ${npxPackage} login     Login to Xiaohongshu with QR code
  npx ${npxPackage} login --browser
                                    Login with the default browser flow
  npx ${npxPackage} check     Check xhs login and screenshot dependencies
  npx ${npxPackage} doctor    Print local diagnostics
`);
}

function firstAvailable(commands) {
  return commands.find((command) => hasCommand(command));
}

function hasCommand(command) {
  return Boolean(commandPath(command));
}

function commandPath(command) {
  const result = spawnSync("which", [command], { encoding: "utf8" });
  return result.status === 0 ? result.stdout.trim() : "";
}

function ensureCommand(command, message) {
  if (!hasCommand(command)) fail(message);
}

function assertDirectory(directory, message) {
  if (!fs.existsSync(directory) || !fs.statSync(directory).isDirectory()) fail(message);
}

function assertFile(file, message) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) fail(message);
}

function run(command, args, options) {
  const result = spawnSync(command, args, { stdio: "inherit" });
  if (result.status !== 0 && !options.allowFailure) {
    process.exit(result.status || 1);
  }
  if (result.status !== 0) {
    console.warn(`${command} ${args.join(" ")} exited with ${result.status}. Continue after checking the message above.`);
  }
}

function fail(message) {
  console.error(message);
  process.exit(1);
}

main();
