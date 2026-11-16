// Which gameplay this build runs (older prototypes stay in the code, archived, not reachable):
//   default                   -> GOLDEN SERVE — RETURN SPINS, build RETURN-01
//   VITE_GAMEPLAY=duel        -> archived Championship Duel (DUEL-01)
//   VITE_GAMEPLAY=goldenserve -> archived Golden Serve A/B (GOLDEN-SERVE-02)
//   VITE_GAMEPLAY=rallypath   -> archived Rally Path (RALLY-PATH-01)
//   VITE_GAMEPLAY=finalset    -> archived v6 THE FINAL SET
const G = import.meta.env.VITE_GAMEPLAY ?? 'returnspins';
export const RETURN_SPINS_BUILD = G === 'returnspins';
export const DUEL_BUILD = G === 'duel';
export const GOLDEN_SERVE_BUILD = G === 'goldenserve';
export const RALLY_PATH_BUILD = G === 'rallypath';
export const FINAL_SET_BUILD = G === 'finalset';
export const BUILD_ID = RETURN_SPINS_BUILD ? 'RETURN-01' : DUEL_BUILD ? 'DUEL-01' : GOLDEN_SERVE_BUILD ? 'GOLDEN-SERVE-02' : RALLY_PATH_BUILD ? 'RALLY-PATH-01' : 'FINAL-SET-v6';
/** development tools (forced scenarios): test builds only; a player build sets VITE_DEV_TOOLS=0 */
export const DEV_TOOLS = import.meta.env.VITE_DEV_TOOLS !== '0';
/** storage namespace: a round of another gameplay can never be resumed here */
export const STORE_NS = RETURN_SPINS_BUILD ? 'rs01' : DUEL_BUILD ? 'duel01' : GOLDEN_SERVE_BUILD ? 'gs02' : RALLY_PATH_BUILD ? 'rp01' : 'v1';
