import { defineConfig } from "vitest/config";

// Dedicated names keep example tests outside the parent package's default scan.
export default defineConfig({ test: { include: ["tests/**/*.check.ts"] } });
