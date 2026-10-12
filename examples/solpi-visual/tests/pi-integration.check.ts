import { execFileSync } from "node:child_process";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { CONFIG_DIR_NAME, createAgentSession, DefaultResourceLoader, SessionManager, SettingsManager, type AgentSession } from "@earendil-works/pi-coding-agent";
import { fauxAssistantMessage, fauxProvider, fauxToolCall } from "@earendil-works/pi-ai/providers/faux";
import { getCurrentSystemPrompt, getSystemMessageText, type TranscriptContext } from "@earendil-works/pi-ai";
import { expect, it } from "vitest";


it("loads the isolated example in real Pi 1.0.4 and delivers a crop to the next request", async () => {
	const cwd = await mkdtemp(join(tmpdir(), "sol-pi-scene-package-"));
	const agentDir = join(cwd, "agent");
	let session: AgentSession | undefined;
	try {
		await mkdir(agentDir);
		await mkdir(join(cwd, CONFIG_DIR_NAME));
		await writeFile(join(cwd, CONFIG_DIR_NAME, "solpi-visual.json"), JSON.stringify({
			version: 1,
			localEditScope: true, magnify: true, awaitRender: true,
		}));
		execFileSync("python3", ["-c", "from PIL import Image; import sys; Image.new('RGB',(8,8),'blue').save(sys.argv[1])", join(cwd, "render.png")]);
		const faux = fauxProvider({ provider: "scene-package-test", api: "scene-package-test-api", models: [{ id: "vision", input: ["text", "image"] }] });
		const requests: TranscriptContext[] = [];
		faux.setResponses([
			(context) => { requests.push(structuredClone(context)); return fauxAssistantMessage(fauxToolCall("magnify", { image: "render.png", bbox: [1, 1, 5, 5] }), { stopReason: "toolUse" }); },
			(context) => { requests.push(structuredClone(context)); return fauxAssistantMessage("inspected crop"); },
			(context) => { requests.push(structuredClone(context)); return fauxAssistantMessage("second user turn"); },
		]);
		const settingsManager = SettingsManager.inMemory({ compaction: { enabled: false }, retry: { enabled: false } }, { projectTrusted: true });
		const resourceLoader = new DefaultResourceLoader({
			cwd, agentDir, settingsManager,
			additionalExtensionPaths: [join(process.cwd(), "src/index.ts")],
			extensionFactories: [{ name: "scene-test-provider", factory: (pi) => pi.registerProvider(faux.provider) }],
			noExtensions: true, noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true,
			systemPrompt: "Original scene task.",
		});
		await resourceLoader.reload();
		expect(resourceLoader.getExtensions().errors).toEqual([]);
		const sessionManager = SessionManager.create(cwd, join(agentDir, "sessions"));
		({ session } = await createAgentSession({ cwd, agentDir, model: faux.getModel(), thinkingLevel: "off", resourceLoader, sessionManager, settingsManager }));
		const errors: unknown[] = [];
		await session.bindExtensions({ onError: (error) => errors.push(error) });
		expect(session.getActiveToolNames()).toEqual(expect.arrayContaining(["edit", "write", "magnify"]));
		expect(session.getActiveToolNames()).not.toContain("obs_recall");
		expect(session.getActiveToolNames()).not.toContain("update_plan");
		await session.prompt("inspect the existing render", { expandPromptTemplates: false });
		await session.prompt("finish", { expandPromptTemplates: false });
		expect(requests).toHaveLength(3);
		for (const request of requests) {
			const prompt = getCurrentSystemPrompt(request.messages);
			const transcriptPrompt = request.messages.filter((m) => m.role === "system").map(getSystemMessageText).join("\n");
			expect(transcriptPrompt.match(/\[SoL-Pi Visual\]/g)).toHaveLength(1);
			expect(prompt).toContain("Original scene task.");
			expect(prompt?.match(/\[SoL-Pi Visual\]/g)).toHaveLength(1);
			expect(prompt).toContain("Local edit scope strategy:");
			expect(prompt).toContain("Local visual evidence before uncertain local edits:");
			expect(prompt).toContain("When launching a render/build command");
		}
		const crop = requests[1]?.messages.find((message) => message.role === "toolResult" && message.toolName === "magnify");
		expect(crop?.role).toBe("toolResult");
		if (crop?.role !== "toolResult") throw new Error("Missing magnify result");
		expect(crop.isError).toBeFalsy();
		expect(crop.content.filter((block) => block.type === "image")).toHaveLength(1);
		expect(errors).toEqual([]);
		expect(session.isIdle).toBe(true);
	} finally {
		session?.dispose();
		await rm(cwd, { recursive: true, force: true });
	}
}, 30_000);
