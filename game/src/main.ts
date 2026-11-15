import '@fontsource/luckiest-guy/400.css';
import '@fontsource/lilita-one/400.css';
import './ui/theme.css';
import { mount } from 'svelte';
import App from './App.svelte';

mount(App, { target: document.getElementById('app')! });
