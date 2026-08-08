import streamlit as st
import requests

st.set_page_config(
    page_title="Fast Tax - Consulta de Crédito Tributário",
    page_icon="⚡",
    layout="centered"
)

# Estilização do app
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        background-color: #0066cc;
        color: white;
        font-weight: bold;
        height: 50px;
        border-radius: 8px;
    }
    .card-verde {
        padding: 20px;
        background-color: #d4edda;
        border-left: 6px solid #28a745;
        border-radius: 8px;
        color: #155724;
        margin-bottom: 15px;
    }
    .card-vermelho {
        padding: 20px;
        background-color: #f8d7da;
        border-left: 6px solid #dc3545;
        border-radius: 8px;
        color: #721c24;
        margin-bottom: 15px;
    }
    .pro-box {
        padding: 15px;
        background-color: #e9ecef;
        border: 2px dashed #6c757d;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Fast Tax")
st.caption("Verificação instantânea de risco de crédito fiscal (IBS/CBS - Reforma Tributária)")

# Controle de demonstração do Plano PRO no menu lateral
st.sidebar.header("⚙️ Painel de Demonstração")
plano_pro = st.sidebar.checkbox("Simular Usuário PRO (Pago)", value=False)

st.divider()

# --- FUNÇÃO COM SISTEMA DE REDUNDÂNCIA (2 APIS) ---
def consultar_cnpj(cnpj: str):
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        return None, "Digite um CNPJ válido com 14 números."
        
    # Tentativa 1: API Minha Receita (Excelente para MEIs e Pequenas Empresas)
    try:
        res = requests.get(f"https://minhareceita.org/{cnpj_limpo}", timeout=6)
        if res.status_code == 200:
            d = res.json()
            socios = [s.get("nome_socio_razao_social") or s.get("nome_socio") for s in d.get("qsa", []) if s]
            return {
                "razao": d.get("razao_social"),
                "fantasia": d.get("nome_fantasia") or d.get("razao_social"),
                "situacao": (d.get("descricao_situacao_cadastral") or "DESCONHECIDA").upper(),
                "capital": d.get("capital_social", 0),
                "cnae": d.get("cnae_fiscal_descricao", "Não informado"),
                "simples": "Sim" if d.get("opcao_pelo_simples") else "Não",
                "mei": "Sim" if d.get("opcao_pelo_mei") else "Não",
                "endereco": f"{d.get('logradouro', '')}, {d.get('numero', '')} - {d.get('municipio', '')}/{d.get('uf', '')}",
                "socios": socios if socios else ["Nenhum sócio informado / MEI"]
            }, None
    except:
        pass

    # Tentativa 2: BrasilAPI (Fallback de Segurança)
    try:
        res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}", timeout=6)
        if res.status_code == 200:
            d = res.json()
            socios = [s.get("nome_socio_razao_social") or s.get("nome_socio") for s in d.get("qsa", []) if s]
            return {
                "razao": d.get("razao_social"),
                "fantasia": d.get("nome_fantasia") or d.get("razao_social"),
                "situacao": (d.get("descricao_situacao_cadastral") or "DESCONHECIDA").upper(),
                "capital": d.get("capital_social", 0),
                "cnae": d.get("cnae_fiscal_descricao", "Não informado"),
                "simples": "Não informado",
                "mei": "Não informado",
                "endereco": f"{d.get('logradouro', '')}, {d.get('numero', '')} - {d.get('municipio', '')}/{d.get('uf', '')}",
                "socios": socios if socios else ["Nenhum sócio informado / MEI"]
            }, None
    except:
        pass

    return None, "CNPJ não encontrado nas bases oficiais do governo."

# --- INTERFACE ---
cnpj_input = st.text_input("CNPJ do Fornecedor", placeholder="Digite o CNPJ aqui (ex: 33.000.167/0001-01)")

if st.button("🔍 VERIFICAR CRÉDITO"):
    if not cnpj_input:
        st.warning("Por favor, digite um CNPJ.")
    else:
        with st.spinner("Consultando bases oficiais da Receita Federal..."):
            dados, erro = consultar_cnpj(cnpj_input)
            
            if erro:
                st.error(erro)
            else:
                st.subheader(f"🏢 {dados['fantasia']}")
                st.write(f"**Razão Social:** {dados['razao']}")
                
                # --- RESULTADO GRATUITO (BÁSICO) ---
                if dados['situacao'] == "ATIVA":
                    st.markdown(f"""
                        <div class="card-verde">
                            <h3>🟢 STATUS: CRÉDITO GARANTIDO</h3>
                            <p><b>Situação Cadastral:</b> ATIVA</p>
                            <p><b>Recomendação:</b> Compra segura. Crédito fiscal liberado.</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="card-vermelho">
                            <h3>🔴 STATUS: RISCO DE CRÉDITO</h3>
                            <p><b>Situação Cadastral:</b> {dados['situacao']}</p>
                            <p><b>Recomendação:</b> Atenção! Alto risco de retenção do crédito tributário.</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                # --- ÁREA PRO (DADOS AVANÇADOS) ---
                st.divider()
                st.subheader("📊 Dossiê do Fornecedor")
                
                if plano_pro:
                    st.success("🔓 **Acesso PRO Ativo**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Capital Social", f"R$ {dados['capital']:,.2f}")
                        st.write(f"**Opção pelo Simples:** {dados['simples']}")
                        st.write(f"**Optante pelo MEI:** {dados['mei']}")
                    with col2:
                        st.write(f"**Atividade (CNAE):** {dados['cnae']}")
                        st.write(f"**Endereço:** {dados['endereco']}")
                    
                    st.write("**Quadro de Sócios (QSA):**")
                    for s in dados['socios']:
                        st.caption(f"• {s}")
                else:
                    st.markdown("""
                        <div class="pro-box">
                            <h4>🔒 Recursos Exclusivos do Plano PRO</h4>
                            <p>Desbloqueie o <b>Capital Social</b>, <b>Quadro de Sócios</b>, <b>Regime do Simples/MEI</b> e <b>CNAE Fiscal</b> deste fornecedor.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("🚀 ASSINAR PLANO PRO (R$ 49/mês)"):
                        st.info("Para assinar, entre em contato com nosso time de vendas.")
