import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .routes import account, audit, auth, transfers

logger = logging.getLogger("sertao_digital")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # O Compose só inicia a API depois que o PostgreSQL passa no healthcheck.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Sertão Digital - API de Transferências",
    description="Carteira digital com transferências atômicas, autenticação e auditoria.",
    version="1.1.0",
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def home():
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Sertão Digital</title>
            <style>
                :root {
                    --bg: #040a11;
                    --bg-2: #091822;
                    --panel: rgba(10, 17, 24, 0.8);
                    --panel-strong: rgba(8, 12, 18, 0.95);
                    --card: rgba(16, 22, 29, 0.8);
                    --line: rgba(255,255,255,0.07);
                    --text: #ebf5ff;
                    --muted: #9fb3c5;
                    --cyan: #67d0ff;
                    --blue: #1b3c54;
                    --red: #ff4d4d;
                    --orange: #ff8f4a;
                    --shadow: rgba(0, 0, 0, 0.45);
                }

                * { box-sizing: border-box; }

                html, body {
                    margin: 0;
                    min-height: 100%;
                    background:
                        radial-gradient(circle at 20% 15%, rgba(255, 90, 90, 0.12), transparent 13%),
                        radial-gradient(circle at 75% 20%, rgba(75, 232, 255, 0.18), transparent 20%),
                        linear-gradient(180deg, var(--bg) 0%, #030a10 100%);
                    color: var(--text);
                    font-family: Inter, "Segoe UI", Arial, sans-serif;
                }

                body {
                    min-height: 100vh;
                    display: grid;
                    place-items: center;
                    overflow: hidden;
                }

                .scene {
                    position: relative;
                    width: min(1300px, 92vw);
                    min-height: 88vh;
                    padding: 28px 32px 28px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    border: 1px solid rgba(255,255,255,0.06);
                    background: rgba(4, 9, 17, 0.42);
                    box-shadow: 0 35px 120px rgba(0,0,0,0.55);
                    backdrop-filter: blur(6px);
                }

                .topbar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    gap: 16px;
                    z-index: 2;
                }

                .brand {
                    display: inline-flex;
                    align-items: center;
                    gap: 12px;
                    font-weight: 800;
                    letter-spacing: 0.12em;
                    text-transform: uppercase;
                    font-size: 0.8rem;
                    color: rgba(235,245,255,0.9);
                }

                .brand-mark {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, var(--orange), var(--red));
                    box-shadow: 0 0 20px rgba(255, 109, 79, 0.8);
                }

                .nav {
                    display: flex;
                    gap: 8px;
                    align-items: center;
                    color: var(--muted);
                    font-size: 0.8rem;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                }

                .chip {
                    padding: 10px 14px;
                    border-radius: 999px;
                    border: 1px solid rgba(255,255,255,0.08);
                    background: rgba(255,255,255,0.02);
                }

                .hero {
                    position: relative;
                    display: grid;
                    grid-template-columns: 1.1fr 1fr;
                    align-items: center;
                    gap: 32px;
                    flex: 1;
                    z-index: 2;
                }

                .copy {
                    max-width: 600px;
                }

                .eyebrow {
                    display: inline-flex;
                    margin-bottom: 18px;
                    padding: 8px 12px;
                    border: 1px solid rgba(255, 115, 71, 0.4);
                    background: rgba(255, 96, 71, 0.09);
                    color: #ffb7aa;
                    border-radius: 999px;
                    font-size: 0.7rem;
                    font-weight: 700;
                    letter-spacing: 0.14em;
                    text-transform: uppercase;
                }

                h1 {
                    margin: 0;
                    font-size: clamp(2.6rem, 5vw, 5.4rem);
                    line-height: 0.9;
                    letter-spacing: -0.07em;
                    font-weight: 900;
                }

                h1 .soft {
                    color: rgba(235,245,255,0.68);
                    font-weight: 700;
                }

                .lead {
                    margin-top: 20px;
                    color: var(--muted);
                    max-width: 560px;
                    font-size: 1.09rem;
                    line-height: 1.7;
                }

                .actions {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 14px;
                    margin-top: 32px;
                }

                .btn {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 52px;
                    padding: 0 24px;
                    border-radius: 14px;
                    font-weight: 700;
                    text-decoration: none;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }

                .btn:hover {
                    transform: translateY(-1px);
                }

                .btn.primary {
                    background: linear-gradient(135deg, var(--orange), var(--red));
                    color: #130b0b;
                    box-shadow: 0 18px 35px rgba(255, 90, 90, 0.2);
                }

                .btn.secondary {
                    border: 1px solid rgba(255,255,255,0.09);
                    background: rgba(255,255,255,0.02);
                    color: var(--text);
                }

                .visual {
                    position: relative;
                    min-height: 540px;
                    display: grid;
                    place-items: center;
                }

                .screen-cube {
                    position: relative;
                    width: min(560px, 90%);
                    aspect-ratio: 1 / 1;
                    border-radius: 34% 66% 40% 60% / 50% 35% 65% 50%;
                    background: linear-gradient(180deg, rgba(10, 16, 22, 0.92), rgba(4, 10, 17, 0.96));
                    border: 1px solid rgba(255,255,255,0.08);
                    transform: rotate(12deg);
                    box-shadow: inset 0 0 32px rgba(118, 201, 255, 0.08), 0 30px 90px rgba(0,0,0,0.55);
                    overflow: hidden;
                }

                .screen-cube::before,
                .screen-cube::after {
                    content: "";
                    position: absolute;
                    inset: 8% 9% 10% 10%;
                    border-radius: 32% 68% 40% 60% / 48% 35% 65% 52%;
                    background: linear-gradient(180deg, rgba(41, 85, 109, 0.9), rgba(6, 17, 22, 0.9));
                    border: 1px solid rgba(158, 206, 255, 0.08);
                    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
                }

                .screen-cube::after {
                    inset: 23% 19% 25% 18%;
                    border-radius: 0;
                    background: linear-gradient(135deg, rgba(0,0,0,0.1), rgba(255,255,255,0.04));
                    box-shadow: 0 0 0 1px rgba(255,255,255,0.08);
                }

                .panel-grid {
                    position: absolute;
                    inset: 15% 18% 20% 17%;
                    display: grid;
                    grid-template-columns: repeat(2, minmax(120px, 1fr));
                    gap: 18px;
                    transform: rotate(-9deg);
                }

                .panel-tile {
                    position: relative;
                    border-radius: 14px;
                    border: 1px solid rgba(255,255,255,0.12);
                    overflow: hidden;
                    background:
                        linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.45)),
                        radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.3), transparent 18%),
                        linear-gradient(135deg, rgba(35, 70, 80, 0.7), rgba(8, 26, 33, 0.9));
                    box-shadow: inset 0 0 26px rgba(24, 46, 58, 0.65);
                }

                .panel-tile:nth-child(1) {
                    background:
                        linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.45)),
                        linear-gradient(135deg, rgba(255, 66, 66, 0.34), rgba(5, 18, 28, 0.95));
                }

                .panel-tile:nth-child(2) {
                    background:
                        linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.45)),
                        linear-gradient(135deg, rgba(72, 200, 255, 0.28), rgba(10, 22, 28, 0.94));
                }

                .panel-tile:nth-child(3) {
                    background:
                        linear-gradient(180deg, rgba(0,0,0,0.22), rgba(0,0,0,0.44)),
                        linear-gradient(135deg, rgba(255, 176, 71, 0.22), rgba(13, 25, 30, 0.94));
                }

                .panel-tile:nth-child(4) {
                    background:
                        linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.44)),
                        linear-gradient(135deg, rgba(94, 138, 255, 0.18), rgba(8, 18, 25, 0.94));
                }

                .pulse {
                    position: absolute;
                    width: 18px;
                    height: 18px;
                    border-radius: 50%;
                    background: radial-gradient(circle, rgba(255,112,112,1) 0%, rgba(255,112,112,0.2) 70%, transparent 100%);
                    box-shadow: 0 0 16px rgba(255,90,90,0.9);
                    animation: blink 2.4s ease-in-out infinite;
                }

                .pulse.p1 { left: 8%; top: 22%; }
                .pulse.p2 { left: 22%; top: 10%; animation-delay: .3s; }
                .pulse.p3 { right: 12%; top: 26%; animation-delay: .8s; }
                .pulse.p4 { left: 48%; bottom: 12%; animation-delay: 1.1s; }

                .stats {
                    position: absolute;
                    left: 12%;
                    right: 12%;
                    bottom: 8%;
                    display: grid;
                    grid-template-columns: repeat(3, minmax(110px, 1fr));
                    gap: 14px;
                    z-index: 3;
                }

                .stat {
                    background: rgba(6, 12, 18, 0.78);
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 14px;
                    padding: 16px 18px;
                    backdrop-filter: blur(8px);
                }

                .stat strong {
                    display: block;
                    font-size: clamp(1rem, 1.8vw, 1.8rem);
                    color: #ffca8b;
                }

                .stat span {
                    color: var(--muted);
                    font-size: 0.72rem;
                    letter-spacing: 0.09em;
                    text-transform: uppercase;
                }

                @keyframes blink {
                    0%, 100% { opacity: 0.4; transform: scale(0.96); }
                    50% { opacity: 1; transform: scale(1.1); }
                }

                @media (max-width: 960px) {
                    .scene {
                        padding: 22px 18px 26px;
                    }
                    .hero {
                        grid-template-columns: 1fr;
                        padding-top: 16px;
                    }
                    .visual {
                        min-height: 420px;
                    }
                }

                @media (max-width: 620px) {
                    .topbar {
                        align-items: flex-start;
                        flex-direction: column;
                    }
                    .nav {
                        flex-wrap: wrap;
                    }
                    .stats {
                        grid-template-columns: repeat(2, minmax(110px, 1fr));
                    }
                }
            </style>
        </head>
        <body>
            <div class="scene">
                <header class="topbar">
                    <div class="brand">
                        <span class="brand-mark"></span>
                        <span>Sertão Digital</span>
                    </div>
                    <nav class="nav" aria-label="Navegação principal">
                        <span class="chip">API</span>
                        <span class="chip">Transferências</span>
                        <span class="chip">Auditoria</span>
                    </nav>
                </header>

                <main class="hero">
                    <section class="copy">
                        <div class="eyebrow">Sistema financeiro</div>
                        <h1>Carteira digital<br /><span class="soft">remodelada para a era dos dados.</span></h1>
                        <p class="lead">
                            Destaque para uma plataforma de transferências com autenticação segura,
                            validação rigorosa de regras de negócio e auditoria em tempo real,
                            pronta para operar com presença institucional e experiência premium.
                        </p>
                        <div class="actions">
                            <a class="btn primary" href="/docs">Abrir documentação</a>
                            <a class="btn secondary" href="/health">Ver status</a>
                        </div>
                    </section>

                    <section class="visual" aria-label="Ilustração do produto">
                        <div class="screen-cube">
                            <div class="panel-grid">
                                <div class="panel-tile"></div>
                                <div class="panel-tile"></div>
                                <div class="panel-tile"></div>
                                <div class="panel-tile"></div>
                            </div>
                        </div>
                        <span class="pulse p1"></span>
                        <span class="pulse p2"></span>
                        <span class="pulse p3"></span>
                        <span class="pulse p4"></span>

                        <div class="stats">
                            <div class="stat">
                                <strong>1000</strong>
                                <span>Saldo inicial</span>
                            </div>
                            <div class="stat">
                                <strong>JWT</strong>
                                <span>Token</span>
                            </div>
                            <div class="stat">
                                <strong>60s</strong>
                                <span>Duplicidade</span>
                            </div>
                        </div>
                    </section>
                </main>
            </div>
        </body>
        </html>
        """
    )


@app.exception_handler(HTTPException)
async def business_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    # O PDF exige que qualquer valor ausente/inválido em /transferencias
    # resulte exatamente em 422 {"error":"VALOR_INVALIDO"}.
    if request.url.path == "/auth/login":
        return JSONResponse(status_code=401, content={"error": "CREDENCIAIS_INVALIDAS"})

    if request.url.path == "/transferencias" and any(
        "valor" in error.get("loc", ()) or error.get("loc") == ("body",)
        for error in exc.errors()
    ):
        return JSONResponse(status_code=422, content={"error": "VALOR_INVALIDO"})

    return JSONResponse(status_code=422, content={"error": "REQUISICAO_INVALIDA"})


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception):
    # Falhas inesperadas não devem vazar detalhes internos nem virar resposta ambígua.
    logger.exception("Falha não tratada durante %s %s", request.method, request.url.path)
    return JSONResponse(status_code=503, content={"error": "ERRO_INTERNO"})


app.include_router(auth.router)
app.include_router(account.router)
app.include_router(transfers.router)
app.include_router(audit.router)


@app.get("/health", tags=["Sistema"])
def health(db: Session = Depends(get_db)):
    # Healthcheck de prontidão: confirma também que o banco está acessível.
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
