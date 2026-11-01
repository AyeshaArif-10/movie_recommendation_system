import html

import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(
    page_title="Reel Picks",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================
# STYLES
# =============================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=DM+Sans:wght@400;500;700&display=swap');

:root {
  --bg: #12101A;
  --surface: #1C1928;
  --line: #2E2A40;
  --text: #ECE9F4;
  --muted: #9B96AE;
  --accent: #8B7CFF;
  --gold: #F2B84B;
}
html, body, .stApp { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1280px; padding-top: 1.5rem; padding-bottom: 4rem; }

/* top bar */
.brand { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.6rem; letter-spacing: -0.02em; }
.brand a { color: var(--text) !important; text-decoration: none; }
.brand span { color: var(--accent); }
.tagline { color: var(--muted); margin: 0.2rem 0 1.4rem; }

/* section headings */
.section-title { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.35rem; margin: 2rem 0 0.2rem; }
.section-sub { color: var(--muted); font-size: 0.92rem; margin-bottom: 0.9rem; }

/* poster grid */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--min, 170px), 1fr)); gap: 22px 18px; }
.row { display: grid; grid-auto-flow: column; grid-auto-columns: 158px; gap: 16px; overflow-x: auto; padding-bottom: 12px; scrollbar-color: var(--line) transparent; }
a.poster { display: block; text-decoration: none !important; color: var(--text) !important; }
.poster .img { aspect-ratio: 2 / 3; border-radius: 10px; overflow: hidden; background: var(--surface); outline: 2px solid transparent; outline-offset: 3px; transition: outline-color .15s; }
.poster .img img { width: 100%; height: 100%; object-fit: cover; display: block; }
.poster:hover .img, .poster:focus-visible .img { outline-color: var(--accent); }
.poster .noimg { height: 100%; display: flex; align-items: center; justify-content: center; text-align: center; padding: 12px; color: var(--muted); font-size: 0.85rem; }
.poster .name { margin-top: 8px; font-size: 0.92rem; line-height: 1.25rem; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.poster .year { color: var(--muted); font-size: 0.8rem; }

/* details hero */
.hero { position: relative; border-radius: 18px; overflow: hidden; background-color: var(--surface); background-size: cover; background-position: center 20%; border: 1px solid var(--line); }
.hero-inner { display: flex; gap: 32px; padding: 32px; background: linear-gradient(90deg, rgba(18,16,26,.96) 0%, rgba(18,16,26,.82) 55%, rgba(18,16,26,.55) 100%); }
.hero-poster { flex: 0 0 240px; }
.hero-poster img { width: 100%; border-radius: 12px; display: block; }
.hero-info { flex: 1; min-width: 0; }
.hero-info h1 { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: clamp(1.8rem, 4vw, 3rem); letter-spacing: -0.03em; line-height: 1.05; margin: 0 0 0.6rem; padding: 0; }
.meta { color: var(--muted); font-size: 0.95rem; margin-bottom: 0.9rem; }
.rating { color: var(--gold); font-weight: 700; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1.1rem; }
.chip { border: 1px solid var(--line); background: rgba(28,25,40,.8); border-radius: 999px; padding: 4px 12px; font-size: 0.84rem; }
.overview { max-width: 62ch; line-height: 1.65; }
a.back { display: inline-block; color: var(--muted) !important; text-decoration: none !important; margin-bottom: 1rem; font-size: 0.95rem; }
a.back:hover { color: var(--text) !important; }
@media (max-width: 720px) {
  .hero-inner { flex-direction: column; padding: 20px; }
  .hero-poster { flex-basis: auto; max-width: 200px; }
}

/* streamlit widgets */
div[data-testid="stTextInput"] input { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 0.8rem 1rem; font-size: 1rem; }
div[data-testid="stTextInput"] input:focus { border-color: var(--accent); }
div[role="radiogroup"] { gap: 8px; flex-wrap: wrap; }
div[role="radiogroup"] label { background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 4px 14px; }
div[role="radiogroup"] label > div:first-child { display: none; }
div[role="radiogroup"] label:has(input:checked) { background: var(--accent); border-color: var(--accent); }
div[role="radiogroup"] label:has(input:checked) p { color: #12101A; font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING (query params, so every movie has a shareable link)
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except ValueError:
        pass


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=120, show_spinner=False)
def api_get_json(path: str, params: dict | None = None):
    try:
        # Render free instances sleep; the first call can take a while.
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=60)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                }
            )
    return cards


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    """Handles both raw TMDB ({"results": [...]}) and card lists ([{tmdb_id, ...}])."""
    keyword_l = keyword.strip().lower()
    raw_items = []

    if isinstance(data, dict) and "results" in data:
        for m in data.get("results") or []:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            if not title or not tmdb_id:
                continue
            pp = m.get("poster_path")
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{pp}" if pp else None,
                    "release_date": m.get("release_date", ""),
                }
            )
    elif isinstance(data, list):
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": m.get("poster_url"),
                    "release_date": m.get("release_date", ""),
                }
            )
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched or raw_items

    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        suggestions.append((f"{x['title']} ({year})" if year else x["title"], x["tmdb_id"]))

    cards = [
        {
            "tmdb_id": x["tmdb_id"],
            "title": x["title"],
            "poster_url": x["poster_url"],
            "release_date": x.get("release_date", ""),
        }
        for x in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# RENDER HELPERS
# =============================
def poster_html(m: dict) -> str:
    tmdb_id = m.get("tmdb_id")
    if not tmdb_id:
        return ""
    title = html.escape(m.get("title") or "Untitled")
    poster = m.get("poster_url")
    year = html.escape((m.get("release_date") or "")[:4])
    img = (
        f'<img src="{html.escape(poster)}" alt="{title}" loading="lazy">'
        if poster
        else f'<div class="noimg">{title}</div>'
    )
    year_html = f'<div class="year">{year}</div>' if year else ""
    return (
        f'<a class="poster" href="?view=details&id={int(tmdb_id)}" target="_self">'
        f'<div class="img">{img}</div><div class="name">{title}</div>{year_html}</a>'
    )


def poster_grid(cards, min_width=170):
    if not cards:
        st.info("No movies to show.")
        return
    items = "".join(poster_html(m) for m in cards)
    st.markdown(
        f'<div class="grid" style="--min:{int(min_width)}px">{items}</div>',
        unsafe_allow_html=True,
    )


def poster_row(cards):
    if not cards:
        st.caption("Nothing to show here yet.")
        return
    items = "".join(poster_html(m) for m in cards)
    st.markdown(f'<div class="row">{items}</div>', unsafe_allow_html=True)


def section(title: str, sub: str = ""):
    st.markdown(f'<div class="section-title">{html.escape(title)}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="section-sub">{html.escape(sub)}</div>', unsafe_allow_html=True)


# =============================
# SIDEBAR (display options only)
# =============================
with st.sidebar:
    st.markdown("### Display")
    poster_size = st.slider("Poster size", 120, 260, 170, step=10)

# =============================
# HEADER
# =============================
st.markdown(
    '<div class="brand"><a href="?view=home" target="_self">Reel<span>Picks</span></a></div>'
    '<div class="tagline">Search a movie you like. Get ten more you will probably like too.</div>',
    unsafe_allow_html=True,
)

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    typed = st.text_input(
        "Search",
        placeholder="Search by title: batman, love, avengers…",
        label_visibility="collapsed",
    )

    # ---- Search mode
    if typed.strip():
        q = typed.strip()
        if len(q) < 2:
            st.caption("Type at least 2 characters to search.")
            st.stop()

        with st.spinner("Searching…"):
            data, err = api_get_json("/tmdb/search", params={"query": q})

        if err or data is None:
            st.error(f"Search failed. {err}")
            st.stop()

        suggestions, cards = parse_tmdb_search_to_cards(data, q, limit=24)

        if suggestions:
            labels = ["Jump straight to a movie…"] + [s[0] for s in suggestions]
            picked = st.selectbox("Quick pick", labels, index=0, label_visibility="collapsed")
            if picked != labels[0]:
                goto_details(dict(suggestions)[picked])

        section(f"Results for “{q}”", f"{len(cards)} movies")
        poster_grid(cards, poster_size)
        st.stop()

    # ---- Home feed
    categories = {
        "Trending": "trending",
        "Popular": "popular",
        "Top rated": "top_rated",
        "Now playing": "now_playing",
        "Upcoming": "upcoming",
    }
    choice = st.radio("Category", list(categories), horizontal=True, label_visibility="collapsed")

    with st.spinner("Loading movies… (the server may need a few seconds to wake up)"):
        home_cards, err = api_get_json("/home", params={"category": categories[choice], "limit": 24})

    if err or not home_cards:
        st.error(f"Couldn't load the {choice.lower()} list. {err or 'Try again in a moment.'}")
        st.stop()

    section(choice)
    poster_grid(home_cards, poster_size)

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id

    st.markdown('<a class="back" href="?view=home" target="_self">← All movies</a>', unsafe_allow_html=True)

    if not tmdb_id:
        st.warning("No movie selected. Pick one from the home page.")
        st.stop()

    with st.spinner("Loading movie…"):
        data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Couldn't load this movie. {err or 'Try again in a moment.'}")
        st.stop()

    title = html.escape(data.get("title") or "")
    year = (data.get("release_date") or "")[:4]
    genres = [html.escape(g["name"]) for g in data.get("genres", []) if g.get("name")]
    overview = html.escape(data.get("overview") or "No overview available.")
    poster = data.get("poster_url")
    backdrop = data.get("backdrop_url")
    rating = data.get("vote_average")
    runtime = data.get("runtime")

    meta_bits = []
    if year:
        meta_bits.append(year)
    if runtime:
        meta_bits.append(f"{int(runtime) // 60}h {int(runtime) % 60}m")
    if rating:
        meta_bits.append(f'<span class="rating">★ {float(rating):.1f}</span>')
    meta = " &nbsp;|&nbsp; ".join(meta_bits)

    bg = f"background-image:url('{html.escape(backdrop)}');" if backdrop else ""
    poster_block = (
        f'<div class="hero-poster"><img src="{html.escape(poster)}" alt="{title} poster"></div>'
        if poster
        else ""
    )
    chips = "".join(f'<span class="chip">{g}</span>' for g in genres)

    st.markdown(
        f'<div class="hero" style="{bg}"><div class="hero-inner">{poster_block}'
        f'<div class="hero-info"><h1>{title}</h1>'
        f'<div class="meta">{meta}</div><div class="chips">{chips}</div>'
        f'<div class="overview">{overview}</div></div></div></div>',
        unsafe_allow_html=True,
    )

    # ---- Recommendations
    raw_title = (data.get("title") or "").strip()
    if not raw_title:
        st.warning("No title available to compute recommendations.")
        st.stop()

    with st.spinner("Finding similar movies…"):
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": raw_title, "tfidf_top_n": 12, "genre_limit": 12},
        )

    if not err2 and bundle:
        section("Similar movies", "Matched on plot and description")
        poster_row(to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")))

        section("More in the same genres")
        poster_row(bundle.get("genre_recommendations", []))
    else:
        with st.spinner("Trying genre matches instead…"):
            genre_only, err3 = api_get_json("/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18})
        if not err3 and genre_only:
            section("More in the same genres")
            poster_row(genre_only)
        else:
            st.warning("No recommendations are available right now. Try again in a moment.")