import { useMemo, useState } from "react";

const FILTERS = {
  ALL: "all",
  UNREAD: "unread",
  PENDING_AI: "pending_ai",
};

const conversationsMock = [
  {
    id: 1,
    name: "João Silva",
    phone: "+55 21 99999-1111",
    channel: "WhatsApp",
    time: "14:32",
    unread: 2,
    pendingAI: true,
    customerSince: "mar/2026",
    lastService: "Hoje às 14:33",
    statusTags: ["Aguardando IA", "Em atendimento", "Cliente recorrente"],
    tags: ["Entrega Barra", "Interesse pizza grande", "Lead quente"],
    summary:
      "Cliente perguntando sobre preço da pizza grande e disponibilidade de entrega na Barra. Histórico indica forte intenção de compra e boa chance de conversão nesta conversa.",
    notes:
      "Cliente costuma responder rápido. Priorizar envio de sabores, tamanhos e taxa de entrega para a Barra.",
    aiSuggestion:
      "Sim! Entregamos na Barra, dependendo da localização exata. Sobre a pizza grande, posso te enviar agora os sabores disponíveis e os valores de cada opção.",
    messages: [
      {
        id: 1,
        side: "left",
        text: "Boa tarde! Gostaria de saber o preço da pizza grande.",
        time: "14:31",
      },
      {
        id: 2,
        side: "right",
        text: "Boa tarde, João! Temos opções a partir de R$ 52. Posso te enviar os sabores disponíveis.",
        time: "14:32 • Enviada",
      },
      {
        id: 3,
        side: "left",
        text: "Sim, por favor. E vocês entregam na Barra?",
        time: "14:33",
      },
    ],
  },
  {
    id: 2,
    name: "Maria Oliveira",
    phone: "+55 21 98888-2222",
    channel: "WhatsApp",
    time: "13:18",
    unread: 0,
    pendingAI: false,
    customerSince: "jan/2026",
    lastService: "Hoje às 13:18",
    statusTags: ["Em atendimento"],
    tags: ["Entrega Copacabana", "Cliente nova"],
    summary:
      "Cliente quer saber se a loja entrega em Copacabana e está avaliando fazer o primeiro pedido.",
    notes:
      "Enviar taxa de entrega e prazo médio antes de oferecer cardápio completo.",
    aiSuggestion:
      "Sim, entregamos em Copacabana em áreas selecionadas. Posso confirmar sua rua e já te passar taxa e prazo estimado.",
    messages: [
      {
        id: 1,
        side: "left",
        text: "Vocês entregam em Copacabana?",
        time: "13:16",
      },
      {
        id: 2,
        side: "right",
        text: "Entregamos sim em áreas selecionadas. Posso confirmar sua rua para te informar a taxa?",
        time: "13:17 • Enviada",
      },
      {
        id: 3,
        side: "left",
        text: "Claro, é na Rua Barata Ribeiro.",
        time: "13:18",
      },
    ],
  },
  {
    id: 3,
    name: "Pedro Santos",
    phone: "+55 21 97777-3333",
    channel: "WhatsApp",
    time: "12:05",
    unread: 1,
    pendingAI: true,
    customerSince: "fev/2026",
    lastService: "Hoje às 12:05",
    statusTags: ["Aguardando IA", "Lead quente"],
    tags: ["Pedido hoje", "Família"],
    summary:
      "Cliente quer fazer um pedido para hoje à noite e demonstra intenção de fechar rapidamente.",
    notes:
      "Oferecer combo família e informar tempo estimado de preparo.",
    aiSuggestion:
      "Perfeito! Posso te sugerir um combo para hoje à noite com pizzas grandes e bebidas. Quer que eu te envie as opções agora?",
    messages: [
      {
        id: 1,
        side: "left",
        text: "Quero fazer um pedido para hoje à noite.",
        time: "12:05",
      },
    ],
  },
  {
    id: 4,
    name: "Ana Costa",
    phone: "+55 21 96666-4444",
    channel: "WhatsApp",
    time: "Ontem",
    unread: 0,
    pendingAI: false,
    customerSince: "dez/2025",
    lastService: "Ontem às 20:41",
    statusTags: ["Resolvido"],
    tags: ["Sem glúten"],
    summary:
      "Cliente perguntou sobre opções sem glúten. Conversa já foi concluída.",
    notes:
      "Caso retorne, encaminhar direto para cardápio especial.",
    aiSuggestion:
      "Temos algumas opções que podem te atender. Posso te enviar os sabores disponíveis e os cuidados de preparo.",
    messages: [
      {
        id: 1,
        side: "left",
        text: "Tem opção sem glúten?",
        time: "Ontem",
      },
    ],
  },
];

function getNowTime() {
  return new Date().toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getInitials(name) {
  return name
    .split(" ")
    .slice(0, 2)
    .map((part) => part[0])
    .join("");
}

export default function InboxPage() {
  const [conversations, setConversations] = useState(conversationsMock);
  const [selectedConversationId, setSelectedConversationId] = useState(1);
  const [search, setSearch] = useState("");
  const [manualMessage, setManualMessage] = useState("");
  const [activeFilter, setActiveFilter] = useState(FILTERS.ALL);

  const selectedConversation =
    conversations.find((item) => item.id === selectedConversationId) || conversations[0];

  const [aiDraft, setAiDraft] = useState(
    conversations.find((item) => item.id === 1)?.aiSuggestion || ""
  );

  const filteredConversations = useMemo(() => {
    const term = search.toLowerCase().trim();

    let baseList = conversations;

    if (activeFilter === FILTERS.UNREAD) {
      baseList = conversations.filter((conversation) => conversation.unread > 0);
    }

    if (activeFilter === FILTERS.PENDING_AI) {
      baseList = conversations.filter((conversation) => conversation.pendingAI);
    }

    if (!term) return baseList;

    return baseList.filter(
      (conversation) =>
        conversation.name.toLowerCase().includes(term) ||
        conversation.phone.toLowerCase().includes(term)
    );
  }, [search, activeFilter, conversations]);

  const unreadCount = conversations.filter((item) => item.unread > 0).length;
  const pendingAiCount = conversations.filter((item) => item.pendingAI).length;

  const handleSelectConversation = (conversationId) => {
    setSelectedConversationId(conversationId);
    const selected = conversations.find((item) => item.id === conversationId);
    setAiDraft(selected?.aiSuggestion || "");
    setManualMessage("");
  };

  const handleApproveAndSend = () => {
    const content = aiDraft.trim();
    if (!content || !selectedConversation) return;

    const now = getNowTime();

    setConversations((current) =>
      current.map((conversation) => {
        if (conversation.id !== selectedConversationId) return conversation;

        const hasAwaitingTag = conversation.statusTags.includes("Aguardando IA");

        return {
          ...conversation,
          pendingAI: false,
          aiSuggestion: "",
          time: now,
          lastService: `Hoje às ${now}`,
          statusTags: hasAwaitingTag
            ? conversation.statusTags.filter((tag) => tag !== "Aguardando IA")
            : conversation.statusTags,
          messages: [
            ...conversation.messages,
            {
              id: Date.now(),
              side: "right",
              text: content,
              time: `${now} • Enviada`,
            },
          ],
        };
      })
    );

    setAiDraft("");
  };

  const handleRejectSuggestion = () => {
    if (!selectedConversation) return;

    setConversations((current) =>
      current.map((conversation) => {
        if (conversation.id !== selectedConversationId) return conversation;

        const hasAwaitingTag = conversation.statusTags.includes("Aguardando IA");

        return {
          ...conversation,
          pendingAI: false,
          aiSuggestion: "",
          statusTags: hasAwaitingTag
            ? conversation.statusTags.filter((tag) => tag !== "Aguardando IA")
            : conversation.statusTags,
        };
      })
    );

    setAiDraft("");
  };

  const handleSendManualMessage = () => {
    const content = manualMessage.trim();
    if (!content || !selectedConversation) return;

    const now = getNowTime();

    setConversations((current) =>
      current.map((conversation) => {
        if (conversation.id !== selectedConversationId) return conversation;

        return {
          ...conversation,
          time: now,
          lastService: `Hoje às ${now}`,
          messages: [
            ...conversation.messages,
            {
              id: Date.now(),
              side: "right",
              text: content,
              time: `${now} • Enviada`,
            },
          ],
        };
      })
    );

    setManualMessage("");
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      <header className="flex h-16 items-center justify-between border-b bg-white px-6">
        <div className="flex items-center gap-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-black text-sm font-bold text-white">
            T
          </div>
          <div>
            <h1 className="text-base font-semibold">Tenant Demo</h1>
            <p className="text-xs text-gray-500">WhatsApp Inbox • Plano Pro</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button className="relative rounded-xl border px-3 py-2 text-sm text-gray-600 hover:bg-gray-50">
            🔔
            <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
              3
            </span>
          </button>

          <div className="flex items-center gap-2 rounded-xl border px-3 py-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200 text-xs font-semibold text-gray-700">
              RS
            </div>
            <div className="text-left">
              <div className="text-sm font-medium">Roberto</div>
              <div className="text-xs text-gray-500">Admin</div>
            </div>
          </div>
        </div>
      </header>

      <main className="grid min-h-[calc(100vh-64px)] grid-cols-1 lg:grid-cols-[320px_minmax(0,1fr)_320px]">
        <aside className="border-r bg-white p-4">
          <div className="mb-4 text-sm font-semibold text-gray-700">Conversas</div>

          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nome ou telefone..."
            className="mb-4 w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
          />

          <div className="mb-3 flex gap-2 overflow-x-auto pb-1">
            <button
              onClick={() => setActiveFilter(FILTERS.ALL)}
              className={`rounded-full px-3 py-1.5 text-xs font-medium ${
                activeFilter === FILTERS.ALL ? "bg-black text-white" : "border text-gray-600"
              }`}
            >
              Todas
            </button>
            <button
              onClick={() => setActiveFilter(FILTERS.UNREAD)}
              className={`rounded-full px-3 py-1.5 text-xs font-medium ${
                activeFilter === FILTERS.UNREAD ? "bg-black text-white" : "border text-gray-600"
              }`}
            >
              Não lidas {unreadCount > 0 ? `(${unreadCount})` : ""}
            </button>
            <button
              onClick={() => setActiveFilter(FILTERS.PENDING_AI)}
              className={`rounded-full px-3 py-1.5 text-xs font-medium ${
                activeFilter === FILTERS.PENDING_AI ? "bg-black text-white" : "border text-gray-600"
              }`}
            >
              Pendentes IA {pendingAiCount > 0 ? `(${pendingAiCount})` : ""}
            </button>
          </div>

          <div className="space-y-2 overflow-y-auto pr-1 lg:h-[calc(100vh-220px)]">
            {filteredConversations.length === 0 && (
              <div className="rounded-2xl border border-dashed p-4 text-sm text-gray-400">
                Nenhuma conversa encontrada para este filtro.
              </div>
            )}

            {filteredConversations.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => handleSelectConversation(conversation.id)}
                className={`w-full rounded-2xl border p-3 text-left transition hover:bg-gray-50 ${
                  selectedConversation?.id === conversation.id
                    ? "border-black bg-gray-50 shadow-sm"
                    : "border-gray-200 bg-white"
                }`}
              >
                <div className="mb-1 flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-semibold">{conversation.name}</div>
                    <div className="truncate text-xs text-gray-500">{conversation.phone}</div>
                  </div>

                  <div className="shrink-0 text-xs text-gray-400">{conversation.time}</div>
                </div>

                <div className="mb-2 text-sm text-gray-600">
                  {conversation.messages[conversation.messages.length - 1]?.text}
                </div>

                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {conversation.pendingAI && (
                      <span className="rounded-full bg-amber-100 px-2 py-1 text-[11px] font-medium text-amber-700">
                        Pendente IA
                      </span>
                    )}
                  </div>

                  {conversation.unread > 0 && (
                    <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-black px-1.5 text-[11px] font-semibold text-white">
                      {conversation.unread}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        </aside>

        <section className="bg-[#efeae2] p-4">
          {selectedConversation ? (
            <div className="flex h-full min-h-[500px] flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
              <div className="flex items-center justify-between border-b bg-white px-5 py-4">
                <div>
                  <div className="text-sm font-semibold">{selectedConversation.name}</div>
                  <div className="text-xs text-gray-500">
                    {selectedConversation.phone} • {selectedConversation.channel}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {selectedConversation.pendingAI && (
                    <span className="rounded-full bg-amber-100 px-2.5 py-1 text-[11px] font-medium text-amber-700">
                      Aguardando aprovação IA
                    </span>
                  )}
                  <button className="rounded-lg border px-3 py-2 text-sm text-gray-600 hover:bg-gray-50">
                    Encerrar atendimento
                  </button>
                </div>
              </div>

              <div className="flex-1 space-y-4 overflow-y-auto bg-[#efeae2] px-6 py-5 lg:h-[420px]">
                <div className="flex justify-center">
                  <span className="rounded-full bg-white px-3 py-1 text-xs text-gray-500 shadow-sm">
                    Hoje
                  </span>
                </div>

                {selectedConversation.messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.side === "right" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-2xl px-4 py-3 shadow-sm ${
                        message.side === "right"
                          ? "rounded-br-md bg-[#dcf8c6]"
                          : "rounded-bl-md bg-white"
                      }`}
                    >
                      <p className="text-sm text-gray-800">{message.text}</p>
                      <div
                        className={`mt-2 text-right text-[11px] ${
                          message.side === "right" ? "text-gray-500" : "text-gray-400"
                        }`}
                      >
                        {message.time}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="border-t bg-gray-50 p-4">
                {selectedConversation.pendingAI && (
                  <div className="mb-3 rounded-2xl border border-amber-200 bg-amber-50 p-4">
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <div>
                        <div className="text-sm font-semibold text-amber-900">Sugestão da IA</div>
                        <div className="text-xs text-amber-700">
                          Resposta gerada aguardando revisão do operador
                        </div>
                      </div>
                      <span className="rounded-full bg-amber-100 px-2 py-1 text-[11px] font-medium text-amber-700">
                        Review mode
                      </span>
                    </div>

                    <textarea
                      className="min-h-[96px] w-full rounded-xl border bg-white px-3 py-3 text-sm text-gray-700 outline-none focus:ring-2 focus:ring-amber-200"
                      value={aiDraft}
                      onChange={(e) => setAiDraft(e.target.value)}
                    />

                    <div className="mt-3 flex flex-wrap items-center gap-2">
                      <button
                        onClick={handleApproveAndSend}
                        className="rounded-xl bg-black px-4 py-2 text-sm font-medium text-white hover:opacity-95"
                      >
                        Aprovar e enviar
                      </button>
                      <button className="rounded-xl border px-4 py-2 text-sm font-medium text-gray-700 hover:bg-white">
                        Editar antes de enviar
                      </button>
                      <button
                        onClick={handleRejectSuggestion}
                        className="rounded-xl border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
                      >
                        Rejeitar
                      </button>
                    </div>
                  </div>
                )}

                {!selectedConversation.pendingAI && !selectedConversation.aiSuggestion && aiDraft === "" && (
                  <div className="mb-3 rounded-2xl border border-dashed border-gray-300 bg-white p-4 text-sm text-gray-400">
                    Nenhuma sugestão da IA pendente nesta conversa.
                  </div>
                )}

                <div className="flex items-end gap-3">
                  <textarea
                    placeholder="Escreva uma mensagem manual..."
                    className="min-h-[52px] flex-1 rounded-2xl border bg-white px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-black/10"
                    value={manualMessage}
                    onChange={(e) => setManualMessage(e.target.value)}
                  />
                  <button
                    onClick={handleSendManualMessage}
                    className="rounded-2xl bg-black px-5 py-3 text-sm font-medium text-white hover:opacity-95"
                  >
                    Enviar
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex h-full items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white text-sm text-gray-400">
              Selecione uma conversa para visualizar o chat.
            </div>
          )}
        </section>

        <aside className="border-l bg-white p-4">
          {selectedConversation ? (
            <>
              <div className="mb-4 flex items-center justify-between">
                <div className="text-sm font-semibold text-gray-700">Cliente</div>
                <button className="rounded-lg border px-2.5 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50">
                  Editar
                </button>
              </div>

              <div className="space-y-4 overflow-y-auto pr-1 lg:h-[calc(100vh-120px)]">
                <div className="rounded-2xl border bg-gray-50 p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-black text-sm font-semibold text-white">
                      {getInitials(selectedConversation.name)}
                    </div>
                    <div>
                      <div className="text-sm font-semibold">{selectedConversation.name}</div>
                      <div className="text-xs text-gray-500">
                        Cliente desde {selectedConversation.customerSince}
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 space-y-3 text-sm">
                    <div>
                      <div className="text-xs font-medium uppercase tracking-wide text-gray-400">
                        Telefone
                      </div>
                      <div className="mt-1 text-gray-700">{selectedConversation.phone}</div>
                    </div>
                    <div>
                      <div className="text-xs font-medium uppercase tracking-wide text-gray-400">
                        Canal
                      </div>
                      <div className="mt-1 text-gray-700">WhatsApp Cloud API</div>
                    </div>
                    <div>
                      <div className="text-xs font-medium uppercase tracking-wide text-gray-400">
                        Último atendimento
                      </div>
                      <div className="mt-1 text-gray-700">{selectedConversation.lastService}</div>
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border p-4">
                  <div className="mb-3 text-sm font-semibold">Status do atendimento</div>
                  <div className="flex flex-wrap gap-2">
                    {selectedConversation.statusTags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full bg-gray-100 px-2.5 py-1 text-[11px] font-medium text-gray-700"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border p-4">
                  <div className="mb-3 text-sm font-semibold">Tags</div>
                  <div className="flex flex-wrap gap-2">
                    {selectedConversation.tags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full border px-2.5 py-1 text-[11px] font-medium text-gray-700"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border p-4">
                  <div className="mb-3 text-sm font-semibold">Resumo do cliente</div>
                  <p className="text-sm leading-6 text-gray-600">{selectedConversation.summary}</p>
                </div>

                <div className="rounded-2xl border p-4">
                  <div className="mb-3 text-sm font-semibold">Observações internas</div>
                  <textarea
                    className="min-h-[120px] w-full rounded-xl border px-3 py-3 text-sm text-gray-700 outline-none focus:ring-2 focus:ring-black/10"
                    value={selectedConversation.notes}
                    readOnly
                  />
                </div>

                <div className="rounded-2xl border p-4">
                  <div className="mb-3 text-sm font-semibold">Ações rápidas</div>
                  <div className="grid gap-2">
                    <button className="rounded-xl border px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
                      Marcar como VIP
                    </button>
                    <button className="rounded-xl border px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
                      Adicionar tag
                    </button>
                    <button className="rounded-xl border px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
                      Ver histórico completo
                    </button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex h-full items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white text-sm text-gray-400">
              Nenhum cliente selecionado.
            </div>
          )}
        </aside>
      </main>
    </div>
  );
}
