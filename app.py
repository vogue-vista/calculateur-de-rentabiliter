import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# -------------------------
# CONFIGURATION DE LA PAGE
# -------------------------
st.set_page_config(page_title="Calendrier Éditorial IA Pro", page_icon="📅", layout="wide")

# Masquer la sidebar par défaut et injecter le style épuré
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none !important;}
[data-testid="stSidebarNav"] {display: none !important;}
@import url('https://googleapis.com');
html, body, div, p, h1, h2, h3, h4, h5, h6, span {
    font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# CONFIGURATION PAYPAL
# -------------------------
PAYPAL_CLIENT_ID = "DEMO"  # Mettez votre Client ID ici plus tard
PAYPAL_PLAN_ID = "DEMO"    # Mettez votre Plan ID ici plus tard

# -------------------------
# GESTION DE L'ACCÈS (SESSION STATE)
# -------------------------
if "est_abonne" not in st.session_state:
    st.session_state.est_abonne = False

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except:
    API_KEY = ""

# -------------------------
# INTERFACE SÉCURISÉE
# -------------------------
st.title("📅 Calendrier Éditorial IA — Version Pro")

# CAS 1 : L'UTILISATEUR N'A PAS PAYÉ
if not st.session_state.est_abonne:
    st.warning("🔒 Cette application est réservée aux membres de la version Premium.")
    
    col_offre, col_connexion = st.columns(2, gap="large")
    
    with col_offre:
        st.subheader("🚀 Débloquez l'IA pour 30 $/mois")
        st.write("Générez un calendrier complet de 30 jours d'idées de contenu sur-mesure avec les angles d'attaque et les hashtags pour votre niche.")
        st.write("Le paiement est entièrement sécurisé par **PayPal**.")
        
        if PAYPAL_CLIENT_ID == "DEMO":
            paypal_html = """
            <a href="https://paypal.com" target="_blank" style="text-decoration: none;">
                <div style="background-color: #ffc439; color: #003087; text-align: center; 
                            padding: 12px; font-family: Arial, sans-serif; font-weight: bold; 
                            border-radius: 4px; max-width: 300px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    🟨 S'abonner avec PayPal (Démo)
                </div>
            </a>
            """
        else:
            paypal_html = f"""
            <div id="paypal-button-container-fixed" style="max-width: 350px; margin-top: 20px;"></div>
            <script src="https://paypal.com/sdk/js?client-id={PAYPAL_CLIENT_ID}&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
            <script>
              paypal.Buttons({{
                  style: {{ shape: 'rect', color: 'gold', layout: 'vertical', label: 'subscribe' }},
                  createSubscription: function(data, actions) {{
                    return actions.subscription.create({{ 'plan_id': '{PAYPAL_PLAN_ID}' }});
                  }},
                  onApprove: function(data, actions) {{
                    alert('Abonnement réussi ! ID : ' + data.subscriptionID);
                  }}
              }}).render('#paypal-button-container-fixed');
            </script>
            """
        
        components.html(paypal_html, height=150, scrolling=False)
        
    with col_connexion:
        st.subheader("🔑 Déjà abonné ?")
        st.write("Connectez-vous pour activer vos accès.")
        email = st.text_input("Adresse e-mail")
        mot_de_passe = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter", use_container_width=True):
            if email == "test@client.com" and mot_de_passe == "access30":
                st.session_state.est_abonne = True
                st.success("Accès accordé !")
                st.rerun()
            else:
                st.error("Identifiants incorrects ou abonnement PayPal inactif.")

# CAS 2 : L'UTILISATEUR EST ABONNÉ -> ACCÈS COMPLET
else:
    st.write("✨ **Bienvenue dans votre espace Premium.** Votre abonnement est actif.")
    if st.button("🚪 Se déconnecter", key="logout"):
        st.session_state.est_abonne = False
        st.rerun()
        
    st.write("---")

    with st.container(border=True):
        col_input, col_options = st.columns(2)
        
        with col_input:
            niche = st.text_input("Quelle est votre thématique ou produit ?", 
                                  placeholder="Ex: Sneakers de collection, coaching fitness, agence SEO...")
            audience = st.text_input("Quelle est votre cible / audience ?", 
                                     placeholder="Ex: Jeunes urbains 18-25 ans, entrepreneurs...")
            
        with col_options:
            reseau = st.selectbox("Réseau social principal", [
                "📸 Instagram / Facebook", 
                "💼 LinkedIn PRO", 
                "🎵 TikTok / Reels",
                "📌 Pinterest"
            ])
            frequence = st.selectbox("Nombre d'idées de contenu demandées", ["7 jours (Express)", "14 jours (Standard)", "30 jours (Complet)"])

        generer = st.button("🚀 Générer le Calendrier Éditorial Pro", use_container_width=True)

    if generer:
        if not API_KEY:
            st.error("⚠️ Erreur : La clé GROQ_API_KEY est manquante dans les Secrets du serveur.")
        elif not niche:
            st.error("⚠️ Veuillez indiquer votre thématique ou produit.")
        else:
            with st.spinner("L'IA de Groq conçoit votre stratégie de contenu..."):
                try:
                    client = Groq(api_key=API_KEY)
                    
                    prompt_systeme = """Tu es un expert mondial en stratégie de contenu de marque et gestionnaire de réseaux sociaux (CM).
                    Tu dois générer un plan éditorial stratégique.
                    Formate obligatoirement ta réponse sous forme de tableau Markdown avec exactement 4 colonnes :
                    1. **Jour** (ex: Jour 1, Jour 2...)
                    2. **Objectif du post** (ex: Éduquer, Vendre, Divertir, Inspirer)
                    3. **Sujet & Accroche** (Le concept exact du contenu et une idée de titre fort)
                    4. **Hashtags suggérés**
                    Ne fais aucun blabla d'introduction ou de conclusion, donne directement le tableau."""

                    reponse = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": prompt_systeme},
                            {"role": "user", "content": f"Thématique : '{niche}'. Audience cible : '{audience}'. Réseau social : {reseau}. Durée du plan : {frequence}."}
                        ],
                        temperature=0.7
                    )
                    
                    calendrier_genere = reponse.choices[0].message.content
                    st.success("✨ Votre stratégie de contenu sur-mesure est prête !")
                    st.markdown(calendrier_genere)
                    st.text_area("Copier le tableau brut :", value=calendrier_genere, height=200)

                except Exception as e:
                    st.error(f"Erreur technique Groq : {str(e)}")
