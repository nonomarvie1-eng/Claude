<script lang="ts">
  import { onMount } from 'svelte';
  import { game } from './game/state.svelte';
  import { Controller } from './game/controller';
  import { RallyScene, loadTextures } from './render/scene';
  import { audio } from './audio/audio';
  import { createRgs } from './rgs';
  import Hud from './ui/Hud.svelte';
  import Loading from './ui/Loading.svelte';
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

  onMount(async () => {
    try {
      const tex = await loadTextures((p) => (game.loadProgress = p * 0.9));
      await Promise.all([document.fonts.load('700 40px Cinzel'), document.fonts.load('500 20px Inter'), document.fonts.load('700 20px Inter'), document.fonts.load('800 20px Inter')]).catch(() => {});
      await scene.init(host, tex, game.t);
      // expose layout rectangles for automated layout checks (demo/QA only)
      scene.onLayout = (l) => ((window as unknown as { __rallyLayout: unknown }).__rallyLayout = l);
      scene.layout();
      scene.setIntro(true);
      applyPrefs();
      ctrl = new Controller(createRgs(), scene);
      // demo-only QA handle (simulate server errors in automated tests)
      if (ctrl.rgs.kind === 'demo') (window as unknown as { __rallyDemo: unknown }).__rallyDemo = ctrl.rgs;
      game.loadProgress = 1;
      game.phase = 'ready';
    } catch (e) {
      console.error(e);
      game.error = { message: game.t.genericError, retryable: false, fatal: true };
      game.phase = 'error';
    }
    // WebGL context loss (mobile background, GPU reset)
    host.addEventListener('webglcontextlost', () => {
      game.error = { message: game.t.genericError, retryable: false, fatal: true };
    }, true);
  });

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

  async function start() {
    if (!ctrl) return;
    await audio.unlock();
    audio.setMusic('music_base');
    audio.startLoop('ambience', 0.5);
    scene.setIntro(false);
    game.phase = 'spinning';
    try {
      await ctrl.boot();
      game.phase = 'idle';
      scene.welcome();
    } catch (e) {
      game.error = { message: game.t.networkError, retryable: true, fatal: false };
      game.phase = 'error';
    }
  }

  function onKey(e: KeyboardEvent) {
    if (e.code !== 'Space' || game.jurisdiction.disabledSpacebar) return;
    const el = e.target as HTMLElement;
    if (el && (el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA' || el.tagName === 'BUTTON')) return;
    e.preventDefault();
    if (game.phase === 'ready') void start();
    else if (game.autoplay) ctrl?.stopAutoplay();
    else void ctrl?.spin();
  }
</script>

<svelte:window onkeydown={onKey} />

<main class:portrait={false}>
  <div class="stage" bind:this={host}></div>

  {#if game.phase !== 'loading' && game.phase !== 'ready'}
    <Hud {ctrl} />
  {/if}

  {#if game.phase === 'loading' || game.phase === 'ready'}
    <Loading onstart={start} />
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
