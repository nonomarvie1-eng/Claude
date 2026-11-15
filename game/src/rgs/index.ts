import { DemoRgs } from './demoRgs';
import { StakeRgs } from './stakeRgs';
import type { RgsClient } from './types';

/** Chooses the server.  Demo is the default and the only mode enabled in this
 *  build: the Stake client additionally requires VITE_ENABLE_RGS=1 at build time. */
export function createRgs(search: string = typeof location !== 'undefined' ? location.search : ''): RgsClient {
  const q = new URLSearchParams(search);
  const sessionID = q.get('sessionID');
  const rgsUrl = q.get('rgs_url');
  const enabled = import.meta.env?.VITE_ENABLE_RGS === '1';
  if (enabled && sessionID && rgsUrl) return new StakeRgs(rgsUrl, sessionID);
  return new DemoRgs();
}
