// Which bonus gameplay this build runs.
// Test build RALLY-PATH-01: the Rally Path game is the real game (spin button,
// bonus triggers, test buttons).  The v6 "THE FINAL SET" code is kept intact
// and can be rebuilt with VITE_GAMEPLAY=finalset; it is simply not reachable here.
export const RALLY_PATH_BUILD = import.meta.env.VITE_GAMEPLAY !== 'finalset';
export const BUILD_ID = RALLY_PATH_BUILD ? 'RALLY-PATH-01' : 'FINAL-SET-v6';
