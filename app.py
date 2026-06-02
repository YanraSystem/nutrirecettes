"""
NutriRecettes - Application Streamlit multi-pages
Coche tes aliments, choisis ton style de cuisine, l'IA te genere la recette
+ tableau nutritionnel + anecdote pays + mode cuisine pas-a-pas + carnet.

Lancer en local :
    streamlit run app.py
"""

import random
import streamlit as st
import streamlit.components.v1 as components_v1

from recipe_engine import get_recipe, score_nutritionnel, adapter_portions
from image_gen import image_url_for
from pdf_export import build_pdf
import components as ui

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="NutriRecettes - Cuisine du monde et nutrition",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS global — palette editoriale (terracotta / sage / creme / charcoal)
st.markdown("""
<style>
    :root {
      --c-creme: #FAF7F2;
      --c-terracotta: #C97B5F;
      --c-terracotta-dark: #A85A3F;
      --c-sage: #8B9A6C;
      --c-charcoal: #2D2A26;
      --c-warm-gray: #5C5751;
    }
    .main { padding-top: 1rem; }
    .stButton button {
        border-radius: 4px;
        font-weight: 500;
        transition: all 0.25s ease;
        letter-spacing: 0.3px;
    }
    .stButton button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    [data-testid="stHorizontalBlock"] { gap: 1rem; }
    .badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 2px;
        font-weight: 500;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
        margin-right: 8px;
        text-transform: uppercase;
    }
    h1, h2, h3 { color: var(--c-charcoal) !important; letter-spacing: -0.5px; }
    /* Touche editoriale : titres avec serif elegant */
    h1 { font-family: "Cormorant Garamond", Georgia, serif !important; font-weight: 700 !important; }
    /* Touche manuscrite pour accents */
    .handwritten {
      font-family: "Brush Script MT", "Snell Roundhand", cursive;
      font-style: italic;
      color: var(--c-terracotta);
    }
    /* Boutons primary repenses */
    button[kind="primary"] {
      background: var(--c-charcoal) !important;
      border: 1px solid var(--c-charcoal) !important;
    }
    button[kind="primary"]:hover {
      background: var(--c-terracotta) !important;
      border-color: var(--c-terracotta) !important;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# State init
# ------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "splash"
if "recipe" not in st.session_state:
    st.session_state.recipe = None
if "personnes" not in st.session_state:
    st.session_state.personnes = 2
if "regime" not in st.session_state:
    st.session_state.regime = "Aucun"
if "carnet" not in st.session_state:
    st.session_state.carnet = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 0

# Detection du clic "ENTER" depuis le splash : ?enter=1 dans l'URL
if st.query_params.get("enter") == "1" and st.session_state.page == "splash":
    st.session_state.page = "accueil"
    st.query_params.clear()


# ------------------------------------------------------------
# Banque d'aliments
# ------------------------------------------------------------
ALIMENTS = {
    "🥩 Proteines": [
        ("🍗", "Poulet"), ("🥩", "Boeuf"), ("🐑", "Agneau"), ("🥓", "Porc"),
        ("🐟", "Poisson"), ("🍣", "Saumon"), ("🐠", "Thon"), ("🍤", "Crevettes"),
        ("🥚", "Oeuf"), ("🧈", "Tofu"), ("🫘", "Lentilles"), ("🫛", "Pois chiches"),
        ("🫘", "Haricots rouges"),
    ],
    "🥦 Legumes": [
        ("🍅", "Tomate"), ("🧅", "Oignon"), ("🧄", "Ail"), ("🥕", "Carotte"),
        ("🥒", "Courgette"), ("🫑", "Poivron"), ("🍆", "Aubergine"), ("🥬", "Epinards"),
        ("🥗", "Salade"), ("🥦", "Brocoli"), ("🍄", "Champignon"), ("🥒", "Concombre"),
        ("🥔", "Pomme de terre"),
    ],
    "🌾 Feculents": [
        ("🍚", "Riz"), ("🍝", "Pates"), ("🌾", "Semoule"), ("🌾", "Quinoa"),
        ("🌾", "Boulgour"), ("🥖", "Pain"), ("🍲", "Couscous"),
    ],
    "🌿 Herbes & Epices": [
        ("🌿", "Basilic"), ("🌿", "Persil"), ("🌿", "Coriandre"), ("🍃", "Menthe"),
        ("🌶️", "Curry"), ("🟡", "Curcuma"), ("🟤", "Cumin"), ("🔴", "Paprika"),
        ("🫚", "Gingembre"), ("🌰", "Cannelle"), ("🌸", "Safran"), ("✨", "Ras el hanout"),
    ],
    "🥛 Produits laitiers": [
        ("🥛", "Lait"), ("🍶", "Yaourt"), ("🧀", "Fromage"), ("🧈", "Beurre"),
        ("🍦", "Creme"),
    ],
}

CUISINES = ["Europeenne", "Asiatique", "Orientale", "Africaine", "Americaine", "Surprends-moi"]
CUISINES_EMOJI = {
    "Europeenne": "🇪🇺", "Asiatique": "🥢", "Orientale": "🕌",
    "Africaine": "🌍", "Americaine": "🗽", "Surprends-moi": "🎲",
}


# ------------------------------------------------------------
# Navigation top
# ------------------------------------------------------------
def render_nav():
    nav = st.container()
    with nav:
        col_logo, col_nav = st.columns([1, 4])
        with col_logo:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; padding: 8px 0;">
                <span style="font-size: 28px;">🍽️</span>
                <span style="font-size: 20px; font-weight: 800; background: linear-gradient(135deg, #FF6B35, #F7931E); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">NutriRecettes</span>
            </div>
            """, unsafe_allow_html=True)
        with col_nav:
            nav_cols = st.columns(4)
            pages = [
                ("accueil", "🏠 Accueil"),
                ("generer", "🍳 Generer"),
                ("cuisine", "👨‍🍳 Pas-a-pas"),
                ("carnet", "📖 Mon carnet"),
            ]
            for i, (slug, label) in enumerate(pages):
                with nav_cols[i]:
                    if st.button(label, key=f"nav_{slug}", use_container_width=True,
                                 type="primary" if st.session_state.page == slug else "secondary"):
                        st.session_state.page = slug
                        st.rerun()
        st.markdown("---")


# ------------------------------------------------------------
# Page : Splash (amorce "click anywhere to enter")
# ------------------------------------------------------------
def page_splash():
    # Cache tout le chrome Streamlit + force le fond noir cosmique
    # Le st.button est stylé plein écran transparent par-dessus le splash → click anywhere fonctionnel
    st.markdown("""
    <style>
      [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
      .stApp { background: #000 !important; }
      .main .block-container, [data-testid="stAppViewBlockContainer"], [data-testid="stMainBlockContainer"] {
        padding: 0 !important; max-width: 100% !important; margin: 0 !important;
      }
      /* Bouton plein ecran transparent pour click anywhere */
      div[data-testid="stButton"] {
        position: fixed !important;
        inset: 0 !important;
        z-index: 999999 !important;
        width: 100vw !important;
        height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
      }
      div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 100% !important;
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        cursor: pointer !important;
        box-shadow: none !important;
        font-size: 0 !important;
        border-radius: 0 !important;
      }
      div[data-testid="stButton"] > button:hover {
        background: rgba(255,107,53,0.04) !important;
      }
      div[data-testid="stButton"] > button:focus { outline: none !important; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(ui.splash_screen_markdown(), unsafe_allow_html=True)
    if st.button("Entrer", key="splash_enter_anywhere"):
        st.session_state.page = "accueil"
        st.rerun()


# ------------------------------------------------------------
# Page : Accueil — design editorial
# ------------------------------------------------------------
def page_accueil():
    ui.hero_personnage(height=600)

    # CTAs — deux options sobres, pas de banniere clinquante
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("Composer une recette", use_container_width=True, type="primary"):
                st.session_state.page = "generer"
                st.rerun()
        with sc2:
            if st.button("Tirer au sort", use_container_width=True):
                st.session_state.page = "generer"
                st.session_state.surprise = True
                st.rerun()

    st.markdown(ui.how_it_works(), unsafe_allow_html=True)
    st.markdown(ui.temoignages(), unsafe_allow_html=True)
    st.markdown(ui.footer_cuisines(), unsafe_allow_html=True)


# ------------------------------------------------------------
# Page : Generer une recette
# ------------------------------------------------------------
def page_generer():
    st.markdown("## 🍳 Generer ta recette")
    st.caption("Coche tes aliments dispos, choisis ta region, l'IA fait le reste.")

    # Mode Surprise pre-rempli ?
    surprise_mode = st.session_state.get("surprise", False)
    if surprise_mode:
        st.success("🎲 Mode Surprise active — selection aleatoire d'ingredients et cuisine.")
        st.session_state.surprise = False

    # ---- Filtres en haut ----
    st.markdown("### 🌍 Region & preferences")
    f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
    with f1:
        cuisine = st.selectbox(
            "Style de cuisine",
            CUISINES,
            format_func=lambda x: f"{CUISINES_EMOJI.get(x, '')} {x}",
            index=random.randint(0, 4) if surprise_mode else 2,
        )
    with f2:
        personnes = st.number_input("Personnes", 1, 12, st.session_state.personnes)
    with f3:
        regime = st.selectbox("Regime", ["Aucun", "Vegetarien", "Halal", "Sans gluten", "Sans lactose"])
    with f4:
        st.markdown("<br>", unsafe_allow_html=True)
        random_btn = st.button("🎲 Random ingredients", use_container_width=True)

    st.markdown("### 📦 Selectionne tes aliments")

    # Selection aleatoire au clic
    if random_btn or surprise_mode:
        all_items = [item for cat in ALIMENTS.values() for emoji, item in cat]
        random_sel = random.sample(all_items, k=random.randint(4, 7))
        for item in all_items:
            st.session_state[f"chk_{item}"] = item in random_sel

    # Checkboxes par categorie
    selected = []
    cols = st.columns(len(ALIMENTS))
    for col, (categorie, items) in zip(cols, ALIMENTS.items()):
        with col:
            st.markdown(f"**{categorie}**")
            for emoji, item in items:
                if st.checkbox(f"{emoji} {item}", key=f"chk_{item}"):
                    selected.append(item)

    st.markdown("---")

    # Live status
    s1, s2, s3 = st.columns([1, 2, 1])
    with s1:
        st.metric("Aliments selectionnes", len(selected))
    with s2:
        if selected:
            score = score_nutritionnel(selected)
            colors = {3: "#22C55E", 2: "#F59E0B", 1: "#F97316", 0: "#EF4444"}
            st.markdown(f"""
            <div style="padding: 12px 16px; background: {colors[score['score']]}22; border: 1px solid {colors[score['score']]}; border-radius: 12px;">
              <div style="font-weight: 700; color: {colors[score['score']]};">Equilibre instantane : {score['label']}</div>
              <div style="font-size: 12px; color: #555; margin-top: 4px;">
                Proteines {'✅' if score['proteines'] else '❌'} ·
                Legumes {'✅' if score['legumes'] else '❌'} ·
                Feculents {'✅' if score['feculents'] else '❌'}
              </div>
            </div>
            """, unsafe_allow_html=True)
    with s3:
        generate = st.button("🚀 Generer", type="primary", use_container_width=True,
                             disabled=len(selected) == 0)

    # Generation
    if generate:
        with st.spinner("🍳 Le chef prepare ta recette du monde..."):
            recipe = get_recipe(selected, cuisine, personnes, regime)
            st.session_state.recipe = recipe
            st.session_state.personnes = personnes
            st.session_state.regime = regime
            st.session_state.current_step = 0

    # Affichage recette
    if st.session_state.recipe:
        render_recipe(st.session_state.recipe)


def render_recipe(recipe: dict):
    """Affichage complet d'une recette avec toutes les sections enrichies."""
    st.markdown("---")

    # === En-tete recette ===
    col_img, col_info = st.columns([1, 2])

    with col_img:
        img_src = recipe.get("image_url") or image_url_for(
            recipe["nom"],
            recipe.get("origine", ""),
            recipe.get("nom_image", ""),
        )
        drapeau = recipe.get('drapeau', '🍽️')
        # background-image CSS : si l'image charge, photo. Si rate, gradient beige avec drapeau.
        # Pas de <img> donc pas de broken icon ni alt text qui depasse.
        st.markdown(f"""
        <div style="
          width: 100%;
          aspect-ratio: 4/3;
          border-radius: 16px;
          background-image: url('{img_src}'), linear-gradient(135deg, #F0E8DC, #E3D5C0);
          background-size: cover, cover;
          background-position: center, center;
          background-repeat: no-repeat, no-repeat;
          box-shadow: 0 8px 24px rgba(0,0,0,0.08);
          display: flex;
          align-items: flex-end;
          justify-content: flex-start;
          padding: 16px;
        ">
          <div style="
            background: rgba(45, 42, 38, 0.75);
            color: #FAF7F2;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            letter-spacing: 1px;
            text-transform: uppercase;
            backdrop-filter: blur(8px);
          ">{drapeau} {recipe.get('origine', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.markdown(f"## {recipe['drapeau']} {recipe['nom']}")
        meta_html = f"""
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
          <span class="badge" style="background: #F1F5F9; color: #475569;">🌍 {recipe.get('origine', '-')}</span>
          <span class="badge" style="background: #F1F5F9; color: #475569;">🍽️ {recipe.get('categorie', 'Plat')}</span>
          <span class="badge" style="background: #F1F5F9; color: #475569;">⏱️ {recipe.get('temps_total', 'N/A')}</span>
          <span class="badge" style="background: #FEF3C7; color: #92400E;">👥 {st.session_state.personnes} pers.</span>
        </div>
        """
        st.markdown(meta_html, unsafe_allow_html=True)

        # Boutons d'action
        a1, a2, a3, a4 = st.columns(4)
        with a1:
            if st.button("👨‍🍳 Pas-a-pas", use_container_width=True):
                st.session_state.page = "cuisine"
                st.session_state.current_step = 0
                st.rerun()
        with a2:
            if st.button("📖 Sauver", use_container_width=True):
                if recipe not in st.session_state.carnet:
                    st.session_state.carnet.append(recipe)
                    st.success("Ajoutee !")
                else:
                    st.info("Deja sauvee")
        with a3:
            try:
                pdf_bytes = build_pdf(recipe, st.session_state.personnes, st.session_state.regime)
                st.download_button(
                    label="📄 PDF",
                    data=pdf_bytes,
                    file_name=f"{recipe['nom'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception:
                st.button("📄 PDF", disabled=True, use_container_width=True)
        with a4:
            if st.button("🔗 Partager", use_container_width=True):
                st.session_state.show_share = True


    # === Panneau partage (s'affiche apres clic) ===
    if st.session_state.get("show_share"):
        render_share_panel(recipe)

    st.markdown("<br>", unsafe_allow_html=True)

    # === Cout estime + Score compatibilite + Nutrition ===
    cout = recipe.get("cout_estime_eur")
    cout_pers = recipe.get("cout_par_personne_eur")
    if cout is not None:
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg,#22C55E,#16A34A); color: white; padding: 18px 22px; border-radius: 14px; box-shadow: 0 4px 12px rgba(34,197,94,0.25);">
              <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.85; font-weight: 600;">💰 Cout estime</div>
              <div style="font-size: 28px; font-weight: 800; margin-top: 4px;">{cout:.2f} €</div>
              <div style="font-size: 12px; opacity: 0.9;">soit {cout_pers:.2f} € / personne</div>
            </div>
            """, unsafe_allow_html=True)
        with cc2:
            if recipe.get("score_compatibilite") is not None:
                st.markdown(ui.score_compatibilite(recipe["score_compatibilite"]), unsafe_allow_html=True)
        with cc3:
            if recipe.get("indicateur_sante"):
                st.markdown(ui.feu_tricolore(recipe["indicateur_sante"], recipe.get("indicateur_label", "")), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # === Tableau nutrition (composants natifs Streamlit) ===
    if recipe.get("nutrition"):
        render_nutrition_native(recipe["nutrition"])

    # === Adaptation portions ===
    st.markdown("### ⚖️ Adapter les quantites")
    ap1, ap2 = st.columns([3, 1])
    with ap1:
        ratio = st.slider("Multiplicateur de portions", 0.5, 4.0, 1.0, 0.5,
                         help=f"1.0 = quantites originales pour {st.session_state.personnes} pers.")
    with ap2:
        new_pers = int(st.session_state.personnes * ratio)
        st.metric("Pour", f"{new_pers} pers.")

    display_recipe = adapter_portions(recipe, ratio) if ratio != 1.0 else recipe

    # === Ingredients + Etapes ===
    st.markdown("### 🥘 Recette complete")
    ing_col, etapes_col = st.columns([1, 2])

    with ing_col:
        st.markdown("**Ingredients**")
        for ing in display_recipe.get("ingredients", []):
            st.markdown(f"- {ing}")

        # Substitutions intelligentes
        subs = recipe.get("substitutions", {})
        if subs:
            with st.expander(f"🔄 {len(subs)} substitutions possibles"):
                for original, alternatives in subs.items():
                    if alternatives:
                        st.markdown(f"**{original.capitalize()}** → {' · '.join(alternatives)}")

    with etapes_col:
        st.markdown("**Preparation**")
        for i, etape in enumerate(display_recipe.get("etapes", []), 1):
            st.markdown(f"**{i}.** {etape}")

    if recipe.get("astuce_chef"):
        st.info(f"💡 **Astuce du chef** : {recipe['astuce_chef']}")

    # === Immersion culturelle ===
    if recipe.get("anecdote_pays"):
        st.markdown(ui.carte_anecdote(
            recipe.get("origine", "Inconnue"),
            recipe.get("drapeau", "🌍"),
            recipe.get("anecdote_pays", ""),
            recipe.get("fun_fact", ""),
            recipe.get("niveau_authenticite", "Adapte"),
        ), unsafe_allow_html=True)


# ------------------------------------------------------------
# Page : Cuisine pas-a-pas
# ------------------------------------------------------------
def page_cuisine():
    st.markdown("## 👨‍🍳 Mode cuisine pas-a-pas")
    if not st.session_state.recipe:
        st.warning("Genere d'abord une recette dans l'onglet 'Generer' pour acceder au mode pas-a-pas.")
        if st.button("Aller a Generer"):
            st.session_state.page = "generer"
            st.rerun()
        return

    recipe = st.session_state.recipe
    etapes = recipe.get("etapes", [])
    total = len(etapes)
    step = st.session_state.current_step

    st.markdown(f"### {recipe['drapeau']} {recipe['nom']}")

    # Progress bar
    progress = (step + 1) / max(total, 1)
    st.progress(progress, text=f"Etape {step + 1} sur {total}")

    if step < total:
        # Etape courante en grand
        st.markdown(f"""
        <div style="
          padding: 32px;
          background: linear-gradient(135deg, #FFF7ED 0%, #FED7AA 100%);
          border-radius: 20px;
          border-left: 8px solid #FF6B35;
          margin: 20px 0;
        ">
          <div style="font-size: 14px; color: #C2410C; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; margin-bottom: 12px;">Etape {step + 1}</div>
          <div style="font-size: 22px; color: #1E293B; line-height: 1.5; font-weight: 500;">{etapes[step]}</div>
        </div>
        """, unsafe_allow_html=True)

        # Timer integre
        st.markdown("### ⏲️ Minuteur pour cette etape")
        t1, t2, t3 = st.columns(3)
        with t1:
            if st.button("⏱️ 1 min", use_container_width=True):
                _start_timer(60)
        with t2:
            if st.button("⏱️ 5 min", use_container_width=True):
                _start_timer(300)
        with t3:
            if st.button("⏱️ 10 min", use_container_width=True):
                _start_timer(600)

        # Navigation
        n1, n2, n3 = st.columns(3)
        with n1:
            if st.button("⬅️ Etape precedente", disabled=step == 0, use_container_width=True):
                st.session_state.current_step = max(0, step - 1)
                st.rerun()
        with n2:
            if st.button("🔄 Recommencer", use_container_width=True):
                st.session_state.current_step = 0
                st.rerun()
        with n3:
            if st.button("Etape suivante ➡️", type="primary", use_container_width=True):
                st.session_state.current_step = min(total - 1, step + 1)
                if st.session_state.current_step >= total - 1 and step == total - 1:
                    st.session_state.current_step = total
                st.rerun()
    else:
        # Fin de la recette
        st.balloons()
        st.markdown("""
        <div style="
          padding: 48px;
          background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
          border-radius: 20px;
          color: white;
          text-align: center;
          margin: 20px 0;
        ">
          <div style="font-size: 64px;">🎉</div>
          <h2 style="color: white; margin: 16px 0;">Bravo !</h2>
          <p style="color: rgba(255,255,255,0.9); font-size: 18px;">Ton plat est pret. Bon appetit !</p>
        </div>
        """, unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🔄 Refaire la recette", use_container_width=True):
                st.session_state.current_step = 0
                st.rerun()
        with b2:
            if st.button("🍳 Generer une autre recette", type="primary", use_container_width=True):
                st.session_state.page = "generer"
                st.session_state.recipe = None
                st.rerun()


def render_nutrition_native(nutrition: dict):
    """Tableau nutritionnel avec composants Streamlit natifs (fiable, pas de HTML inline)."""
    st.markdown("#### 📊 Tableau nutritionnel")
    st.caption("Valeurs par personne · AJR = Apports Journaliers Recommandes (adulte)")

    cal = nutrition.get("calories_par_personne", 0)
    prot = nutrition.get("proteines_g", 0)
    gluc = nutrition.get("glucides_g", 0)
    lip = nutrition.get("lipides_g", 0)
    fib = nutrition.get("fibres_g", 0)

    # Ligne 1 : 5 metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("Calories", f"{cal} kcal")
    with m2: st.metric("Proteines", f"{prot} g")
    with m3: st.metric("Glucides", f"{gluc} g")
    with m4: st.metric("Lipides", f"{lip} g")
    with m5: st.metric("Fibres", f"{fib} g")

    # Ligne 2 : barres de progression vs AJR
    refs = [("Calories", cal, 2000, "kcal"),
            ("Proteines", prot, 50, "g"),
            ("Glucides", gluc, 260, "g"),
            ("Lipides", lip, 70, "g"),
            ("Fibres", fib, 30, "g")]
    st.caption("**% des apports journaliers couvert par ce plat**")
    for label, val, ref, unit in refs:
        pct = min(1.0, val / ref) if ref else 0
        st.progress(pct, text=f"{label} : {val}{unit} / {ref}{unit} ({int(pct*100)}%)")


def render_share_panel(recipe: dict):
    """Panneau de partage : recette en texte brut + bouton copier."""
    txt = f"🍽️ {recipe.get('drapeau', '')} {recipe['nom']}\n"
    txt += f"Origine : {recipe.get('origine', '-')} · {recipe.get('temps_total', 'N/A')} · Pour {st.session_state.personnes} pers.\n"
    if recipe.get("cout_estime_eur"):
        txt += f"Cout : ~{recipe['cout_estime_eur']:.2f} €\n"
    txt += "\n--- INGREDIENTS ---\n"
    for ing in recipe.get("ingredients", []):
        txt += f"- {ing}\n"
    txt += "\n--- PREPARATION ---\n"
    for i, etape in enumerate(recipe.get("etapes", []), 1):
        txt += f"{i}. {etape}\n"
    if recipe.get("astuce_chef"):
        txt += f"\n💡 Astuce : {recipe['astuce_chef']}\n"
    txt += f"\nGenere avec NutriRecettes - Source : {recipe.get('source', 'IA')}"

    # Encode pour JS (echapper guillemets et retours ligne)
    import json as _json
    txt_js = _json.dumps(txt)

    components_v1.html(f"""
    <div style="background: #F0F9FF; border: 1px solid #38BDF8; padding: 16px; border-radius: 14px; font-family: -apple-system, sans-serif;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div style="font-size: 13px; color: #0369A1; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">🔗 Partager la recette</div>
        <button id="copyBtn" onclick="copyRecipe()" style="
          background: #FF6B35; color: white; border: none; padding: 8px 16px; border-radius: 8px;
          font-weight: 600; cursor: pointer; font-size: 13px;
        ">📋 Copier le texte</button>
      </div>
      <textarea id="recipeTxt" readonly style="
        width: 100%; min-height: 140px; padding: 12px; border: 1px solid #BAE6FD; border-radius: 10px;
        font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size: 12px; background: white; color: #0F172A; resize: vertical;
      ">{txt.replace('<', '&lt;').replace('>', '&gt;')}</textarea>
      <div id="msg" style="margin-top: 8px; font-size: 12px; color: #16A34A; font-weight: 600; min-height: 16px;"></div>
    </div>
    <script>
      const text = {txt_js};
      function copyRecipe() {{
        navigator.clipboard.writeText(text).then(() => {{
          document.getElementById('msg').textContent = '✅ Recette copiee dans le presse-papier !';
          document.getElementById('copyBtn').textContent = '✅ Copie !';
          setTimeout(() => {{
            document.getElementById('msg').textContent = '';
            document.getElementById('copyBtn').textContent = '📋 Copier le texte';
          }}, 2500);
        }}).catch(() => {{
          // Fallback : selectionne le texte pour copie manuelle
          document.getElementById('recipeTxt').select();
          document.execCommand('copy');
          document.getElementById('msg').textContent = '✅ Texte selectionne, Cmd+C pour copier';
        }});
      }}
    </script>
    """, height=280)


def _start_timer(seconds: int):
    """Affiche un timer countdown JS qui sonne a la fin."""
    components_v1.html(f"""
    <div id="timer" style="
      padding: 24px;
      background: #FF6B35;
      color: white;
      border-radius: 16px;
      text-align: center;
      font-family: -apple-system, sans-serif;
      box-shadow: 0 4px 16px rgba(255,107,53,0.3);
    ">
      <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 2px; opacity: 0.8;">Minuteur</div>
      <div id="time" style="font-size: 64px; font-weight: 900; margin: 8px 0; font-variant-numeric: tabular-nums;">{seconds // 60:02d}:{seconds % 60:02d}</div>
      <div id="status" style="font-size: 14px; opacity: 0.9;">En cours...</div>
    </div>
    <script>
      let total = {seconds};
      const el = document.getElementById('time');
      const status = document.getElementById('status');
      const interval = setInterval(() => {{
        total--;
        const m = Math.floor(total / 60);
        const s = total % 60;
        el.textContent = (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
        if (total <= 0) {{
          clearInterval(interval);
          el.textContent = '00:00';
          status.textContent = '⏰ Temps ecoule !';
          document.getElementById('timer').style.background = '#22C55E';
          try {{
            const audio = new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=');
            audio.play().catch(()=>{{}});
          }} catch(e) {{}}
        }}
      }}, 1000);
    </script>
    """, height=160)


# ------------------------------------------------------------
# Page : Mon carnet
# ------------------------------------------------------------
def page_carnet():
    st.markdown("## 📖 Mon carnet de recettes")
    st.caption("Tes recettes preferees, sauvegardees pour cette session.")

    if not st.session_state.carnet:
        st.info("Ton carnet est vide. Genere une recette puis clique sur 'Sauvegarder' pour l'ajouter ici.")
        if st.button("🍳 Generer ma premiere recette", type="primary"):
            st.session_state.page = "generer"
            st.rerun()
        return

    st.markdown(f"**{len(st.session_state.carnet)} recette(s) sauvegardee(s)**")
    st.markdown("---")

    for i, recipe in enumerate(st.session_state.carnet):
        with st.container():
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.markdown(f"### {recipe.get('drapeau', '🍽️')} {recipe['nom']}")
                st.caption(f"{recipe.get('origine', '-')} · {recipe.get('temps_total', 'N/A')} · {recipe.get('source', '')}")
            with c2:
                if st.button("👀 Voir", key=f"voir_{i}", use_container_width=True):
                    st.session_state.recipe = recipe
                    st.session_state.page = "generer"
                    st.rerun()
            with c3:
                if st.button("🗑️ Retirer", key=f"del_{i}", use_container_width=True):
                    st.session_state.carnet.pop(i)
                    st.rerun()
            st.markdown("---")


# ------------------------------------------------------------
# Router
# ------------------------------------------------------------
page = st.session_state.page

if page == "splash":
    # Pas de nav sur le splash, pleine page
    page_splash()
else:
    render_nav()
    if page == "accueil":
        page_accueil()
    elif page == "generer":
        page_generer()
    elif page == "cuisine":
        page_cuisine()
    elif page == "carnet":
        page_carnet()
