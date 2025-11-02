import { writable } from 'svelte/store';

export type ViewType = 'chat' | 'documents' | 'settings' | 'analytics';

export const currentView = writable<ViewType>('chat');

