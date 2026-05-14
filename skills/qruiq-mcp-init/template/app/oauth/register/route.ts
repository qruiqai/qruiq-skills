import { NextRequest, NextResponse } from "next/server";

import { prisma } from "@/lib/prisma";

/**
 * OAuth 2.0 Dynamic Client Registration (RFC 7591)
 * MCP clients call this to register before starting OAuth flow.
 */
export async function POST(req: NextRequest) {
  const body = await req.json();
  const { client_name, redirect_uris, grant_types, response_types, token_endpoint_auth_method, scope } = body;

  if (!redirect_uris || !Array.isArray(redirect_uris) || redirect_uris.length === 0) {
    return NextResponse.json(
      { error: "invalid_client_metadata", error_description: "redirect_uris is required" },
      { status: 400 },
    );
  }

  const clientId = `mcp_${crypto.randomUUID()}`;
  const clientSecret = `secret_${crypto.randomUUID()}`;

  await prisma.oAuthClient.create({
    data: {
      clientId,
      clientSecret,
      name: client_name || "MCP Client",
      redirectUris: JSON.stringify(redirect_uris),
      scopes: scope || "tasks:read tasks:write projects:read projects:write",
    },
  });

  return NextResponse.json({
    client_id: clientId,
    client_secret: clientSecret,
    client_name: client_name || "MCP Client",
    redirect_uris,
    grant_types: grant_types || ["authorization_code", "refresh_token"],
    response_types: response_types || ["code"],
    token_endpoint_auth_method: token_endpoint_auth_method || "none",
    scope: scope || "tasks:read tasks:write projects:read projects:write",
  }, { status: 201 });
}
