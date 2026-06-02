"use client";

import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import NebulaSplash from "@/components/NebulaSplash";

const Planet3D = dynamic(() => import("@/components/Planet3D"), { ssr: false });

export default function Home() {
  const router = useRouter();
  const [showSplash, setShowSplash] = useState(true);

  // Si l'utilisateur a deja entre dans la session, skip le splash
  useEffect(() => {
    if (sessionStorage.getItem("nutri:entered") === "1") {
      setShowSplash(false);
    }
  }, []);

  const dismissSplash = () => {
    sessionStorage.setItem("nutri:entered", "1");
    setShowSplash(false);
  };

  if (showSplash) {
    return <NebulaSplash onDismiss={dismissSplash} />;
  }

  return (
    <main
      className="relative min-h-screen overflow-hidden"
      style={{
        background:
          "linear-gradient(160deg, #1A0A24 0%, #2A1338 60%, #3A2050 100%)",
        color: "var(--text-primary)",
      }}
    >
      {/* Planete 3D interactive — couvre toute la zone droite */}
      <div className="absolute inset-0 z-0">
        <Planet3D
          onCuisineSelect={(id) => router.push(`/compose?cuisine=${id}`)}
        />
      </div>

      {/* Glow magenta radial discret pour profondeur */}
      <div
        className="pointer-events-none absolute inset-0 z-[5]"
        style={{
          background:
            "radial-gradient(ellipse 60% 40% at 20% 60%, rgba(139,58,106,0.25) 0%, rgba(139,58,106,0) 60%)",
        }}
      />

      {/* Overlay gradient pour lisibilite du texte cote gauche — aubergine */}
      <div
        className="pointer-events-none absolute inset-y-0 left-0 z-10 w-1/2"
        style={{
          background:
            "linear-gradient(90deg, rgba(26,10,36,0.92) 0%, rgba(42,19,56,0.78) 50%, rgba(42,19,56,0) 100%)",
        }}
      />

      <section className="pointer-events-none relative z-20 mx-auto flex min-h-screen max-w-7xl flex-col justify-between px-8 py-10">
        {/* Header */}
        <header
          className="flex items-center justify-between text-[0.65rem] uppercase tracking-[0.32em]"
          style={{ color: "var(--text-muted)" }}
        >
          <span
            className="font-medium"
            style={{ color: "var(--text-primary)" }}
          >
            NutriRecettes
          </span>
          <span className="font-medium">N°01 — Édition Première · 2026</span>
        </header>

        {/* Bloc editorial gauche */}
        <div className="max-w-xl">
          <p
            className="mb-6 text-[0.65rem] uppercase tracking-[0.32em]"
            style={{ color: "var(--rose-poudre)" }}
          >
            — Une planète de saveurs
          </p>
          <h1
            className="font-serif text-[clamp(3.5rem,8vw,7rem)] italic leading-[0.92] tracking-[-0.04em]"
            style={{ color: "var(--text-primary)" }}
          >
            Compose,
            <br />
            <span
              className="text-gradient-gold-rose"
              style={{
                filter:
                  "drop-shadow(0 0 40px rgba(232, 168, 159, 0.35))",
              }}
            >
              découvre,
            </span>
            <br />
            cuisine.
          </h1>
          <p
            className="mt-10 max-w-md font-sans text-[0.95rem] leading-[1.7]"
            style={{ color: "rgba(248, 242, 234, 0.78)" }}
          >
            Dix-neuf cuisines du monde, accessibles d'un geste. Faites tourner
            la planète, posez le doigt sur un pays — la recette suit.
          </p>

          {/* CTAs sobres editorial */}
          <div className="pointer-events-auto mt-10 flex flex-wrap gap-3">
            <button
              onClick={() => router.push("/compose")}
              className="group px-7 py-3 text-[0.7rem] font-medium uppercase tracking-[0.25em] transition-all duration-300"
              style={{
                border: "1px solid rgba(232, 168, 159, 0.4)",
                color: "var(--text-primary)",
                background: "transparent",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "var(--or-doux)";
                e.currentTarget.style.borderColor = "var(--or-doux)";
                e.currentTarget.style.color = "var(--bg-deep)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "transparent";
                e.currentTarget.style.borderColor =
                  "rgba(232, 168, 159, 0.4)";
                e.currentTarget.style.color = "var(--text-primary)";
              }}
            >
              <span className="inline-flex items-center gap-3">
                Composer une recette
                <span className="transition-transform duration-300 group-hover:translate-x-1">
                  →
                </span>
              </span>
            </button>
            <button
              onClick={() => {
                router.push("/compose?surprise=1");
              }}
              className="border border-transparent px-4 py-3 text-[0.7rem] font-medium uppercase tracking-[0.25em] transition-colors duration-300"
              style={{ color: "rgba(248, 242, 234, 0.6)" }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = "var(--rose-bright)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = "rgba(248, 242, 234, 0.6)";
              }}
            >
              ou tirer au sort
            </button>
          </div>
        </div>

        {/* Footer */}
        <footer
          className="flex items-end justify-between text-[0.6rem] uppercase tracking-[0.3em]"
          style={{ color: "var(--text-muted)" }}
        >
          <span className="flex items-center gap-3">
            <span
              className="inline-block h-px w-12"
              style={{ background: "var(--text-muted)" }}
            />
            Faites pivoter — survolez un pays
          </span>
          <span>Carnet de cuisine</span>
        </footer>
      </section>
    </main>
  );
}
