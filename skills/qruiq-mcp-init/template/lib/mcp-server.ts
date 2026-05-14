import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

/**
 * Create an MCP server with tools for the authenticated user.
 * Replace the example tool below with your app's actual resources.
 *
 * Guidelines:
 * - Every API resource should have full CRUD tools (list, get, create, update, delete)
 * - All queries must be scoped to userId
 * - Return JSON.stringify(result, null, 2) as text content
 * - Return { isError: true } for not-found / permission errors
 * - Tool descriptions should be detailed — the AI reads them to understand capabilities
 */
export function createMcpServer(userId: string) {
  const server = new McpServer({
    name: "__APP_NAME__",
    version: "1.0.0",
  });

  // Example: replace with your actual tools
  // server.tool("list_items", "List all items for the current user", {
  //   categoryId: z.string().optional().describe("Filter by category ID"),
  // }, async ({ categoryId }) => {
  //   const items = await prisma.item.findMany({ where: { userId } });
  //   return { content: [{ type: "text" as const, text: JSON.stringify(items, null, 2) }] };
  // });

  return server;
}
