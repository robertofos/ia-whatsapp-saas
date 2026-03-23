import { useRef, useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import {  approveMessage,  rejectMessage,  editAndApproveMessage,  sendManualMessage,} from "../services/messageService";
import api from "../services/api";
import "../styles/inbox.css";
import { getConversations,
        getConversationDetail,
        getConversationMessages

 } from "../services/messageService";

const FILTERS = {
  ALL: "all",
  UNREAD: "unread",
  PENDING_AI: "pending_ai",
};
// TODO remover essa parte do código e usar apenas a obtenção da conversa selecionada a partir da lista de conversas carregadas do backend quando a integração estiver completa.


export default function Inbox() {
const [conversations, setConversations] = useState([]);
const [selectedConversationId, setSelectedConversationId] = useState(null);
const [search, setSearch] = useState("");
const [manualMessage, setManualMessage] = useState("");
const [activeFilter, setActiveFilter] = useState(FILTERS.ALL);
const [loadingConversations, setLoadingConversations] = useState(false);
const [messages, setMessages] = useState([]);
const [loadingMessages, setLoadingMessages] = useState(false);
const messagesContainerRef = useRef(null);

const [conversationDetail, setConversationDetail] = useState(null);
const [loadingConversationDetail, setLoadingConversationDetail] = useState(false);

// state para controlar ações de aprovação, rejeição e edição de mensagens geradas pela IA
const [loadingAction, setLoadingAction] = useState(null);
const [isEditingAi, setIsEditingAi] = useState(false);
const [aiDraft, setAiDraft] = useState("");

// função para rejeitar a mensagem gerada pela IA e remover a sugestão da conversa
const handleRejectAi = async () => {
  if (!pendingAiMessage) return;

  try {
    setLoadingAction("reject");

    await rejectMessage(pendingAiMessage.id);

    setIsEditingAi(false);
    setAiDraft("");
    await refreshInboxData();
    await refreshSelectedConversation();
  } catch (error) {
    console.error("Erro ao rejeitar mensagem:", error);
    const detail = error?.response?.data?.detail || "Erro ao rejeitar mensagem";
    alert(detail);
  } finally {
    setLoadingAction(null);
  }
};
// função para formatar a data das mensagens e exibir um separador de data no painel de mensagens
const formatDayLabel = (dateKey) => {
  const date = new Date(dateKey);

  return date.toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};
// função para carregar mensagens de uma conversa específica, usada tanto no carregamento inicial das mensagens
//  quando a conversa é selecionada, quanto após ações de aprovação/rejeição/edição de mensagens geradas pela IA
//  para atualizar o painel de mensagens com o conteúdo mais recente do backend.
const loadConversationMessages = async (
  conversationIdParam = selectedConversationId,
  { silent = false } = {}
) => {
  if (!conversationIdParam) return;

  try {
    if (!silent) setLoadingMessages(true);

    const data = await getConversationMessages(conversationIdParam);
    setMessages(data || []);
  } catch (error) {
    console.error("Erro ao carregar mensagens:", error);
  } finally {
    if (!silent) setLoadingMessages(false);
  }
};

//  função para recarregar os detalhes da conversa selecionada, incluindo as mensagens e
//  outras informações relevantes, garantindo que o operador veja a versão mais atualizada 
// da conversa após interagir com as sugestões de IA.
const refreshSelectedConversation = async () => {
  if (!selectedConversationId) return;

  await loadConversationMessages(selectedConversationId);

  // só chama se esse endpoint existir no seu projeto
  // await loadConversationDetail(selectedConversationId);
   requestAnimationFrame(() => {
    scrollMessagesToBottom();
  });
};

useEffect(() => {
  scrollMessagesToBottom();
}, [messages]);
// função para rolar o painel de mensagens para a última mensagem, 
const scrollMessagesToBottom = () => {
  if (!messagesContainerRef.current) return;

  messagesContainerRef.current.scrollTop =
    messagesContainerRef.current.scrollHeight;
};
// função para recarregar tanto a lista de conversas no painel lateral quanto os detalhes da conversa selecionada,
const refreshInboxData = async () => {
  await loadConversations({ silent: true });
  await refreshSelectedConversation();
};

// função para carregar a lista de conversas do backend, aplicada tanto no carregamento inicial da página quanto após ações que podem alterar o estado das conversas 
// para garantir que o painel lateral de conversas reflita as informações mais recentes,como contagem de mensagens não lidas e status de pendência de IA.

const loadConversations = async ({ silent = false } = {}) => {
  try {
    if (!silent) setLoadingConversations(true);

    const data = await getConversations({
      limit: 20,
      offset: 0,
    });

    const results = data.results || [];

    setConversations(results);

    if (results.length > 0 && !selectedConversationId) {
      setSelectedConversationId(results[0].id);
    }
  } catch (error) {
    console.error("Erro ao carregar conversas:", error);
  } finally {
    setLoadingConversations(false);
  }
};
// carregamento inicial das conversas quando o componente é montado
useEffect(() => {
  loadConversations();
}, []);
// carregamento das mensagens sempre que a conversa selecionada for alterada

useEffect(() => {
  const loadMessages = async () => {
    if (!selectedConversationId) {
      setMessages([]);
      return;
    }

    try {
      setLoadingMessages(true);

      const data = await getConversationMessages(selectedConversationId);
      setMessages(data || []);
    } catch (error) {
      console.error("Erro ao carregar mensagens:", error);
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  };

  loadMessages();
}, [selectedConversationId]);

/* carregamento dos detalhes da conversa selecionada (incluindo mensagens e outras informações relevantes) 
 sempre que a conversa selecionada for alterada, garantindo que o painel de mensagens e detalhes
  mostre as informações mais atualizadas do backend,
  especialmente após interações com sugestões de IA.*/
useEffect(() => {
  const loadConversationDetail = async () => {
    if (!selectedConversationId) {
      setConversationDetail(null);
      return;
    }

    try {
      setLoadingConversationDetail(true);

      
      const data = await getConversationDetail(selectedConversationId);
      setConversationDetail(data);
    } catch (error) {
      console.error("Erro ao carregar detalhe da conversa:", error);
      setConversationDetail(null);
    } finally {
      setLoadingConversationDetail(false);
    }
  };

  loadConversationDetail();
}, [selectedConversationId]);
// obtenção da conversa selecionada a partir da lista de conversas carregadas do backend,
  const selectedConversation =
   conversations.find((item) => item.id === selectedConversationId) || null;
/* obtenção da conversa selecionada a partir de uma lista mockada,
  usada para desenvolvimento e testes antes da implementação completa do backend,
  garantindo que o painel de mensagens e detalhes possa ser desenvolvido e testado com dados consistentes mesmo sem a integração total com o backend.
 TODO remover essa parte do código e usar apenas a obtenção da conversa selecionada a partir da lista de conversas carregadas do backend quando a integração estiver completa.*/

  // função para filtrar a lista de conversas com base no termo de busca e no filtro ativo (todas, não lidas, pendentes de IA),
  const filteredConversations = useMemo(() => {
    const term = search.toLowerCase().trim();

    let baseList = [...conversations];

    if (activeFilter === FILTERS.UNREAD) {
      baseList = baseList.filter((conversation) => conversation.unread > 0);
    }

    if (activeFilter === FILTERS.PENDING_AI) {
      baseList = baseList.filter((conversation) => conversation.pendingAI);
    }

    if (term) {
      baseList = baseList.filter(
        (conversation) =>
          conversation.name.toLowerCase().includes(term) ||
          conversation.phone.toLowerCase().includes(term)
      );
    }

    baseList.sort((a, b) => {
      if (a.pendingAI === b.pendingAI) return 0;
      return a.pendingAI ? -1 : 1;
    });

    return baseList;
}, [search, activeFilter, conversations]);
  // contagem de conversas não lidas e pendentes de IA para exibir nos filtros do painel lateral
  const unreadCount = conversations.filter((item) => item.unread > 0).length;
  // contagem de conversas com mensagens geradas pela IA aguardando aprovação para exibir no filtro de pendentes de IA do painel lateral
  const pendingAiCount = conversations.filter((item) => item.pendingAI).length;
  // identificação da mensagem gerada pela IA que está aguardando aprovação na conversa selecionada,
  //  para exibir a sugestão de resposta no painel de mensagens e permitir que o operador aprove, edite ou rejeite a mensagem antes de enviá-la ao cliente.
  const pendingAiMessage = [...messages].reverse().find((message) =>
        message.review_status === "pending" &&
        (message.ai_generated === true || message.sender_type === "ai"));

  // efeito para atualizar o rascunho da mensagem de IA sempre que a mensagem pendente for alterada,      
  useEffect(() => {
  if (pendingAiMessage) {
    setAiDraft(pendingAiMessage.content || "");
  } else {
    setAiDraft("");
    setIsEditingAi(false);
  }
}, [pendingAiMessage]);
  
// variável booleana para indicar se existe uma mensagem gerada pela IA aguardando aprovação,
  //  usada para controlar a exibição da sugestão de resposta e das ações de aprovação/edição/rejeição no painel de mensagens.
  const hasPendingAiSuggestion = Boolean(pendingAiMessage);

  // função para selecionar uma conversa da lista, atualizando o estado da conversa selecionada
  //  e limpando os rascunhos de mensagens de IA e manuais para garantir que o operador comece com um estado limpo ao mudar de conversa.
  const handleSelectConversation = (conversationId) => {
    setSelectedConversationId(conversationId);
    setAiDraft("");
    setManualMessage("");
  };
  // função para enviar uma mensagem manualmente digitada pelo operador, associada à conversa selecionada,
  const handleSendManualMessage = async () => {
  if (!selectedConversationId) return;
  // validação para garantir que a mensagem não seja vazia ou composta apenas por espaços em branco antes de tentar enviá-la ao backend.
  const content = manualMessage.trim();
  if (!content) return;
  // chamada da função de serviço para enviar a mensagem manual ao backend, passando o ID da conversa selecionada e o conteúdo da mensagem,
  try {
    setLoadingAction("manual-send");
    await sendManualMessage(selectedConversationId, content);
    setManualMessage("");
    await refreshInboxData();
    // uso de requestAnimationFrame para garantir que o scroll para a última mensagem ocorra após a atualização do estado 
    // e renderização das mensagens, proporcionando uma experiência mais fluida ao operador.
    requestAnimationFrame(() => {
      scrollMessagesToBottom();
    });
  } catch (error) {
    console.error("Erro ao enviar mensagem manual:", error);
    const detail =
      error?.response?.data?.detail || "Erro ao enviar mensagem manual";
    alert(detail);
  } finally {
    setLoadingAction(null);
  }
};
// função para aprovar a mensagem gerada pela IA, enviando-a ao cliente, ou editar o conteúdo sugerido pela IA 
// e aprovar a mensagem editada antes de enviá-la ao cliente,
  const handleApproveOrEditAi = async () => {
  if (!pendingAiMessage) return;

  const originalContent = pendingAiMessage.content || "";
  const editedContent = aiDraft.trim();

  if (!editedContent) {
    alert("Mensagem não pode ficar vazia.");
    return;
  }

  try {
    setLoadingAction("approve");

    if (editedContent === originalContent.trim()) {
      await approveMessage(pendingAiMessage.id);
    } else {
      await editAndApproveMessage(pendingAiMessage.id, editedContent);
    }

    setAiDraft("");
    await refreshSelectedConversation();
    await refreshInboxData();
  } catch (error) {
    console.error("Erro ao aprovar/enviar mensagem:", error);
    const detail =
      error?.response?.data?.detail || "Erro ao enviar mensagem";
    alert(detail);
  } finally {
    setLoadingAction(null);
  }
};
  // função para determinar o lado da mensagem (esquerda para mensagens recebidas, direita para mensagens enviadas) com base nas propriedades de direção e tipo do remetente,
  const getMessageSide = (message) => {
  if (message.direction === "outbound") return "right";
  if (message.direction === "inbound") return "left";

  if (message.sender_type === "tenant") return "right";
  if (message.sender_type === "customer") return "left";

  return "left";
  };
  // mapeamento das mensagens carregadas do backend para o formato necessário para exibição no painel de mensagens,
  //  incluindo a determinação do lado da mensagem, formatação do horário e inclusão do conteúdo original da mensagem 
  // para futuras ações de aprovação/edição/rejeição.
  const chatMessages = messages.map((message) => ({
    id: message.id,
    text: message.content || message.body || message.text || "",
    time: (message.timestamp || message.created_at)
      ? new Date(message.created_at).toLocaleTimeString("pt-BR", {
          hour: "2-digit",
          minute: "2-digit",
        })
      : "",
    side: getMessageSide(message),
    raw: message,
  }));
// efeito para rolar o painel de mensagens para a última mensagem sempre que a conversa selecionada for alterada ou quando novas mensagens forem carregadas, garantindo que o operador veja as mensagens mais recentes sem precisar rolar manualmente.
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop =
        messagesContainerRef.current.scrollHeight;
    }
  }, [selectedConversationId, chatMessages.length]);

  // função para agrupar as mensagens por data, criando um objeto onde cada chave é uma data (no formato YYYY-MM-DD) e o valor é um array de mensagens correspondentes a essa data,
  const groupMessagesByDate = (messages) => {
  const groups = {};
// iteração sobre as mensagens para agrupá-las por data, usando a data de criação ou timestamp da mensagem para determinar a chave de agrupamento, e garantindo que as mensagens sejam organizadas cronologicamente dentro de cada grupo.
  messages.forEach((msg) => {
    const date = new Date(
      msg.raw?.timestamp || msg.raw?.created_at
    );

    const key = date.toISOString().split("T")[0]; // YYYY-MM-DD

    if (!groups[key]) {
      groups[key] = [];
    }

    groups[key].push(msg);
  });
  return groups;
};
  // uso de useMemo para memorizar o resultado do agrupamento das mensagens por data, evitando cálculos desnecessários em re-renderizações quando as mensagens não forem alteradas, e garantindo que o agrupamento seja atualizado apenas quando a lista de mensagens (chatMessages) for modificada.
  const groupedMessages = useMemo(() => {
    return groupMessagesByDate(chatMessages);
  }, [chatMessages]); 

const { authUser, tenant, signOut } = useAuth();
const navigate = useNavigate();

function handleLogout() {
  signOut();
  navigate("/login");
}


  // renderização do componente Inbox, incluindo o cabeçalho, painel lateral de conversas com filtros e campo de busca, 
  // e painel principal de mensagens com detalhes da conversa selecionada, 
  // ações para mensagens geradas pela IA e campo para envio de mensagens manuais,
  return (
    <div className="inbox-shell">
      <header className="inbox-topbar">
        <div className="inbox-topbar-brand">
          <div className="inbox-topbar-logo">
            {tenant?.name?.[0]?.toUpperCase() || "T"}
          </div>

          <div className="inbox-topbar-brand-text">
            <h1 className="inbox-topbar-title">
              {tenant?.name || "Tenant"}
            </h1>
            <p className="inbox-topbar-subtitle">
              WhatsApp Inbox
            </p>
          </div>
        </div>

        <div className="inbox-topbar-actions">
          <div className="inbox-topbar-user">
            <div className="inbox-topbar-avatar">
              {authUser?.initials || "US"}
            </div>

            <div className="inbox-topbar-user-text">
              <div className="inbox-topbar-user-name">
                {authUser?.name || "Usuário"}
              </div>
              <div className="inbox-topbar-user-role">
                {authUser?.role || "Perfil"}
              </div>
            </div>
          </div>

          {/* 🔥 BOTÃO LOGOUT */}
          <button onClick={handleLogout} className="inbox-topbar-logout">
            Sair
          </button>
        </div>
      </header>
      <main className="grid min-h-[calc(100vh-64px)] grid-cols-1 lg:grid-cols-[360px_minmax(0,1fr)_320px]">
        <aside className="inbox-sidebar">
          <div className="inbox-sidebar__title">Conversas</div>

          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nome ou telefone..."
            className="inbox-search"
          />

          <div className="inbox-filters">
            <button
              onClick={() => setActiveFilter(FILTERS.ALL)}
              className={`inbox-filter-btn ${
                activeFilter === FILTERS.ALL && "inbox-filter-btn--active"
              }`}
            >
              Todas
            </button>

            <button
              onClick={() => setActiveFilter(FILTERS.UNREAD)}
              className={`inbox-filter-btn ${
                activeFilter === FILTERS.UNREAD && "inbox-filter-btn--active"
              }`}
            >
              Não lidas {unreadCount > 0 && `(${unreadCount})`}
            </button>

            <button
              onClick={() => setActiveFilter(FILTERS.PENDING_AI)}
              className={`inbox-filter-btn ${
                activeFilter === FILTERS.PENDING_AI && "inbox-filter-btn--active"
              }`}
            >
              Pendentes IA {pendingAiCount > 0 && `(${pendingAiCount})`}
            </button>
          </div>

          <div
            className="inbox-conversation-list"
            style={{ height: "calc(100vh - 220px)" }}
          >
            {loadingConversations ? (
              <div className="inbox-empty">Carregando conversas...</div>
            ) : filteredConversations.length === 0 ? (
              <div className="inbox-empty">
                Nenhuma conversa encontrada para este filtro.
              </div>
            ) : (
              filteredConversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => handleSelectConversation(conversation.id)}
                  className={`inbox-conversation-item ${
                    selectedConversation?.id === conversation.id &&
                    "inbox-conversation-item--active"
                  }`}
                >
                  <div className="inbox-conversation-header">
                    <div className="min-w-0">
                      <div className="inbox-conversation-name">
                        {conversation.name}
                      </div>
                      <div className="inbox-conversation-phone">
                        {conversation.phone}
                      </div>
                    </div>

                    <div className="inbox-conversation-time">
                      {conversation.time}
                    </div>
                  </div>

                  <div className="inbox-conversation-channel">
                    {conversation.channel}
                  </div>

                  <div className="inbox-conversation-footer">
                    <div className="flex items-center gap-2">
                      {conversation.pendingAI && (
                        <span className="tag tag--ai">Pendente IA</span>
                      )}
                    </div>

                    {conversation.unread > 0 && (
                      <span className="badge badge--unread">
                        {conversation.unread}
                      </span>
                    )}
                  </div>
                </button>
              ))
            )}
          </div>
        </aside>
        <section className="inbox-chat-wrapper">
          {selectedConversation ? (
            <div className="inbox-chat-container">

              {/* HEADER */}
              <div className="inbox-chat-header">
                <div>
                  <div className="inbox-chat-title">
                    {selectedConversation?.name}
                  </div>
                  <div className="inbox-chat-subtitle">
                    {selectedConversation?.phone} • {selectedConversation?.channel}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {selectedConversation?.pendingAI && (
                    <span className="tag--ai-pending">
                      Aguardando aprovação IA
                    </span>
                  )}

                </div>
              </div>

              {/* MESSAGES */}
              <div
                ref={messagesContainerRef}
                className="inbox-messages"
                style={{ maxHeight: "calc(100vh - 220px)" }}
              >

                {loadingMessages && (
                  <div className="flex justify-center">
                    <span className="inbox-date-label">
                      Carregando mensagens...
                    </span>
                  </div>
                )}

                {!loadingMessages && chatMessages.length === 0 && (
                  <div className="text-sm text-gray-400 text-center">
                    Nenhuma mensagem encontrada.
                  </div>
                )}

                {!loadingMessages &&
                  Object.entries(groupedMessages).map(([dateKey, messages]) => (
                    <div key={dateKey}>
                      <div className="inbox-date-divider">
                        <span className="inbox-date-label">
                          {formatDayLabel(dateKey)}
                        </span>
                      </div>

                      {messages.map((message) => {
                        const isRejected =
                          (message.raw?.sender_type === "ai" ||
                            message.raw?.ai_generated === true) &&
                          message.raw?.review_status === "rejected";

                        return (
                          <div
                            key={message.id}
                            className={`message-row ${
                              message.side === "right"
                                ? "message-row--right"
                                : "message-row--left"
                            }`}
                          >
                            <div
                              className={`message-bubble ${
                                isRejected
                                  ? "message-bubble--rejected"
                                  : message.side === "right"
                                  ? "message-bubble--me"
                                  : "message-bubble--other"
                              }`}
                            >
                              {isRejected && (
                                <div className="text-[11px] text-red-600 mb-1">
                                  Sugestão rejeitada
                                </div>
                              )}

                              {message.text}

                              <div
                                className={`message-time ${
                                  message.side === "right"
                                    ? "message-time--me"
                                    : ""
                                }`}
                              >
                                {message.time}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ))}
              </div>

              {/* INPUT + IA */}
              <div className="border-t border-gray-200 bg-gray-50 p-4">

                {hasPendingAiSuggestion && (
                  <div className="inbox-ai-panel">
                    <div className="mb-2 flex justify-between">
                      <div>
                        <div className="inbox-ai-title">Sugestão da IA</div>
                        <div className="inbox-ai-subtitle">
                          Revisar antes de enviar
                        </div>
                      </div>
                      <span className="tag--ai-pending">Review mode</span>
                    </div>

                    <textarea
                      className="inbox-ai-textarea"
                      value={aiDraft}
                      onChange={(e) => setAiDraft(e.target.value)}
                    />

                    <div className="mt-3 flex gap-2">
                      <button className="btn-primary">
                        Aprovar e enviar
                      </button>
                      <button className="btn-danger">
                        Rejeitar
                      </button>
                    </div>
                  </div>
                )}

                <div className="inbox-input-area">
                  <input
                    type="text"
                    value={manualMessage}
                    onChange={(e) => setManualMessage(e.target.value)}
                    placeholder="Escreva uma mensagem..."
                    className="inbox-input"
                  />

                  <button className="btn-primary">
                    Enviar
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="inbox-empty">
              Selecione uma conversa para visualizar o chat.
            </div>
          )}
        </section>
        <aside className="inbox-details">
          {selectedConversation ? (
            <>
              <div className="inbox-details__header">
                <div className="inbox-details__title">Cliente</div>
              </div>

              <div className="inbox-details__content">
                <div className="details-card details-card--muted">
                  <div className="customer-summary">
                    <div className="customer-summary__avatar">
                      {conversationDetail?.customer?.name}
                    </div>

                    <div>
                      <div className="customer-summary__name">
                        {conversationDetail?.customer?.name}
                      </div>

                      <div className="customer-summary__meta">
                        {conversationDetail?.customer?.customer_since
                          ? `Cliente desde ${new Date(
                              conversationDetail.customer.customer_since
                            ).toLocaleDateString("pt-BR", {
                              month: "2-digit",
                              year: "numeric",
                            })}`
                          : ""}
                      </div>
                    </div>
                  </div>

                  <div className="customer-fields">
                    <div>
                      <div className="customer-field__label">Telefone</div>
                      <div className="customer-field__value">
                        {conversationDetail?.customer?.phone || "-"}
                      </div>
                    </div>

                    <div>
                      <div className="customer-field__label">Canal</div>
                      <div className="customer-field__value">
                        {conversationDetail?.channel?.name || "-"}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="details-card">
                  <div className="details-card__title">Resumo do cliente</div>
                  <p className="details-text">Cliente....</p>
                </div>

                <div className="details-card">
                  <div className="details-card__title">Ações rápidas</div>
                  <div className="details-actions">
                    <button className="btn-ghost-block">Marcar como VIP</button>
                    <button className="btn-ghost-block">Adicionar tag</button>
                    <button className="btn-ghost-block">Ver histórico completo</button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="inbox-details__empty">
              Nenhum cliente selecionado.
            </div>
          )}
        </aside>
        
      </main>
    </div>
  );
}
