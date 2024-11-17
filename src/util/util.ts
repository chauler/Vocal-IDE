import path from "path";

export const rootDir = path.normalize(`${path.dirname(__filename)}${path.sep}..`);

export function isString(value: unknown): value is string {
    return typeof value === "string";
}

export function isValidObject(value: unknown): value is Record<string, unknown> {
    return typeof value === "object" && value !== null;
}
