import streamlit as st
import requests

# Configuração da página
st.set_page_config(
    page_title="Fast Tax - Consulta de Crédito e CNPJ",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Fast Tax")
st.write("Consulte a situação cadastral e a **Ficha Completa** de qualquer CNPJ.")

# Entrada do CNPJ
cnpj_input = st.text_input("Digite o CNPJ (somente números ou formatado):", "")

def limpar_cnpj(cnpj):
    return "".join(filter(str.isdigit, cnpj))

def buscar_cnpj(cnpj_limpio):
    # Primeira opção: BrasilAPI
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpio}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    # Segunda opção (Redundância): Minha Receita
    try:
        url = f"https://minhareceita.org/{cnpj_limpio}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
        
    return None

if st.button("Consultar CNPJ", type="primary"):
    cnpj_limpo = limpar_cnpj(cnpj_input)
    
    if len(cnpj_limpo) != 14:
        st.error("⚠️ Por favor, digite um CNPJ válido com 14 dígitos.")
    else:
        with st.spinner("Buscando dados na Receita Federal..."):
            dados = buscar_cnpj(cnpj_limpo)
            
            if not dados:
                st.error("❌ CNPJ não encontrado ou indisponível no momento.")
            else:
                # Normalização de dados entre APIs
                razao_social = dados.get("razao_social") or dados.get("nome") or "Não informado"
                nome_fantasia = dados.get("nome_fantasia") or razao_social
                situacao = str(dados.get("descricao_situacao_cadastral") or dados.get("situacao") or "").upper()
                
                # Validação de Status de Crédito
                if "ATIVA" in situacao or situacao == "2":
                    st.success("🟢 STATUS: CRÉDITO GARANTIDO (Empresa Ativa)")
                else:
                    st.error(f"🔴 STATUS: RISCO DE CRÉDITO (Situação: {situacao or 'INATIVA/IRREGULAR'})")
                
                st.markdown("---")
                st.subheader("📋 Ficha Completa da Empresa")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Razão Social:** {razao_social}")
                    st.write(f"**Nome Fantasia:** {nome_fantasia}")
                    
                    # Capital Social
                    capital = dados.get("capital_social", 0)
                    if isinstance(capital, (int, float)):
                        capital_fmt = f"R$ {capital:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    else:
                        capital_fmt = f"R$ {capital}"
                    st.write(f"**Capital Social:** {capital_fmt}")

                with col2:
                    # Endereço
                    logradouro = dados.get("logradouro", "")
                    numero = dados.get("numero", "")
                    bairro = dados.get("bairro", "")
                    municipio = dados.get("municipio", "")
                    uf = dados.get("uf", "")
                    st.write(f"**Endereço:** {logradouro}, {numero} - {bairro}, {municipio}/{uf}")
                    
                    # Simples / MEI
                    simples = "Sim" if dados.get("opcao_pelo_simples") else "Não / Não informado"
                    mei = "Sim" if dados.get("opcao_pelo_mei") else "Não / Não informado"
                    st.write(f"**Optante do Simples:** {simples}")
                    st.write(f"**Optante do MEI:** {mei}")

                # Atividade Principal (CNAE)
                st.markdown("---")
                st.write("**Atividade Econômica Principal (CNAE):**")
                cnaes = dados.get("cnae_fiscal_descricao") or dados.get("atividade_principal", [{}])[0].get("text", "Não informado")
                st.info(cnaes)
                
                # Quadro de Sócios (QSA)
                st.markdown("---")
                st.write("**Quadro de Sócios e Administradores (QSA):**")
                socios = dados.get("qsa") or dados.get("socios") or []
                
                if socios:
                    for socio in socios:
                        nome_socio = socio.get("nome") or socio.get("nome_socio") or "Sócio"
                        qualificacao = socio.get("qualificacao_socio") or socio.get("qualificacao") or "Sócio/Administrador"
                        st.write(f"• **{nome_socio}** ({qualificacao})")
                else:
                    st.write("Nenhum sócio listado ou Empresa Individual/MEI.")
