"use client";

import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";

const Planet3D = dynamic(() => import("@/components/Planet3D"), { ssr: false });

export default function Home() {
  const router = useRouter();

  return (
    <main className="relative min-h-screen overflow-hidden bg-charcoal text-creme">
      {/* Planete 3D interactive — couvre toute la zone droite */}
      <div className="absolute inset-0 z-0">
        <Planet3D
          onCuisineSelect={(id) => router.push(`/compose?cuisine=${id}`)}
        />
      </div>

      {/* Overlay gradient pour lisibilite du texte cote gauche */}
      <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-1/2 bg-gradient-to-r from-charcoal via-charcoal/80 to-transparent" />

      <section className="pointer-events-none relative z-20 mx-auto flex min-h-screen max-w-7xl flex-col justify-between px-8 py-10">
        {/* Header */}
        <header className="flex items-center justify-between text-[0.65rem] uppercase tracking-[0.32em] text-mute">
          <span className="font-medium text-creme">NutriRecettes</span>
          <span className="font-medium">N°01 — Édition Première · 2026</span>
        </header>

        {/* Bloc editorial gauche */}
        <div className="max-w-xl">
          <p className="mb-6 text-[0.65rem] uppercase tracking-[0.32em] text-terracotta">
            — Une planète de saveurs
          </p>
          <h1 className="font-serif text-[clamp(3.5rem,8vw,7rem)] italic leading-[0.92] tracking-[-0.04em] text-creme">
            Compose,
            <br />
            <span className="text-terracotta">découvre,</span>
            <br />
            cuisine.
          </h1>
          <p className="mt-10 max-w-md font-sans text-[0.95rem] leading-[1.7] text-creme/75">
            Dix-neuf cuisines du monde, accessibles d'un geste. Faites tourner
            la planète, posez le doigt sur un pays — la recette suit.
          </p>

          {/* CTAs sobres editorial */}
          <div className="pointer-events-auto mt-10 flex flex-wrap gap-3">
            <button
              onClick={() => router.push("/compose")}
              className="group border border-creme/30 px-7 py-3 text-[0.7rem] font-medium uppercase tracking-[0.25em] text-creme transition-all duration-300 hover:border-terracotta hover:bg-terracotta hover:text-creme"
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
              className="border border-transparent px-4 py-3 text-[0.7rem] font-medium uppercase tracking-[0.25em] text-creme/60 transition-colors duration-300 hover:text-creme"
            >
              ou tirer au sort
            </button>
          </div>
        </div>

        {/* Footer */}
        <footer className="flex items-end justify-between text-[0.6rem] uppercase tracking-[0.3em] text-mute">
          <span className="flex items-center gap-3">
            <span className="inline-block h-px w-12 bg-mute" />
            Faites pivoter — survolez un pays
          </span>
          <span>Carnet de cuisine</span>
        </footer>
      </section>
    </main>
  );
}
