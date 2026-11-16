// Which bonus gameplay this build runs (older ones stay in the code, archived, not reachable):
//   default                   -> CHAMPIONSHIP DUEL prototype, build DUEL-01
//   VITE_GAMEPLAY=goldenserve -> archived Golden Serve prototypes (GOLDEN-SERVE-02)
//   VITE_GAMEPLAY=rallypath   -> archived Rally Path (RALLY-PATH-01)
//   VITE_GAMEPLAY=finalset    -> archived v6 THE FINAL SET
const G = import.meta.env.VITE_GAMEPLAY ?? 'duel';
export const DUEL_BUILD = G === 'duel';
export const GOLDEN_SERVE_BUILD = G === 'goldenserve';
export const RALLY_PATH_BUILD = G === 'rallypath';
export const FINAL_SET_BUILD = G === 'finalset';
export const BUILD_ID = DUEL_BUILD ? 'DUEL-01' : GOLDEN_SERVE_BUILD ? 'GOLDEN-SERVE-02' : RALLY_PATH_BUILD ? 'RALLY-PATH-01' : 'FINAL-SET-v6';
/** storage namespace: a round of another gameplay can never be resumed here */
export const STORE_NS = DUEL_BUILD ? 'duel01' : GOLDEN_SERVE_BUILD ? 'gs02' : RALLY_PATH_BUILD ? 'rp01' : 'v1';
