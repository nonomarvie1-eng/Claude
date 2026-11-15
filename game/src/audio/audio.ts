// WebAudio sound manager: separate master / music / effects volumes,
// suspended when the page is hidden (interruptions: calls, tab switch).
const files = import.meta.glob('../assets/audio/*.{mp3,wav}', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;

export type SoundName =
  | 'button' | 'reel_stop' | 'spin_start' | 'spin_loop' | 'scatter_1' | 'scatter_2' | 'scatter_3' | 'wild_land'
  | 'win_0' | 'win_1' | 'win_2' | 'win_3' | 'line_tick' | 'bonus_trigger' | 'wind' | 'mult_up' | 'count_tick'
  | 'bonus_end' | 'music_base' | 'music_free';

const urlOf = (n: string) => Object.entries(files).find(([k]) => k.endsWith(`/${n}.mp3`) || k.endsWith(`/${n}.wav`))?.[1];

/** Inline (single-file) builds embed sounds as data URLs: decode them without
 *  fetch(), which some sandboxed hosts forbid. */
function dataUrlToBuffer(url: string): ArrayBuffer {
  const b64 = url.slice(url.indexOf(',') + 1);
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out.buffer;
}

export class AudioManager {
  private ctx: AudioContext | null = null;
  private master!: GainNode;
  private musicBus!: GainNode;
  private sfxBus!: GainNode;
  private buffers = new Map<string, AudioBuffer>();
  private music: { name: string; src: AudioBufferSourceNode; gain: GainNode } | null = null;
  private loops = new Map<string, AudioBufferSourceNode>();
  volumes = { master: 0.8, music: 0.5, sfx: 0.9 };
  enabled = true;

  /** Must be called from a user gesture (mobile autoplay policies). */
  async unlock(): Promise<void> {
    if (this.ctx) {
      if (this.ctx.state === 'suspended') await this.ctx.resume().catch(() => {});
      return;
    }
    const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (!AC) return;
    this.ctx = new AC();
    this.master = this.ctx.createGain();
    this.musicBus = this.ctx.createGain();
    this.sfxBus = this.ctx.createGain();
    this.musicBus.connect(this.master);
    this.sfxBus.connect(this.master);
    this.master.connect(this.ctx.destination);
    this.applyVolumes();
    document.addEventListener('visibilitychange', () => {
      if (!this.ctx) return;
      if (document.hidden) this.ctx.suspend().catch(() => {});
      else this.ctx.resume().catch(() => {});
    });
    await this.loadAll();
  }

  private async loadAll() {
    const names = Object.keys(files).map((k) => k.split('/').pop()!.replace(/\.(mp3|wav)$/, ''));
    await Promise.all(
      names.map(async (n) => {
        try {
          const url = urlOf(n)!;
          const data = url.startsWith('data:') ? dataUrlToBuffer(url) : await (await fetch(url)).arrayBuffer();
          const buf = await this.ctx!.decodeAudioData(data);
          this.buffers.set(n, buf);
        } catch {
          /* missing sound must never block the game */
        }
      }),
    );
  }

  applyVolumes() {
    if (!this.ctx) return;
    const t = this.ctx.currentTime;
    this.master.gain.setTargetAtTime(this.enabled ? this.volumes.master : 0, t, 0.05);
    this.musicBus.gain.setTargetAtTime(this.volumes.music, t, 0.05);
    this.sfxBus.gain.setTargetAtTime(this.volumes.sfx, t, 0.05);
  }

  play(name: SoundName, opts: { volume?: number; rate?: number; delay?: number } = {}) {
    const buf = this.buffers.get(name);
    if (!this.ctx || !buf) return;
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    src.playbackRate.value = opts.rate ?? 1;
    const g = this.ctx.createGain();
    g.gain.value = opts.volume ?? 1;
    src.connect(g).connect(this.sfxBus);
    src.start(this.ctx.currentTime + (opts.delay ?? 0));
  }

  startLoop(name: SoundName, volume = 1) {
    const buf = this.buffers.get(name);
    if (!this.ctx || !buf || this.loops.has(name)) return;
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    src.loop = true;
    const g = this.ctx.createGain();
    g.gain.value = volume;
    src.connect(g).connect(this.sfxBus);
    src.start();
    this.loops.set(name, src);
  }

  stopLoop(name: SoundName) {
    const src = this.loops.get(name);
    if (src) {
      try {
        src.stop();
      } catch {
        /* already stopped */
      }
      this.loops.delete(name);
    }
  }

  setMusic(name: 'music_base' | 'music_free' | null) {
    if (!this.ctx) return;
    if (this.music?.name === name) return;
    const t = this.ctx.currentTime;
    if (this.music) {
      const old = this.music;
      old.gain.gain.setTargetAtTime(0, t, 0.4);
      setTimeout(() => {
        try {
          old.src.stop();
        } catch {
          /* noop */
        }
      }, 2500);
      this.music = null;
    }
    if (!name) return;
    const buf = this.buffers.get(name);
    if (!buf) return;
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    src.loop = true;
    const gain = this.ctx.createGain();
    gain.gain.value = 0;
    gain.gain.setTargetAtTime(1, t, 0.6);
    src.connect(gain).connect(this.musicBus);
    src.start();
    this.music = { name, src, gain };
  }
}

export const audio = new AudioManager();
