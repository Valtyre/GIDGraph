const DEFAULT_LOCAL_API_BASE_URL = "http://localhost:8000";
const DEFAULT_PROD_API_BASE_URL = "https://api.gidgraph.com";

function parseBooleanEnv(value: string | undefined): boolean | undefined {
  if (value === undefined) {
    return undefined;
  }

  const normalized = value.trim().toLowerCase();

  if (normalized === "true") {
    return true;
  }

  if (normalized === "false") {
    return false;
  }

  return undefined;
}

const envToggle = parseBooleanEnv(process.env.NEXT_PUBLIC_USE_LOCAL_BACKEND);

export const USE_LOCAL_BACKEND =
  envToggle ?? process.env.NODE_ENV === "development";

const localApiBaseUrl =
  process.env.NEXT_PUBLIC_LOCAL_API_BASE_URL || DEFAULT_LOCAL_API_BASE_URL;
const prodApiBaseUrl =
  process.env.NEXT_PUBLIC_PROD_API_BASE_URL || DEFAULT_PROD_API_BASE_URL;

export const API_BASE_URL = USE_LOCAL_BACKEND
  ? localApiBaseUrl
  : prodApiBaseUrl;

export function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}
