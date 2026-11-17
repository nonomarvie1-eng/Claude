// Optional external player clip for the ACE! opening (see src/assets/cinematic/README.md).
// Nothing is bundled while the files are absent: the globs are simply empty.
import type { ServeClip } from './aceCinematic';

const manifests = import.meta.glob('../assets/cinematic/serve.json', { eager: true, import: 'default' }) as Record<string, ServeClip>;
const videos = import.meta.glob('../assets/cinematic/*.mp4', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;

/** Loads the clip if it exists (dev QA can inject one with window.__aceClipOverride).
 *  Resolves to null if absent, not playable or too slow (the HTML5 version is played then). */
export async function loadServeClip(timeoutMs = 5000): Promise<{ clip: ServeClip; video: HTMLVideoElement } | null> {
  const override = import.meta.env.VITE_ENABLE_RGS === '1' ? undefined : (window as unknown as { __aceClipOverride?: { clip: ServeClip; url: string } }).__aceClipOverride;
  const clip = override?.clip ?? Object.values(manifests)[0];
  if (!clip) return null;
  const url = override?.url ?? Object.entries(videos).find(([k]) => k.endsWith('/' + clip.src))?.[1];
  if (!url) return null;
  const video = document.createElement('video');
  video.muted = true;
  video.playsInline = true;
  video.setAttribute('playsinline', '');
  video.preload = 'auto';
  video.crossOrigin = 'anonymous';
  video.src = url;
  const ok = await new Promise<boolean>((resolve) => {
    const t = setTimeout(() => resolve(false), timeoutMs);
    video.addEventListener('canplaythrough', () => { clearTimeout(t); resolve(true); }, { once: true });
    video.addEventListener('error', () => { clearTimeout(t); resolve(false); }, { once: true });
    video.load();
  });
  return ok ? { clip, video } : null;
}
