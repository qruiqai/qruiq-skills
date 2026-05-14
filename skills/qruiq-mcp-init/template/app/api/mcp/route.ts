import { NextRequest } from "next/server";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";

import { authenticateRequest } from "@/lib/api-auth";
import { createMcpServer } from "@/lib/mcp-server";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const auth = await authenticateRequest(req);
  if (!auth) {
    const baseUrl = `${req.headers.get("x-forwarded-proto") || "https"}://${req.headers.get("host")}`;
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: {
        "Content-Type": "application/json",
        "WWW-Authenticate": `Bearer resource_metadata="${baseUrl}/.well-known/oauth-protected-resource"`,
      },
    });
  }

  const server = createMcpServer(auth.userId);
  const transport = new WebStandardStreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
  });

  await server.connect(transport);
  return transport.handleRequest(req);
}

export async function GET() {
  return new Response(JSON.stringify({ error: "Use POST for MCP requests" }), {
    status: 405,
    headers: { "Content-Type": "application/json" },
  });
}

export async function DELETE() {
  return new Response(null, { status: 204 });
}
