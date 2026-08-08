import streamlit as st
import requests

st.set_page_config(
    page_title="Fast Tax - Consulta de Crédito Tributário",
    page_icon="⚡",
    layout="centered"
)

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
    }
    .card-vermelho {
        padding: 20px;
        background-color: #f8d7da;
        border-left: 6px solid #dc3545;
        border-radius: 8px;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Fast Tax")
st.caption("Verificação instantânea de risco de crédito fiscal (IBS/CBS - Reforma Tributária)")
st.divider()

def consultar_cnpj(cnpj: str):
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        return None, "Digite um CNPJ válido com 14 números."
        
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json(), None
        return None, "CNPJ não encontrado."
    except:
        return None, "Erro ao conectar com a base de dados."

cnpj_input = st.text_input("CNPJ do Fornecedor", placeholder="Digite o CNPJ aqui (ex: 33.000.167/0001-01)")

if st.button("🔍 VERIFICAR CRÉDITO"):
    if not cnpj_input:
        st.warning("Por favor, digite um CNPJ.")
    else:
        with st.spinner("Consultando bases do governo..."):
            dados, erro = consultar_cnpj(cnpj_input)
            
            if erro:
                st.error(erro)
            else:
                razao = dados.get("razao_social")
                fantasia = dados.get("nome_fantasia") or razao
                situacao = dados.get("descricao_situacao_cadastral", "DESCONHECIDA").upper()
                
                st.subheader(f"🏢 {fantasia}")
                st.text(f"Razão Social: {razao}")
                
                if situacao == "ATIVA":
                    st.markdown(f"""
                        <div class="card-verde">
                            <h3>🟢 STATUS: CRÉDITO GARANTIDO</h3>
                            <p><b>Situação Cadastral:</b> ATIVA</p>
                            <p><b>Recomendação:</b> Compra segura. O imposto será recolhido via Split Payment e o crédito fiscal estará liberado.</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="card-vermelho">
                            <h3>🔴 STATUS: RISCO DE CRÉDITO</h3>
                            <p><b>Situação Cadastral:</b> {situacao}</p>
                            <p><b>Recomendação:</b> Atenção! Alto risco de retenção do crédito tributário. Exige regularização prévia do fornecedor.</p>
                        </div>
                    """, unsafe_allow_html=True)
