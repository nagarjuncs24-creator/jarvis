const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type Session = { access_token: string; refresh_token: string; user: { id: string; email: string } };

export async function signIn(email: string, password: string): Promise<Session> {
  const response = await fetch(`${baseUrl}/api/v1/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
  if (!response.ok) throw new Error("Invalid email or password");
  return response.json();
}

export async function createConversation(accessToken: string) {
  const response = await fetch(`${baseUrl}/api/v1/conversations`, { method: "POST", headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" }, body: JSON.stringify({ title: "Voice conversation" }) });
  if (!response.ok) throw new Error("Unable to create conversation");
  return response.json() as Promise<{ id: string }>;
}
