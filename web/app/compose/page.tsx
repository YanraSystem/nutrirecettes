"use client";

import {
  Suspense,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import {
  countryIdToCuisine,
  CUISINE_OPTIONS,
  type CuisineLabel,
} from "@/lib/cuisine-mapping";

/* ----------------------------------------------------------------------------
 * Données
 * -------------------------------------------------------------------------- */

const ALIMENTS = {
  "Protéines": [
    "Poulet",
    "Bœuf",
    "Agneau",
    "Porc",
    "Poisson",
    "Saumon",
    "Thon",
    "Crevettes",
    "Œuf",
    "Tofu",
    "Lentilles",
    "Pois chiches",
    "Haricots rouges",
  ],
  "Légumes": [
    "Tomate",
    "Oignon",
    "Ail",
    "Carotte",
    "Courgette",
    "Poivron",
    "Aubergine",
    "Épinards",
    "Salade",
    "Brocoli",
    "Champignon",
    "Concombre",
    "Pomme de terre",
  ],
  "Féculents": [
    "Riz",
    "Pâtes",
    "Semoule",
    "Quinoa",
    "Boulgour",
    "Pain",
    "Couscous",
  ],
  "Herbes & Épices": [
    "Basilic",
    "Persil",
    "Coriandre",
    "Menthe",
    "Curry",
    "Curcuma",
    "Cumin",
    "Paprika",
    "Gingembre",
    "Cannelle",
    "Safran",
    "Ras el hanout",
  ],
  "Produits laitiers": ["Lait", "Yaourt", "Fromage", "Beurre", "Crème"],
} as const;

type Category = keyof typeof ALIMENTS;
const CATEGORIES = Object.keys(ALIMENTS) as Category[];

// Emoji par ingrédient (affichage uniquement, la valeur stockée reste le nom propre)
const EMOJIS: Record<string, string> = {
  Poulet: "🍗", Bœuf: "🥩", Agneau: "🐑", Porc: "🥓",
  Poisson: "🐟", Saumon: "🍣", Thon: "🐠", Crevettes: "🍤",
  Œuf: "🥚", Tofu: "🧈", Lentilles: "🫘", "Pois chiches": "🫛",
  "Haricots rouges": "🫘",
  Tomate: "🍅", Oignon: "🧅", Ail: "🧄", Carotte: "🥕",
  Courgette: "🥒", Poivron: "🫑", Aubergine: "🍆", Épinards: "🥬",
  Salade: "🥗", Brocoli: "🥦", Champignon: "🍄", Concombre: "🥒",
  "Pomme de terre": "🥔",
  Riz: "🍚", Pâtes: "🍝", Semoule: "🌾", Quinoa: "🌾",
  Boulgour: "🌾", Pain: "🥖", Couscous: "🍲",
  Basilic: "🌿", Persil: "🌿", Coriandre: "🌿", Menthe: "🍃",
  Curry: "🌶️", Curcuma: "🟡", Cumin: "🟤", Paprika: "🔴",
  Gingembre: "🫚", Cannelle: "🌰", Safran: "🌸", "Ras el hanout": "✨",
  Lait: "🥛", Yaourt: "🍶", Fromage: "🧀", Beurre: "🧈", Crème: "🍦",
};

// Accent couleur par categorie (CSS vars pour eviter les problemes JIT Tailwind v4)
const CATEGORY_ACCENT: Record<Category, { color: string; soft: string }> = {
  "Protéines":       { color: "var(--terracotta)", soft: "rgba(201,123,95,0.4)"  },
  "Légumes":         { color: "var(--sage-deep)",  soft: "rgba(95,112,80,0.4)"   },
  "Féculents":       { color: "var(--safran)",     soft: "rgba(201,154,79,0.4)"  },
  "Herbes & Épices": { color: "var(--paprika)",    soft: "rgba(184,88,71,0.4)"   },
  "Produits laitiers": { color: "var(--azur)",     soft: "rgba(74,107,133,0.4)"  },
};

const REGIMES = [
  "Aucun",
  "Végétarien",
  "Halal",
  "Sans gluten",
  "Sans lactose",
] as const;
type Regime = (typeof REGIMES)[number];

/* ----------------------------------------------------------------------------
 * Selectbox custom (editorial)
 * -------------------------------------------------------------------------- */

type EditorialSelectProps<T extends string> = {
  label: string;
  value: T;
  options: ReadonlyArray<T>;
  onChange: (v: T) => void;
  disabled?: boolean;
};

function EditorialSelect<T extends string>({
  label,
  value,
  options,
  onChange,
  disabled,
}: EditorialSelectProps<T>) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handle(e: MouseEvent) {
      if (!ref.current) return;
      if (!ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handle);
    return () => document.removeEventListener("mousedown", handle);
  }, []);

  return (
    <div ref={ref} className="relative">
      <span className="block text-[0.6rem] font-medium uppercase tracking-[0.28em] text-terracotta">
        {label}
      </span>
      <div className="mt-2 border-b border-terracotta/30 pb-2">
        <button
          type="button"
          disabled={disabled}
          onClick={() => setOpen((o) => !o)}
          className="flex w-full items-center justify-between gap-3 text-left font-serif text-2xl italic text-charcoal transition-colors hover:text-terracotta disabled:opacity-40"
        >
          <span>{value}</span>
          <span
            className={`text-xs text-warm-gray transition-transform duration-300 ${
              open ? "rotate-180" : ""
            }`}
            aria-hidden
          >
            ▾
          </span>
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.ul
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.18, ease: [0.25, 0, 0, 1] }}
            className="absolute left-0 right-0 top-full z-40 mt-2 border border-charcoal/10 bg-creme py-2 shadow-[0_24px_60px_-24px_rgba(45,42,38,0.35)]"
          >
            {options.map((opt) => {
              const active = opt === value;
              return (
                <li key={opt}>
                  <button
                    type="button"
                    onClick={() => {
                      onChange(opt);
                      setOpen(false);
                    }}
                    className={`flex w-full items-center justify-between px-4 py-2 font-serif text-base italic transition-colors ${
                      active
                        ? "text-terracotta"
                        : "text-charcoal hover:bg-creme-warm hover:text-terracotta"
                    }`}
                  >
                    <span>{opt}</span>
                    {active && (
                      <span className="text-[0.6rem] uppercase tracking-[0.28em]">
                        ✓
                      </span>
                    )}
                  </button>
                </li>
              );
            })}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ----------------------------------------------------------------------------
 * Stepper Personnes
 * -------------------------------------------------------------------------- */

function PersonStepper({
  value,
  onChange,
  disabled,
}: {
  value: number;
  onChange: (v: number) => void;
  disabled?: boolean;
}) {
  const dec = () => onChange(Math.max(1, value - 1));
  const inc = () => onChange(Math.min(12, value + 1));
  return (
    <div>
      <span className="block text-[0.6rem] font-medium uppercase tracking-[0.28em] text-terracotta">
        Personnes
      </span>
      <div className="mt-2 flex items-center justify-between border-b border-terracotta/30 pb-2">
        <button
          type="button"
          onClick={dec}
          disabled={disabled || value <= 1}
          aria-label="Diminuer le nombre de personnes"
          className="flex h-9 w-9 items-center justify-center border border-charcoal/20 text-base text-charcoal transition-all hover:border-terracotta hover:text-terracotta disabled:opacity-30"
        >
          −
        </button>
        <span className="font-serif text-3xl italic text-charcoal tabular-nums">
          {value}
        </span>
        <button
          type="button"
          onClick={inc}
          disabled={disabled || value >= 12}
          aria-label="Augmenter le nombre de personnes"
          className="flex h-9 w-9 items-center justify-center border border-charcoal/20 text-base text-charcoal transition-all hover:border-terracotta hover:text-terracotta disabled:opacity-30"
        >
          +
        </button>
      </div>
    </div>
  );
}

/* ----------------------------------------------------------------------------
 * Toggle pill ingrédient
 * -------------------------------------------------------------------------- */

function IngredientPill({
  label,
  selected,
  onToggle,
  disabled,
  accentColor,
}: {
  label: string;
  selected: boolean;
  onToggle: () => void;
  disabled?: boolean;
  accentColor?: string;
}) {
  const emoji = EMOJIS[label] ?? "";
  const color = accentColor ?? "var(--terracotta)";
  return (
    <motion.button
      type="button"
      onClick={onToggle}
      disabled={disabled}
      whileTap={{ scale: 0.97 }}
      onMouseEnter={(e) => {
        if (!selected) e.currentTarget.style.borderColor = color;
      }}
      onMouseLeave={(e) => {
        if (!selected) e.currentTarget.style.borderColor = "rgba(45,42,38,0.1)";
      }}
      transition={{ type: "spring", stiffness: 500, damping: 28 }}
      className={`group relative w-full overflow-hidden border px-4 py-2.5 text-left text-[0.875rem] transition-all duration-200 ease-out disabled:opacity-50 ${
        selected
          ? "bg-charcoal text-creme hover:-translate-y-px"
          : "border-charcoal/10 bg-creme text-charcoal hover:-translate-y-px hover:shadow-[0_8px_24px_-16px_rgba(45,42,38,0.4)]"
      }`}
      style={selected ? { borderColor: color, boxShadow: `0 0 0 1px ${color}` } : undefined}
    >
      <span className="relative z-10 inline-flex items-center gap-2.5">
        {emoji && <span className="text-base leading-none">{emoji}</span>}
        <span>{label}</span>
      </span>
      {selected && (
        <span
          className="absolute right-3 top-1/2 -translate-y-1/2 text-[0.6rem] tracking-[0.2em]"
          style={{ color }}
          aria-hidden
        >
          ●
        </span>
      )}
    </motion.button>
  );
}

/* ----------------------------------------------------------------------------
 * Équilibre nutritionnel (vert / orange / rouge)
 * -------------------------------------------------------------------------- */

function computeBalance(selected: Set<string>): {
  status: "ok" | "warn" | "bad";
  label: string;
} {
  const hasProtein = ALIMENTS["Protéines"].some((p) => selected.has(p));
  const hasVeg = ALIMENTS["Légumes"].some((p) => selected.has(p));
  const hasStarch = ALIMENTS["Féculents"].some((p) => selected.has(p));
  const score =
    (hasProtein ? 1 : 0) + (hasVeg ? 1 : 0) + (hasStarch ? 1 : 0);
  if (score === 3) return { status: "ok", label: "Équilibre complet" };
  if (score === 2) return { status: "warn", label: "Équilibre presque là" };
  return { status: "bad", label: "Manque d'équilibre" };
}

/* ----------------------------------------------------------------------------
 * Compose Inner (utilise useSearchParams → wrap dans Suspense)
 * -------------------------------------------------------------------------- */

type ApiResponse = {
  recipe?: unknown;
  [key: string]: unknown;
};

function ComposeInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialCuisineId = searchParams.get("cuisine");
  const surpriseFlag = searchParams.get("surprise") === "1";

  const [cuisine, setCuisine] = useState<CuisineLabel>(() =>
    countryIdToCuisine(initialCuisineId),
  );
  const [personnes, setPersonnes] = useState<number>(2);
  const [regime, setRegime] = useState<Regime>("Aucun");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const surpriseRan = useRef(false);

  const allIngredients = useMemo(
    () => CATEGORIES.flatMap((c) => ALIMENTS[c]),
    [],
  );

  const drawRandom = useCallback(() => {
    const count = 4 + Math.floor(Math.random() * 4); // 4–7
    const shuffled = [...allIngredients].sort(() => Math.random() - 0.5);
    setSelected(new Set(shuffled.slice(0, count)));
  }, [allIngredients]);

  // Auto-déclenchement si ?surprise=1
  useEffect(() => {
    if (surpriseFlag && !surpriseRan.current) {
      surpriseRan.current = true;
      drawRandom();
      if (!initialCuisineId) {
        const realCuisines = CUISINE_OPTIONS.filter(
          (c) => c !== "Surprends-moi",
        );
        setCuisine(
          realCuisines[
            Math.floor(Math.random() * realCuisines.length)
          ] as CuisineLabel,
        );
      }
    }
  }, [surpriseFlag, drawRandom, initialCuisineId]);

  const toggle = (item: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(item)) next.delete(item);
      else next.add(item);
      return next;
    });
  };

  const selectedList = useMemo(() => Array.from(selected), [selected]);
  const balance = useMemo(() => computeBalance(selected), [selected]);

  const submit = async () => {
    if (selectedList.length === 0 || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/recipe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ingredients: selectedList,
          cuisine,
          personnes,
          regime,
        }),
      });
      if (!res.ok) {
        throw new Error(`Erreur API ${res.status}`);
      }
      const data: ApiResponse = await res.json();
      sessionStorage.setItem("currentRecipe", JSON.stringify(data));
      router.push("/recipe");
    } catch (e) {
      const msg =
        e instanceof Error ? e.message : "Impossible de générer la recette";
      setError(msg);
      setSubmitting(false);
    }
  };

  const balanceColor =
    balance.status === "ok"
      ? "bg-sage"
      : balance.status === "warn"
        ? "bg-terracotta"
        : "bg-terracotta-dark";

  return (
    <main className="relative min-h-screen bg-creme text-charcoal">
      {/* Section 1 — Header de page */}
      <section className="mx-auto max-w-7xl px-6 pt-16 sm:px-10 lg:pt-24">
        <div className="flex items-start justify-between gap-6">
          <div>
            <p className="text-[0.65rem] font-medium uppercase tracking-[0.32em] text-terracotta">
              — Étape 1
            </p>
            <h1 className="mt-6 font-serif text-[clamp(3rem,7vw,6rem)] italic leading-[0.95] tracking-[-0.03em] text-charcoal">
              Composez votre carte
            </h1>
            <p className="mt-8 max-w-2xl font-serif text-[clamp(1.05rem,1.4vw,1.35rem)] italic leading-[1.55] text-warm-gray">
              Sélectionnez les ingrédients à votre disposition. La cuisine du
              monde s'invitera ensuite à votre table.
            </p>
          </div>

          <button
            type="button"
            onClick={() => router.push("/")}
            className="hidden shrink-0 self-start border border-charcoal/20 px-5 py-2.5 text-[0.6rem] font-medium uppercase tracking-[0.28em] text-charcoal transition-all hover:border-terracotta hover:text-terracotta sm:inline-flex"
          >
            ← Retour
          </button>
        </div>
      </section>

      {/* Section 2 — Préférences (bandeau sticky) */}
      <section className="sticky top-0 z-30 mt-16 border-y border-charcoal/10 bg-creme/95 backdrop-blur-md">
        <div className="mx-auto max-w-7xl px-6 py-6 sm:px-10">
          <div className="grid grid-cols-1 gap-x-10 gap-y-6 sm:grid-cols-2 lg:grid-cols-4">
            <EditorialSelect<CuisineLabel>
              label="Cuisine"
              value={cuisine}
              options={CUISINE_OPTIONS}
              onChange={setCuisine}
              disabled={submitting}
            />
            <PersonStepper
              value={personnes}
              onChange={setPersonnes}
              disabled={submitting}
            />
            <EditorialSelect<Regime>
              label="Régime"
              value={regime}
              options={REGIMES}
              onChange={setRegime}
              disabled={submitting}
            />
            <div>
              <span className="block text-[0.6rem] font-medium uppercase tracking-[0.28em] text-terracotta">
                Inspiration
              </span>
              <div className="mt-2 border-b border-terracotta/30 pb-2">
                <button
                  type="button"
                  onClick={drawRandom}
                  disabled={submitting}
                  className="group flex w-full items-center justify-between font-serif text-2xl italic text-charcoal transition-colors hover:text-terracotta disabled:opacity-40"
                >
                  <span>Tirer au sort</span>
                  <span className="text-[0.6rem] uppercase tracking-[0.28em] text-warm-gray transition-transform group-hover:translate-x-1">
                    →
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 3 — Picker d'ingrédients */}
      <section className="mx-auto max-w-7xl px-6 pb-48 pt-16 sm:px-10 sm:pt-20">
        <div className="grid grid-cols-1 gap-x-10 gap-y-14 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {CATEGORIES.map((cat) => {
            const accent = CATEGORY_ACCENT[cat];
            return (
              <div key={cat}>
                <div className="mb-6">
                  <h2
                    className="font-serif text-2xl italic"
                    style={{ color: accent.color }}
                  >
                    {cat}
                  </h2>
                  <span
                    className="mt-2 block h-px w-10"
                    style={{ background: accent.soft }}
                  />
                </div>
                <ul className="space-y-2.5">
                  {ALIMENTS[cat].map((item) => (
                    <li key={item}>
                      <IngredientPill
                        label={item}
                        selected={selected.has(item)}
                        onToggle={() => toggle(item)}
                        disabled={submitting}
                        accentColor={accent.color}
                      />
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>

        {/* Footer note éditorial */}
        <p className="mt-24 max-w-xl font-serif text-base italic text-mute">
          — Cochez ce que vous avez dans le frigo. Les manques sont rarement
          des obstacles, plus souvent des prétextes à l'invention.
        </p>
      </section>

      {/* Section 4 — Bottom bar fixed */}
      <AnimatePresence>
        {selected.size > 0 && (
          <motion.div
            initial={{ y: 120, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 120, opacity: 0 }}
            transition={{ duration: 0.4, ease: [0.25, 0, 0, 1] }}
            className="fixed inset-x-0 bottom-0 z-50 border-t border-charcoal/10 bg-creme/95 backdrop-blur-md"
          >
            <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-5 sm:px-10 lg:flex-row lg:items-center lg:gap-8">
              {/* Compteur + équilibre */}
              <div className="flex items-center gap-4 lg:shrink-0">
                <span
                  aria-hidden
                  className={`inline-block h-2.5 w-2.5 rounded-full ${balanceColor}`}
                />
                <div>
                  <p className="font-serif text-xl italic text-charcoal">
                    {selected.size} ingrédient{selected.size > 1 ? "s" : ""}{" "}
                    sélectionné{selected.size > 1 ? "s" : ""}
                  </p>
                  <p className="text-[0.65rem] uppercase tracking-[0.28em] text-mute">
                    {balance.label}
                  </p>
                </div>
              </div>

              {/* Pills horizontalement scrollables */}
              <div className="min-w-0 flex-1 overflow-x-auto">
                <ul className="flex items-center gap-2 whitespace-nowrap">
                  {selectedList.map((item) => (
                    <li
                      key={item}
                      className="flex items-center gap-2 border border-charcoal/15 bg-creme-warm px-3 py-1.5 text-[0.75rem] text-charcoal"
                    >
                      <span>{item}</span>
                      <button
                        type="button"
                        onClick={() => toggle(item)}
                        aria-label={`Retirer ${item}`}
                        className="text-mute transition-colors hover:text-terracotta"
                      >
                        ×
                      </button>
                    </li>
                  ))}
                </ul>
              </div>

              {/* CTA */}
              <button
                type="button"
                onClick={submit}
                disabled={submitting || selected.size === 0}
                className="group relative inline-flex shrink-0 items-center justify-center gap-3 bg-charcoal px-8 py-4 text-[0.7rem] font-medium uppercase tracking-[0.28em] text-creme transition-all duration-300 hover:bg-terracotta disabled:cursor-not-allowed disabled:opacity-60"
              >
                {submitting ? (
                  <>
                    <span
                      aria-hidden
                      className="h-3 w-3 animate-spin rounded-full border border-creme/40 border-t-creme"
                    />
                    <span className="font-serif text-sm italic normal-case tracking-normal">
                      Composition en cours…
                    </span>
                  </>
                ) : (
                  <>
                    <span>Générer la recette</span>
                    <span className="transition-transform duration-300 group-hover:translate-x-1">
                      →
                    </span>
                  </>
                )}
              </button>
            </div>

            {/* Toast erreur */}
            <AnimatePresence>
              {error && (
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="mx-auto max-w-7xl border-t border-terracotta/30 bg-terracotta/5 px-6 py-3 font-serif text-sm italic text-terracotta-dark sm:px-10"
                  role="status"
                >
                  — {error}. La table attendra.
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}

/* ----------------------------------------------------------------------------
 * Page (wrap Suspense pour useSearchParams en Next.js 16)
 * -------------------------------------------------------------------------- */

function ComposeFallback() {
  return (
    <main className="min-h-screen bg-creme px-8 py-24 text-charcoal">
      <p className="text-[0.65rem] font-medium uppercase tracking-[0.32em] text-terracotta">
        — Étape 1
      </p>
      <h1 className="mt-6 font-serif text-6xl italic">Composez votre carte</h1>
    </main>
  );
}

export default function ComposePage() {
  return (
    <Suspense fallback={<ComposeFallback />}>
      <ComposeInner />
    </Suspense>
  );
}
