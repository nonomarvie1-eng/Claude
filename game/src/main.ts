import '@fontsource/cinzel/700.css';
import '@fontsource/marcellus/400.css';
import '@fontsource/poiret-one/400.css';
import './ui/theme.css';
import { mount } from 'svelte';
import App from './App.svelte';

mount(App, { target: document.getElementById('app')! });
