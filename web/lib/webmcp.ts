/**
 * Current WebMCP imperative API (W3C WebML CG draft, Chrome origin trial).
 *
 * Use document.modelContext.registerTool(tool, { signal }).
 * Do not call provideContext(), clearContext(), or unregisterTool() —
 * those older methods are obsolete. Tear down with AbortSignal instead.
 *
 * Prefer document.modelContext; navigator.modelContext is a deprecated alias.
 * @see https://webmachinelearning.github.io/webmcp/
 * @see https://developer.chrome.com/docs/ai/webmcp/imperative-api
 */

export type JsonSchemaObject = {
  type: "object";
  properties: Record<string, unknown>;
  required?: string[];
};

export type ModelContextTool = {
  name: string;
  title?: string;
  description: string;
  inputSchema: JsonSchemaObject;
  annotations?: {
    readOnlyHint?: boolean;
    untrustedContentHint?: boolean;
  };
  execute: (
    input: Record<string, unknown>,
    options?: { signal?: AbortSignal },
  ) => Promise<string>;
};

export type ModelContext = {
  registerTool: (
    tool: ModelContextTool,
    options?: { signal?: AbortSignal },
  ) => Promise<void>;
  getTools?: () => Promise<Array<{ name: string }>>;
};

export function getModelContext(): ModelContext | undefined {
  if (typeof document === "undefined") return undefined;
  const doc = document as Document & { modelContext?: ModelContext };
  if (doc.modelContext) return doc.modelContext;
  const nav = navigator as Navigator & { modelContext?: ModelContext };
  return nav.modelContext;
}
