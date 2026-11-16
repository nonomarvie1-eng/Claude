// Which bonus gameplay this build runs (the older ones stay in the code, not reachable):
//   default            -> GOLDEN SERVE prototypes (A Cross-Court / B Court Switch), build GOLDEN-SERVE-02
//   VITE_GAMEPLAY=rallypath -> Rally Path test build RALLY-PATH-01
//   VITE_GAMEPLAY=finalset  -> v6 THE FINAL SET
const G = import.meta.env.VITE_GAMEPLAY ?? 'goldenserve';
export const GOLDEN_SERVE_BUILD = G === 'goldenserve';
export const RALLY_PATH_BUILD = G === 'rallypath';
export const FINAL_SET_BUILD = G === 'finalset';
export const BUILD_ID = GOLDEN_SERVE_BUILD ? 'GOLDEN-SERVE-02' : RALLY_PATH_BUILD ? 'RALLY-PATH-01' : 'FINAL-SET-v6';
/** storage namespace: a round of another gameplay can never be resumed here */
export const STORE_NS = GOLDEN_SERVE_BUILD ? 'gs02' : RALLY_PATH_BUILD ? 'rp01' : 'v1';
