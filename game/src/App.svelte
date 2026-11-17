<script lang="ts">
  import { onMount } from 'svelte';
  import { game } from './game/state.svelte';
  import { Controller } from './game/controller';
  import { RallyScene, loadTextures, introImages } from './render/scene';
  import { audio } from './audio/audio';
  import { createRgs } from './rgs';
  import Hud from './ui/Hud.svelte';
  import Intro from './ui/Intro.svelte';
  import { IntroScene } from './render/intro';
  import { STORE_NS } from './engine/gameplay';
  import { tick } from 'svelte';
  import Modal from './ui/Modal.svelte';
  import Paytable from './ui/Paytable.svelte';
  import Settings from './ui/Settings.svelte';
  import History from './ui/History.svelte';
  import BuyBonus from './ui/BuyBonus.svelte';
  import Autoplay from './ui/Autoplay.svelte';

  let host: HTMLDivElement;
  let ctrl: Controller | null = $state(null);
  const scene = new RallyScene();
  const t = $derived(game.t);

  // ---- THE FIRST SERVE: loading -> (first visit: feature card) -> transition -> reels
  let introHost: HTMLDivElement | undefined = $state();
  let intro: IntroScene | null = null;
  let showCard = $state(false);
  let entering = $state(false);
  let slow = $state(false);
  let failed = $state(false);
  const SEEN_KEY = `golden-rally-first-serve-seen-${STORE_NS}`;
  const seen = () => { try { return localStorage.getItem(SEEN_KEY) === '1'; } catch { return false; } };
  const markSeen = () => { try { localStorage.setItem(SEEN_KEY, '1'); } catch { /* private mode */ } };
  // real progress: intro images 15 %, game images 70 %, fonts 5 %, scene + session objects 10 %
  const progress = (p: number) => {
    game.loadProgress = Math.max(game.loadProgress, p);
    intro?.setProgress(game.loadProgress);
  };

  onMount(async () => {
    const slowTimer = setTimeout(() => (slow = true), 7000);
    try {
      await Promise.all([document.fonts.load('700 40px Cinzel'), document.fonts.load('600 20px Cinzel'), document.fonts.load('700 13px Inter'), document.fonts.load('500 20px Inter'), document.fonts.load('800 20px Inter')]).catch(() => {});
      const introTex = await loadTextures((p) => progress(0.15 * p), introImages(innerHeight > innerWidth * 1.05));
      intro = new IntroScene(introTex, { preparing: game.t.introPreparing, ready: game.t.introReady, subtitle: 'THE FIRST SERVE' });
      intro.reducedMotion = game.prefs.reducedMotion;
      await intro.init(introHost!);
      document.getElementById('preboot')?.remove();
      (window as unknown as { __rallyIntro: unknown }).__rallyIntro = intro;
      intro.setProgress(game.loadProgress);
      const tex = await loadTextures((p) => progress(0.15 + 0.7 * p), undefined, introTex);
      progress(0.9);
      await scene.init(host, tex, game.t);
      // expose layout rectangles for automated layout checks (demo/QA only)
      scene.onLayout = (l) => ((window as unknown as { __rallyLayout: unknown }).__rallyLayout = l);
      scene.layout();
      scene.setIntro(true);
      applyPrefs();
      ctrl = new Controller(createRgs(), scene);
      // demo-only QA handle (simulate server errors in automated tests)
      if (ctrl.rgs.kind === 'demo') (window as unknown as { __rallyDemo: unknown }).__rallyDemo = ctrl.rgs;
      progress(1);
      clearTimeout(slowTimer);
      slow = false;
      intro.addTextures(tex);
      // completion: ball at the end of the track, one small bounce, highlight, bar fades
      await intro.complete();
      game.phase = 'ready';
      if (seen()) void enter(false); // returning player: straight to the reels, no artificial delay
      else {
        intro.showFeatureCard(tex, { title: game.t.introFeatureKicker, name: 'GOLDEN SERVE · RETURN SPINS', text1: game.t.introFeature1, text2: game.t.introFeature2, zone: game.t.introZone });
        showCard = true;
      }
    } catch (e) {
      console.error(e);
      clearTimeout(slowTimer);
      document.getElementById('preboot')?.remove();
      failed = true;
    }
    // WebGL context loss (mobile background, GPU reset)
    host.addEventListener('webglcontextlost', () => {
      game.error = { message: game.t.genericError, retryable: false, fatal: true };
    }, true);
  });

  /** Sound only after a real user gesture (autoplay policies). */
  let audioStarted = false;
  async function startAudio() {
    if (audioStarted) return;
    audioStarted = true;
    await audio.unlock();
    audio.setMusic('music_base');
    audio.startLoop('ambience', 0.5);
  }
  function armAudioOnFirstGesture() {
    const go = () => {
      window.removeEventListener('pointerdown', go, true);
      window.removeEventListener('keydown', go, true);
      void startAudio();
    };
    window.addEventListener('pointerdown', go, true);
    window.addEventListener('keydown', go, true);
  }

  async function enter(fromGesture: boolean) {
    if (!ctrl || !intro || entering || game.phase !== 'ready') return;
    markSeen();
    if (fromGesture) void startAudio();
    else armAudioOnFirstGesture();
    entering = true;
    showCard = false;
    game.phase = 'spinning'; // the HUD mounts (hidden while entering) so the reels get their final layout
    await tick();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    scene.layout();
    const L = scene.layoutInfo;
    const target = L ? L.board : { x: 0, y: 0, w: 1, h: 1 };
    await intro.enter(target, () => scene.setIntro(false, game.prefs.reducedMotion ? 150 : 260));
    intro.destroy();
    intro = null;
    entering = false;
    try {
      await ctrl.boot(); // session, interrupted round resumed and closed if any
      game.phase = 'idle';
      scene.welcome();
    } catch (e) {
      game.error = { message: game.t.networkError, retryable: true, fatal: false };
      game.phase = 'error';
    }
  }

  function applyPrefs() {
    scene.prefs.reducedMotion = game.prefs.reducedMotion;
    scene.prefs.turbo = game.prefs.turbo && !game.jurisdiction.disabledTurbo;
    scene.lang = game.prefs.lang;
    scene.setStrings(game.t);
    document.documentElement.classList.toggle('rm', game.prefs.reducedMotion);
    audio.enabled = game.prefs.sound;
    audio.volumes = { master: game.prefs.master, music: game.prefs.music, sfx: game.prefs.sfx };
    audio.applyVolumes();
    game.savePrefs();
    document.documentElement.lang = game.prefs.lang;
  }

  $effect(() => {
    scene.setInsets({ ...game.insets });
  });

  $effect(() => {
    // re-apply whenever a preference changes
    JSON.stringify(game.prefs);
    applyPrefs();
  });


  function onKey(e: KeyboardEvent) {
    if (e.code !== 'Space' || game.jurisdiction.disabledSpacebar) return;
    const el = e.target as HTMLElement;
    if (el && (el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA' || el.tagName === 'BUTTON')) return;
    e.preventDefault();
    if (game.phase === 'ready') void enter(true);
    else if (game.autoplay) ctrl?.stopAutoplay();
    else void ctrl?.spin();
  }
</script>

<svelte:window onkeydown={onKey} />

<main class:portrait={false}>
  <div class="stage" bind:this={host}></div>

  {#if game.phase !== 'loading' && game.phase !== 'ready'}
    <div class="hudwrap" class:entering><Hud {ctrl} /></div>
  {/if}

  {#if game.phase === 'loading' || game.phase === 'ready' || entering || failed}
    <Intro bind:host={introHost} {showCard} {entering} {slow} {failed} oncontinue={() => enter(true)} onskiptransition={() => intro?.skipTransition()} />
  {/if}

  {#if game.notice}
    <div class="toast" role="status">{game.notice}</div>
  {/if}
  {#if game.banner}
    <div class="banner" role="status">{game.banner}</div>
  {/if}

  {#if game.modal === 'paytable'}
    <Modal title={t.paytable} onclose={() => (game.modal = null)}><Paytable /></Modal>
  {:else if game.modal === 'settings'}
    <Modal title={t.settings} onclose={() => (game.modal = null)}><Settings {ctrl} /></Modal>
  {:else if game.modal === 'history'}
    <Modal title={t.history} onclose={() => (game.modal = null)}><History {ctrl} /></Modal>
  {:else if game.modal === 'buy'}
    <Modal title={t.buyTitle} onclose={() => (game.modal = null)}><BuyBonus {ctrl} /></Modal>
  {:else if game.modal === 'auto'}
    <Modal title={t.autoTitle} onclose={() => (game.modal = null)}><Autoplay {ctrl} /></Modal>
  {/if}

  {#if game.error}
    <div class="error-veil" role="alertdialog" aria-modal="true" aria-labelledby="err-title">
      <div class="error-box">
        <h2 id="err-title">{t.errorTitle}</h2>
        <p>{game.error.message}</p>
        {#if game.error.retryable}
          <button class="btn" onclick={() => ctrl?.retry()}>{t.retry}</button>
        {:else}
          <button class="btn" onclick={() => location.reload()}>{t.retry}</button>
        {/if}
      </div>
    </div>
  {/if}
</main>

<style>
  main { position: fixed; inset: 0; overflow: hidden; }
  .stage { position: absolute; inset: 0; }
  .hudwrap { display: contents; }
  .hudwrap :global(.top), .hudwrap :global(.hud) { transition: opacity .25s ease-out; }
  .hudwrap.entering :global(.top), .hudwrap.entering :global(.hud) { opacity: 0; pointer-events: none; }
  .toast, .banner {
    position: absolute; left: 50%; transform: translateX(-50%); z-index: 30;
    padding: 10px 20px; border-radius: 999px; font-size: 14px; font-weight: 600; letter-spacing: .02em;
    background: rgba(8, 27, 35, .94); border: 1px solid var(--line); box-shadow: var(--shadow);
    max-width: calc(100vw - 32px); text-align: center;
  }
  .toast { top: 42%; }
  .banner { top: calc(64px + var(--safe-t)); font-size: 12px; padding: 6px 14px; color: var(--cream); border-color: var(--tennis); }
  .error-veil { position: absolute; inset: 0; z-index: 60; display: grid; place-items: center; background: rgba(4, 12, 16, .82); padding: 16px; }
  .error-box { max-width: 440px; background: var(--panel); border: 1px solid var(--gold); box-shadow: var(--shadow); border-radius: var(--radius); padding: 24px; text-align: center; }
  .error-box h2 { font-family: var(--font-title); color: var(--gold-hi); margin: 0 0 10px; font-size: 22px; }
  .error-box p { color: var(--ink); line-height: 1.5; }
  .btn { margin-top: 10px; min-height: 44px; padding: 12px 26px; border-radius: 999px; border: none; background: var(--gold-btn); color: var(--night); font-weight: 800; font-size: 15px; letter-spacing: .06em; }
</style>
