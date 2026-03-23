import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/Login.css";

export default function Login() {
  const navigate = useNavigate();
  const { signIn } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await signIn(username, password);
      navigate("/inbox");
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.response?.data?.non_field_errors?.[0] ||
          "Não foi possível entrar."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-page__container">
        <div className="login-page__grid">
          <div className="login-page__hero">
            <div className="login-page__brand">
              <div className="login-page__logo">IA</div>

              <div>
                <div className="login-page__brand-kicker">Plataforma de</div>
                <h1 className="login-page__title">CRM Social Mídia</h1>
              </div>
            </div>

            <p className="login-page__description">
              Plataforma SaaS de atendimento automatizado para comércios, com IA
              para interagir com seus clientes em múltiplos canais digitais com base em
              contexto, documentos e dados estruturados.
            </p>

            <div className="login-page__image-wrap">
              <img
                src="/login-hero.png"
                alt="Plataforma IA CRM Social Mídia"
                className="login-page__image"
              />
            </div>
          </div>

          <div className="login-page__form-column">
            <div className="login-card">
              <h2 className="login-card__title">Acesse sua conta</h2>

              <form onSubmit={handleSubmit} className="login-form">
                <div className="login-form__group">
                  <label className="login-form__label">Usuário</label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="login-form__input"
                    placeholder="Digite seu usuário"
                  />
                </div>

                <div className="login-form__group">
                  <label className="login-form__label">Senha</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="login-form__input"
                    placeholder="Digite sua senha"
                  />
                </div>

                {error && <div className="login-form__error">{error}</div>}

                <button
                  type="submit"
                  disabled={loading}
                  className="login-form__button"
                >
                  {loading ? "Entrando..." : "Entrar"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}