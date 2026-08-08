import streamlit as st
import requests
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Fast Tax - Consulta de Crédito e CNPJ",
    page_icon="⚡",
    layout="wide"
)

# Inicializa variáveis de sessão
if "historico" not in st.session_state:
    st.session_state.historico = []
if "favoritos" not in st.session_state:
    st.session_state.favoritos = []
if "cnpj_ativo" not in st.session_state:
    st.session_state.cnpj_ativo = ""

def limpar_cnpj(cnpj):
    return "".join(filter(str.isdigit, str(cnpj)))

def formatar_data(data_str):
    if not data_str:
        return "Não informada"
    try:
        dt = datetime.strptime(str(data_str)[:10], "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except:
        return str(data_str)

def buscar_cnpj(cnpj_limpio):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpio}"
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    try:
        url = f"https://minhareceita.org/{cnpj_limpio}"
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            return response.json()
    except:
        pass
        
    return None

# ==================== BARRA LATERAL (FAVORITOS & HISTÓRICO) ====================
st.sidebar.title("⭐ Empresas Salvas")

# Lista de Empresas Salvas (Acesso Rápido com 1 clique)
if st.session_state.favoritos:
    for idx, fav in enumerate(st.session_state.favoritos):
        col_f1, col_f2 = st.sidebar.columns([4, 1])
        with col_f1:
            if st.button(f"📌 {fav['nome'][:16]}...", key=f"fav_{fav['cnpj']}_{idx}", use_container_width=True):
                st.session_state.cnpj_ativo = fav['cnpj']
                st.rerun()
            st.caption(f"`{fav['cnpj']}` — {fav['status']}")
        with col_f2:
            if st.button("❌", key=f"del_fav_{fav['cnpj']}_{idx}"):
                st.session_state.favoritos.pop(idx)
                st.rerun()
        st.sidebar.markdown("---")
else:
    st.sidebar.caption("Nenhuma empresa salva ainda. Consulte um CNPJ e clique em '⭐ Salvar Empresa'.")

st.sidebar.title("📜 Histórico Recente")
if st.session_state.historico:
    for idx, item in enumerate(reversed(st.session_state.historico)):
        col_h1, col_h2 = st.sidebar.columns([4, 1])
        with col_h1:
            if st.button(f"🔍 {item['nome'][:16]}...", key=f"hist_{item['cnpj']}_{idx}", use_container_width=True):
                st.session_state.cnpj_ativo = item['cnpj']
                st.rerun()
            st.caption(f"`{item['cnpj']}`")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Limpar Histórico", use_container_width=True):
        st.session_state.historico = []
        st.rerun()
else:
    st.sidebar.caption("Nenhuma consulta recente.")

# ==================== PAINEL PRINCIPAL ====================
st.title("⚡ Fast Tax")
st.write("Consulte a situação cadastral e a **Ficha Completa Exaustiva** de qualquer CNPJ.")

# Formulário para entrada do CNPJ
with st.form(key="cnpj_form"):
    cnpj_input = st.text_input(
        "Digite o CNPJ (somente números ou formatado):", 
        value=st.session_state.cnpj_ativo
    )
    submit_button = st.form_submit_button("Consultar CNPJ", type="primary")

# Atualiza se enviar formulário
if submit_button:
    st.session_state.cnpj_ativo = cnpj_input

# Executa busca
cnpj_limpo = limpar_cnpj(st.session_state.cnpj_ativo)

if cnpj_limpo:
    if len(cnpj_limpo) != 14:
        st.error("⚠️ Por favor, digite um CNPJ válido com 14 dígitos.")
    else:
        with st.spinner("Buscando ficha completa na Receita Federal..."):
            dados = buscar_cnpj(cnpj_limpo)
            
            if not dados:
                st.error("❌ CNPJ não encontrado ou indisponível no momento.")
            else:
                razao_social = dados.get("razao_social") or dados.get("nome") or "Não informado"
                nome_fantasia = dados.get("nome_fantasia") or razao_social
                situacao = str(dados.get("descricao_situacao_cadastral") or dados.get("situacao") or "").upper()
                
                status_texto = "🟢 CRÉDITO GARANTIDO" if ("ATIVA" in situacao or situacao == "2") else "🔴 RISCO DE CRÉDITO"

                # Histórico
                registro = {"nome": nome_fantasia, "cnpj": cnpj_limpo, "status": status_texto}
                if not st.session_state.historico or st.session_state.historico[-1]["cnpj"] != cnpj_limpo:
                    st.session_state.historico.append(registro)

                # Cabeçalho: Status + Botão de Salvar/Favoritar
                col_status, col_fav_btn = st.columns([3, 1])
                
                with col_status:
                    if "ATIVA" in situacao or situacao == "2":
                        st.success("🟢 STATUS: CRÉDITO GARANTIDO (Empresa Ativa)")
                    else:
                        st.error(f"🔴 STATUS: RISCO DE CRÉDITO (Situação: {situacao or 'INATIVA/IRREGULAR'})")
                
                with col_fav_btn:
                    ja_favorito = any(f["cnpj"] == cnpj_limpo for f in st.session_state.favoritos)
                    if ja_favorito:
                        st.info("⭐ Salva nos Favoritos")
                    else:
                        if st.button("⭐ Salvar Empresa", use_container_width=True):
                            st.session_state.favoritos.append(registro)
                            st.rerun()

                st.markdown("---")
                st.header("📋 Ficha Completa da Empresa")
                
                # BLOCO 1: Identificação e Dados Institucionais
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("📌 Identificação")
                    st.write(f"**Razão Social:** {razao_social}")
                    st.write(f"**Nome Fantasia:** {nome_fantasia}")
                    st.write(f"**CNPJ:** {cnpj_limpo}")
                    
                    tipo = dados.get("descricao_identificador_matriz_filial") or dados.get("descricao_matriz_filial") or "Matriz"
                    st.write(f"**Tipo:** {tipo.upper()}")

                with col2:
                    st.subheader("🏢 Estrutura & Porte")
                    porte = dados.get("porte") or dados.get("descricao_porte") or "Não informado"
                    st.write(f"**Porte:** {porte.upper()}")
                    
                    natureza = dados.get("natureza_juridica") or "Não informada"
                    st.write(f"**Natureza Jurídica:** {natureza}")
                    
                    dt_abertura = formatar_data(dados.get("data_inicio_atividade"))
                    st.write(f"**Data de Abertura:** {dt_abertura}")

                with col3:
                    st.subheader("💰 Situação Fiscal")
                    capital = dados.get("capital_social", 0)
                    if isinstance(capital, (int, float)):
                        capital_fmt = f"R$ {capital:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    else:
                        capital_fmt = f"R$ {capital}"
                    st.write(f"**Capital Social:** {capital_fmt}")
                    
                    simples = "Sim" if dados.get("opcao_pelo_simples") else "Não / Não informado"
                    mei = "Sim" if dados.get("opcao_pelo_mei") else "Não / Não informado"
                    st.write(f"**Optante do Simples:** {simples}")
                    st.write(f"**Optante do MEI:** {mei}")

                st.markdown("---")

                # BLOCO 2: Localização e Contato
                col_loc, col_ct = st.columns(2)
                
                with col_loc:
                    st.subheader("📍 Localização")
                    logradouro = dados.get("logradouro", "")
                    numero = dados.get("numero", "")
                    complemento = dados.get("complemento", "")
                    bairro = dados.get("bairro", "")
                    municipio = dados.get("municipio", "")
                    uf = dados.get("uf", "")
                    cep = dados.get("cep", "Não informado")
                    
                    comp_str = f" ({complemento})" if complemento else ""
                    st.write(f"**Logradouro:** {logradouro}, {numero}{comp_str}")
                    st.write(f"**Bairro:** {bairro}")
                    st.write(f"**Cidade/UF:** {municipio}/{uf}")
                    st.write(f"**CEP:** {cep}")

                with col_ct:
                    st.subheader("📞 Contatos Registrados")
                    tel1 = dados.get("ddd_telefone_1") or dados.get("telefone") or ""
                    tel2 = dados.get("ddd_telefone_2") or ""
                    email = dados.get("email") or "Não informado"
                    
                    telefones = ", ".join(filter(None, [tel1, tel2])) or "Não informado"
                    st.write(f"**Telefone(s):** {telefones}")
                    st.write(f"**E-mail:** {email}")

                st.markdown("---")

                # BLOCO 3: Atividades Econômicas
                st.subheader("⚙️ Atividades Econômicas (CNAE)")
                
                cnae_principal = dados.get("cnae_fiscal_descricao") or dados.get("atividade_principal", [{}])[0].get("text", "Não informado")
                st.markdown(f"**Atividade Principal:**")
                st.info(cnae_principal)
                
                cnaes_secundarios = dados.get("cnaes_secundarios") or dados.get("atividades_secundarias") or []
                if cnaes_secundarios:
                    with st.expander(f"Ver {len(cnaes_secundarios)} Atividades Secundárias (CNAEs)"):
                        for item in cnaes_secundarios:
                            desc = item.get("descricao") or item.get("text") or "Sem descrição"
                            cod = item.get("codigo") or ""
                            cod_str = f"[{cod}] " if cod else ""
                            st.write(f"• {cod_str}{desc}")
                else:
                    st.write("Nenhuma atividade secundária cadastrada.")

                st.markdown("---")

                # BLOCO 4: QSA
                st.subheader("👥 Quadro de Sócios e Administradores (QSA)")
                socios = dados.get("qsa") or dados.get("socios") or []
                
                if socios:
                    for socio in socios:
                        nome_socio = socio.get("nome") or socio.get("nome_socio") or socio.get("nome_socio_razao_social") or "Sócio"
                        qualificacao = socio.get("qualificacao_socio") or socio.get("qualificacao") or "Sócio/Administrador"
                        st.write(f"• **{nome_socio}** — *{qualificacao}*")
                else:
                    st.write("Nenhum sócio listado no banco de dados da Receita.")
