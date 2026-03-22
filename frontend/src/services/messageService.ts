import api from "./api"; // ou o caminho do seu axios já configurado

export async function approveMessage(messageId: number) {
  const response = await api.post(`/messages/${messageId}/approve/`);
  return response.data;
}

export async function rejectMessage(messageId: number) {
  const response = await api.post(`/messages/${messageId}/reject/`);
  return response.data;
}

export async function editAndApproveMessage(messageId: number, content: string) {
  const response = await api.post(`/messages/${messageId}/edit-approve/`, {
    content,
  });
  return response.data;
}

export async function sendManualMessage(conversationId: number, content: string) {
  const response = await api.post(
    `/conversations/${conversationId}/send-manual/`,
    { content }
  );
  return response.data;
}