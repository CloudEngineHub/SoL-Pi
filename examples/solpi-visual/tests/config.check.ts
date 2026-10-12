import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { CONFIG_DIR_NAME } from "@earendil-works/pi-coding-agent";
import { afterEach, expect, it } from "vitest";
import { DEFAULT_CONFIG, loadSceneConfig } from "../src/config.ts";

const roots: string[] = [];
function fixture(config?: unknown) {
  const root = mkdtempSync(join(tmpdir(), "scene-config-"));
  roots.push(root);
  mkdirSync(join(root, CONFIG_DIR_NAME));
  if (config !== undefined) {
    writeFileSync(join(root, CONFIG_DIR_NAME, "solpi-visual.json"), JSON.stringify(config));
  }
  return root;
}
afterEach(() => { for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true }); });

it("leaves SoL-Pi config isolated and the example disabled when its config is absent", () => {
  const root = fixture();
  writeFileSync(join(root, CONFIG_DIR_NAME, "sol-pi.json"), JSON.stringify({ version: 1, actionFusion: true }));
  expect(loadSceneConfig(root)).toEqual(DEFAULT_CONFIG);
});

it("enables each scene option independently", () => {
  for (const key of ["localEditScope", "magnify", "awaitRender"] as const) {
    expect(loadSceneConfig(fixture({ version: 1, [key]: true }))).toEqual({ ...DEFAULT_CONFIG, [key]: true });
  }
});

it("ignores project config before trust approval", () => {
  expect(loadSceneConfig(fixture({ version: 1, magnify: true }), false)).toEqual(DEFAULT_CONFIG);
});

it.each([
  [{ version: 2 }, "version must be 1"],
  [{ version: 1, magnify: "yes" }, "magnify must be boolean"],
  [{ version: 1, actionFusion: true }, "unknown key actionFusion"],
  [[], "JSON object"],
])("rejects invalid or core configuration instead of guessing", (config, error) => {
  expect(() => loadSceneConfig(fixture(config))).toThrow(error);
});
