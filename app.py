import streamlit as st
import os
from groq import Groq

# Configuration de la page et style visuel (Sombre, Moderne, Épuré)
st.set_page_config(page_title="Calculateur ROAS IA", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button {
        background-color: #2563eb; color: white; border-radius: 8px;
        width: 100%; border: none; padding: 10px; font-weight: bold;
    }
    .stButton>button:hover { background-color: #1d4ed8; }
    .metric-box {
        background-color: #1e293b; padding: 15px; border-radius: 8px;
        border: 1px solid #334155; margin-bottom: 10px; text-align: center;
    }
    .metric-val { font-size: 24px; font-weight: bold; color: #38bdf8; }
    </style>
""", unsafe_index=True)

# Récupération sécurisée de la clé API Groq (Compatible Local et Streamlit Cloud)
if "GROQ_API_KEY" in st.secrets:
    groq_key = st.secrets["GROQ_API_KEY"]
elif os.environ.get("GROQ_API_KEY"):
    groq_key = os.environ.get("GROQ_API_KEY")
else:
    groq_key = None

# En-tête de l'application
st.title("💰 Calculateur de Rentabilité ROAS IA")
st.caption("Explosez vos ventes pour 30 $/mois — Ne brûlez plus votre budget publicitaire.")

if not groq_key:
    st.error("⚠️ Clé API Groq introuvable. Veuillez configurer 'GROQ_API_KEY' dans vos secrets Streamlit.")
    st.stop()

client = Groq(api_key=groq_key)

# Formulaire des données financières
st.subheader("📊 Vos Données Financières")
col1, col2 = st.columns(2)

with col1:
    prix_vente = st.number_input("Prix de vente du produit ($)", min_value=0.0, value=50.0, step=1.0)
    cout_produit = st.number_input("Coût d'achat du produit ($)", min_value=0.0, value=15.0, step=1.0)
    frais_livraison = st.number_input("Frais de livraison réels ($)", min_value=0.0, value=5.0, step=1.0)

with col2:
    frais_passerelle = st.number_input("Frais de paiement (ex: Stripe, %)", min_value=0.0, max_value=100.0, value=2.9, step=0.1)
    frais_fixes = st.number_input("Autres frais par commande ($)", min_value=0.0, value=1.0, step=1.0)
    roas_actuel = st.number_input("Votre ROAS Publicitaire actuel", min_value=0.1, value=2.5, step=0.1)

# Calculs mathématiques de base
frais_stripe_calcul = prix_vente * (frais_passerelle / 100)
total_couts = cout_produit + frais_livraison + frais_stripe_calcul + frais_fixes
marge_brute = prix_vente - total_couts

# Calcul du Point Mort (Break-Even ROAS)
if marge_brute > 0:
    break_even_roas = prix_vente / marge_brute
    cpa_max = marge_brute
    
    # Évaluation de la situation actuelle
    chiffre_affaire_par_vente = prix_vente
    depense_pub_par_vente = prix_vente / roas_actuel
    profit_reel_par_vente = marge_brute - depense_pub_par_vente
else:
    break_even_roas = 0.0
    cpa_max = 0.0
    profit_reel_par_vente = 0.0

# Affichage des métriques clés
st.subheader("📈 Votre Point Mort Analysé")

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="metric-box"><div>Marge Brute</div><div class="metric-val">{marge_brute:.2f}$</div></div>', unsafe_index=True)
with m2:
    st.markdown(f'<div class="metric-box"><div>ROAS Point Mort</div><div class="metric-val">{break_even_roas:.2f}x</div></div>', unsafe_index=True)
with m3:
    st.markdown(f'<div class="metric-box"><div>Coût d\'Acquisition Max</div><div class="metric-val">{cpa_max:.2f}$</div></div>', unsafe_index=True)

# Bloc IA pour l'analyse stratégique
st.subheader("🤖 Analyse Stratégique par l'IA")

if marge_brute <= 0:
    st.error("❌ Votre produit n'est pas rentable avant même la publicité. Augmentez votre prix ou baissez vos coûts.")
else:
    if st.button("Générer l'analyse et les recommandations de l'IA"):
        with st.spinner("L'IA étudie vos chiffres..."):
            
            # Préparation du prompt pour Groq
            prompt = f"""
            En tant qu'expert en finance e-commerce et en publicité payante (Facebook/Google Ads), analyse ces données :
            - Prix de vente : {prix_vente}$
            - Coût total du produit et logistique : {total_couts:.2f}$
            - Marge brute restante pour la pub : {marge_brute:.2f}$
            - ROAS minimum pour ne pas perdre d'argent (Point Mort) : {break_even_roas:.2f}x
            - ROAS actuel de l'utilisateur : {roas_actuel}x
            - Profit net estimé par vente actuellement : {profit_reel_par_vente:.2f}$
            
            Rédige un diagnostic ultra-court, percutant et actionnable (maximum 3 puces très directes) pour optimiser cette rentabilité publicitaire. Va droit au but.
            """
            
            try:
                # Appel du modèle Llama 3 via Groq
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=300
                )
                
                # Affichage du résultat de l'IA
                st.info(completion.choices.message.content)
                
            except Exception as e:
                st.error(f"Erreur lors de la génération IA : {e}")

# Note de bas de page sécurisée
st.markdown("---")
st.caption("🔒 Paiement entièrement sécurisé par PayPal. Vos données de simulation ne sont pas enregistrées.")
